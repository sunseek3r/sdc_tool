import sys

import os
os.environ["QT_API"] = "pyqt5"

#імпортуємо всі необхідні бібліотеки
from random import randint
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QInputDialog,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from pyvistaqt import QtInteractor, MainWindow, BackgroundPlotter
import pyvista as pv
import numpy as np
from figure_classes import Figure, Surface, ArrowLabel, PointLabel, ConicSurface, CylindricSurface
from inputs import PointDialog, VectorLineDialog, ParameterDialog
from settings import Settings
from instruments import compute_points, compute_parameter, get_bounds, get_rotational_matrix
from scipy.spatial import cKDTree
import time


# Function to create and display the 3D plot


#Клас головного вікна програми
class Window(MainWindow):
    
    def __init__(self):
        # Створюємо вікно
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.temp_line = 0
        self.temp_vector_line = 0 
        self.temp_surface = 0 
        self.temp_curve = 0 
        self.temp_cylindric = 0 
        self.temp_conic = 0 
        self.temp_surface_of_revolution = 0
        self.settings = Settings() 
        #Задаємо назву та розміри вікна

        self.setWindowTitle("SDC Tool")
        self.setGeometry(50, 50, 800, 600)

        self.meshes = []
        
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        #Створюємо лівий віджет на якому розташовуються перелік введених користувачем примітивів та кнопки для їх додання
        left_widget = QWidget(main_widget)
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(300)
        main_layout.addWidget(left_widget)

        #Створюємо та додаємо до лівого віджета текстове поле
        self.text_box = QListWidget(self)
        self.text_box.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        left_layout.addWidget(self.text_box)

        #Створюємо головне меню програми
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        exitButton = QtWidgets.QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        #Додаємо до меню кнопку для знаходження перетину
        tools_menu = mainMenu.addMenu('Tools')
        intersect_button = QtWidgets.QAction('Intersection', self)
        intersect_button.triggered.connect(self.intersect)
        tools_menu.addAction(intersect_button)

        #Створюємо правий віджет на якому буде відображатись координатна площина
        right_widget = QWidget(main_widget)
        right_layout = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget)

        #Створюємо координатну площину та додаємо її до правого віджета
        self.plotter = BackgroundPlotter(show=False)
        right_layout.addWidget(self.plotter)

        #Додаємо тулбал для керування камерою
        self.addToolBar(self.plotter.default_camera_tool_bar)
        self.addToolBar(self.plotter.saved_cameras_tool_bar)

        #Додаємо меню та всі необхідні кнопки до нього
        self.setMenuBar(self.plotter.main_menu)
        mainMenu = self.menuBar()
        tools_menu = mainMenu.addMenu('Custom Tools')
        intersect_button = QtWidgets.QAction('Intersection', self)
        intersect_button.triggered.connect(self.intersect)
        tools_menu.addAction(intersect_button)
        
        delete_button = QtWidgets.QAction('Delete', self)
        delete_button.triggered.connect(self.delete_figures)
        tools_menu.addAction(delete_button)

        pick_button = QtWidgets.QAction('Select', self)
        pick_button.triggered.connect(self.pick_figure)
        tools_menu.addAction(pick_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови лінії за двома точками
        line_button = QPushButton("Line", self)
        line_button.clicked.connect(self.add_line)
        left_layout.addWidget(line_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови площини
        surface_button = QPushButton("Surface", self)
        surface_button.clicked.connect(self.add_surface)
        left_layout.addWidget(surface_button)
        

        #Створюємо та додаємо до лівого віджета кнопку для побудови параметричної кривої
        parameters_button = QPushButton("Curve by parameter", self)
        parameters_button.clicked.connect(self.add_curve_by_t)
        left_layout.addWidget(parameters_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови конічної поверхні
        conic_curve_button = QPushButton("Conic surface", self)
        conic_curve_button.clicked.connect(self.add_conic_surface)
        left_layout.addWidget(conic_curve_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови циліндричної поверхні
        cylindrical_curve_button = QPushButton("Cylindrical surface", self)
        cylindrical_curve_button.clicked.connect(self.add_cylindrical_surface)
        left_layout.addWidget(cylindrical_curve_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови поверхні обертання
        rotation_surface_button = QPushButton("Surface of revolution", self)
        rotation_surface_button.clicked.connect(self.add_surface_revolution)
        left_layout.addWidget(rotation_surface_button)

        self.plotter.show_grid()

        self.setCentralWidget(main_widget)
        self.show()

    #Функція, що повертає випадковий колір
    def get_color(self):
        return '#%06X' % randint(0, 0xFFFFFF)
    
    #Функція для зміни яркості кольору фігури
    def change_brightness(self,hex_color, brightness_offset=50):
        rgb_hex = [ hex_color[x : x + 2] for x in [1, 3, 5] ]
        
        if int(rgb_hex[0], 16) < brightness_offset and int(rgb_hex[1], 16) < brightness_offset and int(rgb_hex[2], 16) < brightness_offset:
            new_rgb_int = [ int(hex_value, 16) + 2 * brightness_offset for hex_value in rgb_hex ]
        else:
            new_rgb_int = [ int(hex_value, 16) - brightness_offset for hex_value in rgb_hex ]
            
        new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int]
        return "#" + "".join(['0' + hex(i)[2:] if len(hex(i)[2:]) < 2 else hex(i)[2:] for i in new_rgb_int])
    
    #Функція для побудови прямої за двома точками
    def add_line(self):
        self.temp_line += 1
        def _get_multiplier(directional_coor, anchor_coor, coor_type):
            if coor_type == "X":
                bounds = self.settings.x_bounds
            elif coor_type == "Y":
                bounds = self.settings.y_bounds
            elif coor_type == "Z":
                bounds = self.settings.z_bounds
            
            if directional_coor == 0:
                return 1e9 # cannot extend with this coordinate => return infinity

            if directional_coor < 0:
                return (bounds[0] - anchor_coor) / directional_coor
            else:
                return (bounds[1] - anchor_coor) / directional_coor

        #визиваємо діалогове вікно для вводу першої точки        
        dialog = PointDialog("Input point 1")
        point1 = []
        if dialog.exec():
            point1 = dialog.getInputs()
        
        #визиваємо діалогове вікно для вводу другої точки  
        dialog = PointDialog('Input point 2')
        point2 = []
        if dialog.exec():
            point2 = dialog.getInputs()


        if point1 == point2:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Beginning and end of the line can't be the same point")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            returnValue = msg.exec()
            if returnValue == QMessageBox.Ok:
                return
        #обчислюємо напрямний вектор для прямої  
        point1 = [float(i) for i in point1]
        point2 = [float(i) for i in point2]
        vector = [float(j - i) for i, j in zip(point1, point2)]

        #обчислюємо координати кінцевої точки прямої
        mult = min([_get_multiplier(vector[0], point1[0], "X"), _get_multiplier(vector[1], point1[1], "Y"), _get_multiplier(vector[2], point1[2], "Z")])
        vector = [i * mult for i in vector]
        end_point = [point_coor + vector_coor for point_coor, vector_coor in zip(point1, vector)]
    
        #обчислюємо координати початкової точки прямої
        mult = min([_get_multiplier(-vector[0], point1[0], "X"), _get_multiplier(-vector[1], point1[1], "Y"), _get_multiplier(-vector[2], point1[2], "Z")])
        vector = [i * mult for i in vector]
        start_point = [point_coor - vector_coor for point_coor, vector_coor in zip(point1, vector)]

        midlle_point = [point2_coor - point1_coor for point1_coor, point2_coor in zip(start_point, end_point)]

        #будуємо лінію
        line = pv.Line(start_point, end_point)
        color = self.get_color()
        self.plotter.add_mesh(line, color = color, line_width=5)
        middle_point = [(point2_coor + point1_coor)/2 for point1_coor, point2_coor in zip(start_point, end_point)]
        self.plotter.add_mesh(line, color = color, line_width=5, label = "Line")
        #Додаємо підписи
        label = ["Line " + str(self.temp_line)]
        self.plotter.add_point_labels(middle_point,label,italic=True,font_size=10,point_color='black',point_size=1,render_points_as_spheres=True,always_visible=True,shadow=True)
        self.meshes.append(Figure(line, 'line', labels=[PointLabel([label], middle_point)], color = color))
        self.text_box.addItem(QListWidgetItem(f"Line: {point1}, {point2}"))
        self.plotter.reset_camera()


    #Функція для побудови площини
    def add_surface(self):
        self.temp_surface += 1

        #визиваємо діалогове вікно для вводу точки
        dialog = PointDialog("Input point C")
        point_c = []
        if dialog.exec():
            point_c = [float(i) for i in dialog.getInputs()]

        #визиваємо діалогове вікно для вводу вектора-нормалі
        dialog = PointDialog("Input vector N")
        vector_n = []
        if dialog.exec():
            vector_n = [float(i) for i in dialog.getInputs()]
            


        if len(point_c) != 3 or len(vector_n) != 3:
            return
              
        #обчислюємо параметри для повного рівняння площини
        A = vector_n[0]
        B = vector_n[1]
        C = vector_n[2]
        D = -(point_c[0] * A + point_c[1] * B + point_c[2] * C)

        #обчислюємо координати точок площини по x та y
        x = np.arange(self.settings.x_bounds[0], self.settings.x_bounds[1], 0.3)
        y = np.arange(self.settings.y_bounds[0], self.settings.y_bounds[1], 0.3)
        z = np.arange(self.settings.z_bounds[0], self.settings.z_bounds[1], 0.3)
        #обчислюємо координати точок площини по z
        if C != 0:
            x, y = np.meshgrid(x, y)
            #x = x.reshape(-1)
            #y = y.reshape(-1)
            z = -(A * x + B * y + D) / C
        elif B != 0:
            x, z = np.meshgrid(x, z)
            y = -(A * x + C * z + D) / B
        elif A != 0:
            y, z = np.meshgrid(y, z)
            x = -(B * y + C * z + D) / A
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Wrong norm vector")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            returnValue = msg.exec()
            if returnValue == QMessageBox.Ok:
                return
        grid = pv.StructuredGrid(x, y, z)
        color = self.get_color()

        #відображаємо побудовану площину на графіку та запускаємо анімацію
        self.plotter.add_mesh(grid, opacity=0.7, color=color)
        self.animate(grid.points, step=10000)

        label = ["Surface " + str(self.temp_surface)]

        #label = ["Line " + str(self.temp_surface)]

        #додаємо підписи
        self.plotter.add_point_labels(point_c,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
        arrow = pv.Arrow(point_c, vector_n, scale = 'auto')
        self.plotter.add_mesh(arrow, color='blue')
        self.meshes.append(Surface(A, B, C, D, grid, labels=[ArrowLabel(arrow), PointLabel(label, point_c)], color = color))
        self.text_box.addItem(QListWidgetItem("surface"))
        self.plotter.reset_camera()

    #Функція для побудови параметричної кривої
    def add_curve_by_t(self):
        self.temp_curve += 1

        #визиваємо діалогове вікно для вводу функції
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()

            #обчислюємо точки кривої, якщо це зробити неможливо виводимо повідомлення про неправильні вхідні дані
            try:
                x, y, z = compute_parameter(functions)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                returnValue = msg.exec()
                if returnValue == QMessageBox.Ok:
                    return
            #будуємо та відображаємо криву
            grid = pv.StructuredGrid(x, y, z)
            color = self.get_color()
            self.plotter.add_mesh(grid, color=color, line_width=5,)
            #додаємо підписи
            array = [x[0],y[0],z[0]]
            label = ["Curve " + str(self.temp_curve)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.meshes.append(Figure(grid, 'curve', labels=[PointLabel(label, array)],color = color))
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()

    #Функція для побудови конічної поверхні
    def add_conic_surface(self):
        self.temp_conic += 1
        
        #визиваємо діалогове вікно для вводу точки
        dialog = PointDialog("Input point 0")
        point_0 = []
        if dialog.exec():
            point_0 = dialog.getInputs()

        #визиваємо діалогове вікно для вводу функцій
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()
            #обчислюємо точки кривої, якщо це зробити неможливо виводимо повідомлення про неправильні вхідні дані
            try:
                curve_x, curve_y, curve_z = compute_parameter(functions)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                returnValue = msg.exec()
                if returnValue == QMessageBox.Ok:
                    return

            x = np.array([])
            y = np.array([])
            z = np.array([])
            r_values = np.arange(-10, 10, 0.1)
            x_inst = curve_x - point_0[0]
            y_inst = curve_y - point_0[1]
            z_inst = curve_z - point_0[2]
            #обчислюємо точки поверхні
            for r in r_values:
                x = np.append(x, point_0[0] + r * (x_inst))
                y = np.append(y, point_0[1] + r * (y_inst))
                z = np.append(z, point_0[2] + r * (z_inst))

            if x.size * y.size * z.size == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Some error occured, try again")
                return
            
            #створюємо масив граней фігури
            faces = []
            curve_size = len(x_inst)
            for i in range(len(r_values)-1):
                for j in range(curve_size-1):
                    faces.append(4)
                    faces.append(i*curve_size+j)
                    faces.append(i*curve_size+(j+1))
                    faces.append((i+1)*curve_size+j)
                    faces.append((i+1)*curve_size+(j+1))

            #відображаємо напрямну
            guide = pv.StructuredGrid(curve_x, curve_y, curve_z)
            self.plotter.add_mesh(guide, color='green', line_width=9)

            #будуємо та відображаємо поверхню
            grid = pv.PolyData(list(zip(x,y,z)), faces=faces)
            color = self.get_color()
            self.plotter.add_mesh(grid, color=color, line_width=5, opacity=0.5)

            #будуємо та відображаємо твірну
            start_point = [point_0[0] + 10 * (curve_x[0] - point_0[0]), point_0[1] + 10 * (curve_y[0] - point_0[1]), point_0[2] + 10 * (curve_z[0] - point_0[2])]
            end_point = [point_0[0] - 10 * (curve_x[0] - point_0[0]), point_0[1] - 10 * (curve_y[0] - point_0[1]), point_0[2] - 10 * (curve_z[0] - point_0[2])]
            line = pv.Line(start_point, end_point)
            self.plotter.add_mesh(line, color='red', line_width=7)
            mid_point = [point_0[0] + 5 * (curve_x[0] - point_0[0]), point_0[1] + 5 * (curve_y[0] - point_0[1]), point_0[2] + 5 * (curve_z[0] - point_0[2])]
            # Create an array with the midpoint coordinates
            mid_point_array = np.array(mid_point)

            #запускаємо анімацію
            self.animate(grid.points)
            
            array = np.array(
                [[curve_x[0],curve_y[0],curve_z[0]],[curve_x[len(curve_x)//2],curve_y[len(curve_y)//2],curve_z[len(curve_z)//2]]])
            # Create an array with the midpoint coordinates
            

            # Vertically stack the midpoint array with the existing array
            array = np.vstack((point_0,array,mid_point_array))
         
            #додаємо підписи
            label = ["point c " + str(self.temp_cylindric),"point p " + str(self.temp_conic),"guide curve " + str(self.temp_conic),"creative line " + str(self.temp_conic)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))

            self.meshes.append(ConicSurface(grid, [PointLabel(label, array), ArrowLabel(line, 'red'), ArrowLabel(guide, 'green')], 
                                            curve_x, curve_y, curve_z, point_0,color = color))

            self.plotter.reset_camera()

    #Функція для побудови циліндричної поверхні
    def add_cylindrical_surface(self):
        self.temp_cylindric += 1

        #визиваємо діалогове вікно для вводу напрямного вектора
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        point_0 = [float(i) for i in vector]

        #визиваємо діалогове вікно для вводу функцій
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()
            #обчислюємо точки кривої, якщо це зробити неможливо виводимо повідомлення про неправильні вхідні дані
            try:
                curve_x, curve_y, curve_z = compute_parameter(functions)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                msg.setWindowTitle("Error")
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                returnValue = msg.exec()
                if returnValue == QMessageBox.Ok:
                    return
            first_dot = np.array([curve_x[0], curve_y[0], curve_z[0]])

            #відображаємо напрямну
            guide = pv.StructuredGrid(curve_x, curve_y, curve_z)
            self.plotter.add_mesh(guide, color='green', line_width=9)

            #перевіряємо що вектор ненульовий
            if np.isclose(np.linalg.norm(point_0), 0):
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Length of vector can't be zero")
            x = np.array([])
            y = np.array([])
            z = np.array([])

            r_values = np.arange(-10, 10, 0.1)
            #обчислюємо точки поверхні
            for r in r_values:
                x = np.append(x, point_0[0]*r + curve_x)
                y = np.append(y, point_0[1]*r + curve_y)
                z = np.append(z, point_0[2]*r + curve_z)

            #створюємо масив граней фігури
            faces = []
            curve_size = len(curve_x)
            for i in range(len(r_values)-1):
                for j in range(curve_size-1):
                    faces.append(4)
                    faces.append(i*curve_size+j)
                    faces.append(i*curve_size+(j+1))
                    faces.append((i+1)*curve_size+j)
                    faces.append((i+1)*curve_size+(j+1))

            #будуємо та відображаємо поверхню
            grid = pv.PolyData(list(zip(x, y, z)), faces = faces)
            color = self.get_color()
            self.plotter.add_mesh(grid, color=color, line_width=5, opacity=0.5)

            #будуємо та відображаємо твірну
            start_point = [curve_x[0] + 10 * point_0[0], curve_y[0] + 10 * point_0[1], curve_z[0] + 10 * point_0[2]]
            end_point = [curve_x[0] - 10 * point_0[0], curve_y[0] - 10 * point_0[1], curve_z[0] - 10 * point_0[2]]
            line = pv.Line(start_point, end_point)
            self.plotter.add_mesh(line, color='red', line_width=7)
            mid_point = [curve_x[0] + 5 * point_0[0], curve_y[0] + 5 * point_0[1], curve_z[0] + 5 * point_0[2]]
            array = np.array(
                [[curve_x[0],curve_y[0],curve_z[0]],[curve_x[len(curve_x)//2],curve_y[len(curve_y)//2],curve_z[len(curve_z)//2]]])
            # Create an array with the midpoint coordinates
            mid_point_array = np.array(mid_point)

            #запускаємо анімацію
            self.animate(grid.points)

            #додаємо підписи
            array = np.vstack((array,mid_point_array))
            arrow = pv.Arrow(first_dot, vector, scale = 'auto')
            self.plotter.add_mesh(arrow, color='blue')
            label = ["point p " + str(self.temp_cylindric),"guide curve " + str(self.temp_cylindric),"creative line " + str(self.temp_cylindric)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)

            
            self.meshes.append(CylindricSurface(grid, [ArrowLabel(arrow),PointLabel(label, array), ArrowLabel(line, 'red'), ArrowLabel(guide, 'green')], 
                                                curve_x, curve_y, curve_z, point_0, color = color))


            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()
    
    #Функція для побудови перетину площини та іншого примітиву
    def intersect(self):
        #отримуємо дані про пимітиви перетин яких треба знайти
        items = self.text_box.selectedIndexes()

        indexes = [i.row() for i in items]
        
        selected_meshes = [val for ind,val in enumerate(self.meshes) if ind in indexes]

        if (len(selected_meshes) != 2):
            return

        grid_1 = selected_meshes[0]
        grid_2 = selected_meshes[1]
        
        if (grid_2.fig_type == 'Surface'):
            grid_1, grid_2 = grid_2, grid_1

        A = grid_1.A
        B = grid_1.B
        C = grid_1.C
        D = grid_1.D
        
        print(grid_2.fig_type)
        if grid_2.fig_type == 'Conic Surface':
            #обчислюємо параметри необхідні для перерізу
            denominator = A*(grid_2.curve_x - grid_2.point_0[0]) + B*(grid_2.curve_y - grid_2.point_0[1]) + C*(grid_2.curve_z - grid_2.point_0[2])
            numerator = A*grid_2.point_0[0] + B*grid_2.point_0[1] + C*grid_2.point_0[2] + D
            p = -numerator / denominator

            #обчислюємо точки перетину
            x = p*(grid_2.curve_x - grid_2.point_0[0]) + grid_2.point_0[0]
            y = p*(grid_2.curve_y - grid_2.point_0[1]) + grid_2.point_0[1]
            z = p*(grid_2.curve_z - grid_2.point_0[2]) + grid_2.point_0[2]

            #будуємо та відображаємо перетин
            intersection = pv.PolyData(list(zip(x, y, z)))
            if intersection.points.size == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("No intersection found")
            self.plotter.add_mesh(intersection, color='white', line_width=10)
            self.meshes.append(Figure(intersection, 'Intersection', labels=[], color = "white"))
            self.text_box.addItem(QListWidgetItem("Intersection"))

        
        if grid_2.fig_type == 'Cylindrical Surface':
            #обчислюємо параметри необхідні для перерізу
            denominator = A*grid_2.point_0[0] + B*grid_2.point_0[1] + C*grid_2.point_0[2]

            #перевіряємо на часний випадок
            if np.isclose(denominator, 0):
                if np.isclose(A*grid_2.curve_x[0] + B*grid_2.curve_y[0] + C*grid_2.curve_z[0] + D, 0):
                    overlap_points = grid_2.mesh.points
                    intersection = pv.PolyData(overlap_points)
                    #будуємо переріз
                    self.plotter.add_mesh(intersection, color='white', line_width=10)
                    self.meshes.append(Figure(intersection, 'Intersection', labels=[], color = "white"))
                    self.text_box.addItem(QListWidgetItem("Intersection"))
                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("No intersection found")
            else:
                #обчислюємо точки перетину
                k = A * grid_2.curve_x + B * grid_2.curve_y + C*grid_2.curve_z + D
                k = -k / denominator
                x = grid_2.point_0[0] * k + grid_2.curve_x
                y = grid_2.point_0[1] * k + grid_2.curve_y
                z = grid_2.point_0[2] * k + grid_2.curve_z
                #будуємо переріз
                intersection = pv.PolyData(list(zip(x, y, z)))
                self.plotter.add_mesh(intersection, color='white', line_width=10)
                self.meshes.append(Figure(intersection, 'Intersection', labels=[], color = "white"))
                self.text_box.addItem(QListWidgetItem("Intersection"))


        if grid_2.fig_type == 'Surface of revolution':
            #Проходимо циклом по всім точкам присітиву та перевіряємо чи належать вони площині
            points = grid_2.mesh.points
            overlap_points = []
            delta = 1e-1
            for point in points:
                if np.abs(A*point[0] + B*point[1] + C*point[2] + D) < delta:
                    overlap_points.append(point)
            if len(overlap_points) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("No intersection found")
                return
            #Відображаємо знайдений перетин
            intersection = pv.PolyData(overlap_points)
            
            self.plotter.add_mesh(intersection, color='white', line_width=10)
            self.meshes.append(Figure(intersection, 'Intersection', labels=[], color = "white"))
            self.text_box.addItem(QListWidgetItem("Intersection"))

    def delete_figures(self):
        #отримуємо перелік обраних фігур
        items = self.text_box.selectedIndexes()
        indexes = [i.row() for i in items]

        #видаляємо обрані фігури
        for i in reversed(sorted(indexes)):
            self.text_box.takeItem(i)
        self.meshes = [i for j, i in enumerate(self.meshes) if j not in indexes]

        #очищуємо графік
        self.plotter.clear()
        self.plotter.show_grid()
        self.plotter.enable_lightkit()
        
        #перебудовуємо усі примітиви що залишилися

        for i in self.meshes:
            match i.fig_type:
                case 'line':
                    self.plotter.add_mesh(i.mesh, color=i.color, line_width=5)
                case 'Surface':
                    self.plotter.add_mesh(i.mesh, color=i.color, opacity=0.7)
                case 'curve':
                    self.plotter.add_mesh(i.mesh, color=i.color, line_width=5)
                case 'Conic Surface':
                    self.plotter.add_mesh(i.mesh, color=i.color, line_width=5, opacity=0.5)
                case 'Cylindrical Surface':
                    self.plotter.add_mesh(i.mesh, color=i.color, line_width=5, opacity=0.5)
                case 'Intersection':
                    self.plotter.add_mesh(i.mesh, color='white', line_width=10)
                case 'Surface of revolution':
                    self.plotter.add_mesh(i.mesh, color=i.color, opacity=0.25)
            print(len(i.labels))
            for j in i.labels:
                if isinstance(j, PointLabel):
                    self.plotter.add_point_labels(j.array, j.label, italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
                else:
                    if j.color=='red':
                        self.plotter.add_mesh(j.arrow, color=j.color, line_width=7)
                    elif j.color=='green':
                        self.plotter.add_mesh(j.arrow, color=j.color, line_width=9)
                    else:
                        self.plotter.add_mesh(j.arrow, color=j.color)

    #Функція для побудови поверхні обертання
    def add_surface_revolution(self):
        
        self.temp_surface_of_revolution += 1
        def _get_multiplier(dir, coord, bound, t):
            if dir == 0:
                return t # cannot extend with this coordinate => return infinity
            return (bound-coord)/dir
            

        #визиваємо діалогові вікна для вводу даних про вісь обертання
        dialog1 = PointDialog("Input point 0")
        dialog2 = VectorLineDialog()
        point_0 = []
        vector_n = []
        if dialog1.exec():
            point_0 = dialog1.getInputs()
        if dialog2.exec():
            vector_n = dialog2.getInputs()

        vector_n = vector_n / np.linalg.norm(vector_n)

        #визиваємо діалогові вікна для вводу кривої
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            #обчислюємо точки кривої
            functions = dialog.getInputs()
            try:
                x_g, y_g, z_g = compute_parameter(functions)
            except Exception as e:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText(str(e))
                return

            #будуємо твірну
            guide = pv.StructuredGrid(x_g, y_g, z_g)
            color = self.get_color()
            self.plotter.add_mesh(guide, color='green', line_width=9)

            arrow = pv.Arrow(point_0, vector_n, scale = 'auto')

            #обчмслюємо точки поверхні
            points = []
            for theta in range(360):
                #будуємо матрицю поворота на кут theta
                R = get_rotational_matrix(theta, vector_n)

                #обчислюємо точки кривої оберненої на кут theta
                for x, y, z in zip(x_g, y_g, z_g):
                    points.append(np.dot(R, np.array([x-point_0[0], y - point_0[1], z - point_0[2]])) + np.array(point_0))
            
            x, y, z = zip(*points)
            x = np.array(x)
            y = np.array(y)
            z = np.array(z)
           
            #створюємо масив граней фігури
            faces = []
            curve_size = len(x_g)
            for i in range(359):
                for j in range(curve_size-1):
                    faces.append(4)
                    faces.append(i*curve_size+j)
                    faces.append(i*curve_size+(j+1))
                    faces.append((i+1)*curve_size+j)
                    faces.append((i+1)*curve_size+(j+1))

            #будуємо та відображаємо поверхню
            self.animate(points)

            surface = pv.PolyData(points, faces)

            color = self.get_color()
            self.plotter.add_mesh(surface, color=color, opacity=0.25)
            
            array = np.array(
                [[x[0],y[0],z[0]],[x_g[0],y_g[0],z_g[0]], [x_g[len(x_g)//2],y_g[len(y_g)//2],z_g[len(z_g)//2]],
                 [x[-1],y[-1],z[-1]]]
                )
         
            label = ["point c " +  str(self.temp_surface_of_revolution), "point p " + str(self.temp_surface_of_revolution),"guide curve " + str(self.temp_surface_of_revolution),"creative line " + str(self.temp_surface_of_revolution)]
            


            #обчислюємо напрямний вектор для прямої  
            point_0 = [float(i) for i in point_0]
            vector = [float(i) for i in vector_n]

            bounds = self.plotter.bounds
            bounds = list(bounds)
            bounds[0] = min(bounds[0],point_0[0])
            bounds[1] = max(bounds[1],point_0[0])
            bounds[2] = min(bounds[2],point_0[1])
            bounds[3] = max(bounds[3],point_0[1])
            bounds[4] = min(bounds[4],point_0[2])
            bounds[5] = max(bounds[5],point_0[2])

            #обчислюємо координати кінцевої точки прямої
            mult = max([_get_multiplier(vector[0], point_0[0], bounds[0], -1e9), _get_multiplier(vector[1], point_0[1], bounds[2], -1e9), _get_multiplier(vector[2], point_0[2], bounds[4], -1e9)])
            end_point = [point_coor + vector_coor * mult for point_coor, vector_coor in zip(point_0, vector)]
        
            #обчислюємо координати початкової точки прямої
            mult = min([_get_multiplier(vector[0], point_0[0], bounds[1], 1e9), _get_multiplier(vector[1], point_0[1], bounds[3], 1e9), _get_multiplier(vector[2], point_0[2], bounds[5], 1e9)])
            start_point = [point_coor + vector_coor * mult for point_coor, vector_coor in zip(point_0, vector)]

            #будуємо вісь обертання
            line = pv.Line(start_point, end_point)
            self.plotter.add_mesh(line, color='red', line_width=5)
            mid_point = [(start + end) / 2 for start, end in zip(start_point, end_point)]
            array = np.array(
                [ [x_g[len(x_g)//2],y_g[len(y_g)//2],z_g[len(z_g)//2]]])
            mid_point_array = np.array(mid_point)

            #додаємо підписи
            array = np.vstack((point_0, array, mid_point_array))
            self.plotter.add_mesh(arrow, color='blue')
            label = ["point c " +  str(self.temp_surface_of_revolution), "guide curve " + str(self.temp_surface_of_revolution),"creative line " + str(self.temp_surface_of_revolution)]
            self.meshes.append(Figure(surface, 'Surface of revolution', labels=[PointLabel(label, array), ArrowLabel(line, 'red'), ArrowLabel(guide, 'green')], color=color))
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))

    #Функція для анімації
    def animate(self, points, step=1000):
        try:

            animation_plotter = BackgroundPlotter()
            for i in range(step, len(points) - step, step):
                grid = pv.PolyData(points[(i-step):i])
                animation_plotter.add_mesh(grid)

        except Exception as e:
            return

    #Функція для виділення фігур
    def pick_figure(self):
        #отримуємо перелік обраних фігур        
        items = self.text_box.selectedIndexes()
        indexes = [i.row() for i in items]
        
        #очищуємо графік
        self.plotter.clear()
        self.plotter.show_grid()
        self.plotter.enable_lightkit()

        #перебудовуємо усі примітиви, обрані примітиви робимо більш ярким кольором
        for i, figure in enumerate(self.meshes):
            if i in indexes:
                match figure.fig_type:
                    case 'line':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), line_width=5)
                    case 'Surface':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), opacity=0.95)
                    case 'curve':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), line_width=10)
                    case 'Conic Surface':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), line_width=5, opacity=0.9)
                    case 'Cylindrical Surface':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), line_width=5, opacity=0.9)
                    case 'Intersection':
                        self.plotter.add_mesh(figure.mesh, color='white', point_size=10)
                    case 'Surface of revolution':
                        self.plotter.add_mesh(figure.mesh, color=self.change_brightness(figure.color), opacity=0.9)
            else:
                match figure.fig_type:
                    case 'line':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, line_width=5)
                    case 'Surface':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, opacity=0.7)
                    case 'curve':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, line_width=5)
                    case 'Conic Surface':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, line_width=5, opacity=0.25)
                    case 'Cylindrical Surface':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, line_width=5, opacity=0.25)
                    case 'Intersection':
                        self.plotter.add_mesh(figure.mesh, color='white', point_size=10)
                    case 'Surface of revolution':
                        self.plotter.add_mesh(figure.mesh, color=figure.color, opacity=0.25)
            #print(len(i.labels))
            for j in figure.labels:
                if isinstance(j, PointLabel):
                    self.plotter.add_point_labels(j.array, j.label, italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
                else:
                    self.plotter.add_mesh(j.arrow, color='blue')






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())