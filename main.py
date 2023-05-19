import sys

import os
os.environ["QT_API"] = "pyqt5"

#імпортуємо всі необхідні бібліотеки

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QListWidgetItem, QListWidget, QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QInputDialog,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from pyvistaqt import QtInteractor, MainWindow, BackgroundPlotter
import pyvista as pv
import numpy as np
from figure_classes import Figure, Line, Surface
from inputs import SphereDialog, PointDialog, FunctionDialog, VectorLineDialog, ParameterDialog
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

        self.setMenuBar(self.plotter.main_menu)
        mainMenu = self.menuBar()
        tools_menu = mainMenu.addMenu('Custom Tools')
        intersect_button = QtWidgets.QAction('Intersection', self)
        intersect_button.triggered.connect(self.intersect)
        tools_menu.addAction(intersect_button)
        
        delete_button = QtWidgets.QAction('Delete', self)
        delete_button.triggered.connect(self.delete_figures)
        tools_menu.addAction(delete_button)

        
        #Створюємо та додаємо до лівого віджета кнопку для побудови сфери
        sphere_button = QPushButton("Sphere", self)
        sphere_button.clicked.connect(self.add_sphere)
        left_layout.addWidget(sphere_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови лінії за двома точками
        line_button = QPushButton("Line", self)
        line_button.clicked.connect(self.add_line)
        left_layout.addWidget(line_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови площини
        surface_button = QPushButton("Surface", self)
        surface_button.clicked.connect(self.add_surface)
        left_layout.addWidget(surface_button)
        
        #Створюємо та додаємо до лівого віджета кнопку для побудови точкою та вектором
        line_by_vector_button = QPushButton("Line by vector", self)
        line_by_vector_button.clicked.connect(self.add_vector_line)
        left_layout.addWidget(line_by_vector_button)

        #Створюємо та додаємо до лівого віджета кнопку для побудови кривої
        curve_button = QPushButton("Curve", self)
        curve_button.clicked.connect(self.add_curve)
        left_layout.addWidget(curve_button)

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

        self.plotter.add_mesh(line, color='black', line_width=5)
        midlle_point = [(point2_coor + point1_coor)/2 for point1_coor, point2_coor in zip(start_point, end_point)]
        self.plotter.add_mesh(line, color='black', line_width=5, label = "Line")
        label = ["Line " + str(self.temp_line)]
        self.plotter.add_point_labels(midlle_point,label,italic=True,font_size=10,point_color='black',point_size=1,render_points_as_spheres=True,always_visible=True,shadow=True)
        self.meshes.append(Figure(line, 'line'))
        self.text_box.addItem(QListWidgetItem(f"Line: {point1}, {point2}"))
        self.plotter.reset_camera()

    #Функція для побудови прямої за точкою та вектором
    def add_vector_line(self):
        self.temp_vector_line += 1
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

        #визиваємо діалогове вікно для вводу точки     
        dialog = PointDialog("Input point 0")
        point0 = []
        if dialog.exec():
            point0 = dialog.getInputs()
        
        #визиваємо діалогове вікно для вводу напрямного вектора 
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        point0 = [float(i) for i in point0]
        vector = [float(i) for i in vector]

        #обчислюємо координати кінцевої точки прямої
        mult = min([_get_multiplier(vector[0], point0[0], "X"), _get_multiplier(vector[1], point0[1], "Y"), _get_multiplier(vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        end_point = [point_coor + vector_coor for point_coor, vector_coor in zip(point0, vector)]
    
        #обчислюємо координати початкової точки прямої
        mult = min([_get_multiplier(-vector[0], point0[0], "X"), _get_multiplier(-vector[1], point0[1], "Y"), _get_multiplier(-vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        start_point = [point_coor - vector_coor for point_coor, vector_coor in zip(point0, vector)]

        #будуємо лінію
        midlle_point = [(point2_coor + point1_coor)/2 for point1_coor, point2_coor in zip(start_point, end_point)]
        label = ["Line by vector " + str(self.temp_vector_line)]
        line = pv.Line(start_point, end_point)

        #відображаємо побудовану лінію на графіку та додаємо її до віджету з переліком примітивів
        self.plotter.add_mesh(line, color='black', line_width=5)
        self.plotter.add_point_labels(midlle_point,label,italic=True,font_size=10,point_color='black',point_size=1,render_points_as_spheres=True,always_visible=True,shadow=True)
        self.meshes.append(Figure(line, 'line'))
        self.text_box.addItem(QListWidgetItem(f"Line by vector: {point0}, {vector}"))
        self.plotter.reset_camera()

    def add_sphere(self):
        dialog = SphereDialog()
        centre = []
        if dialog.exec():
            centre = dialog.getInputs()
        if centre is None or len(centre) != 3:
            return
        centre = [float(i) for i in centre]
        radius, ok = QInputDialog.getDouble(self, "Input", "Radius")
        print(radius)
        if ok and radius != 0:
            sphere = pv.Sphere(radius, centre)
            self.plotter.add_mesh(sphere, opacity=0.5, show_edges=False)
            self.meshes.append(Figure(sphere, 'sphere'))
            self.text_box.addItem(QListWidgetItem(f"Sphere: centre:{centre}, radius:{radius}"))
            self.plotter.reset_camera()
            self.settings.update_bounds(sphere.bounds)

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

        #обчислюємо координати точок площини по z
        x, y = np.meshgrid(x, y)
        z = -(A * x + B * y + D) / C

        #будуємо площину
        grid = pv.StructuredGrid(x, y, z)

        #відображаємо побудовану площину на графіку та додаємо її до віджету з переліком примітивів
        self.plotter.add_mesh(grid, opacity=0.7, color='red')
        self.animate(grid.points, step=10000)

        label = ["Surface " + str(self.temp_surface)]

        label = ["Line " + str(self.temp_surface)]

        self.meshes.append(Surface(A, B, C, D, grid))
        self.plotter.add_point_labels(point_c,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
        arrow = pv.Arrow(point_c, vector_n, scale = 'auto')
        self.plotter.add_mesh(arrow, color='blue')
        self.text_box.addItem(QListWidgetItem("surface"))
        self.plotter.reset_camera()

    #Функція для побудови кривої
    def add_curve(self):

        self.temp_curve += 1


        #визиваємо діалогове вікно для вводу функції
        dialog = FunctionDialog("Input a function in form i.e. \"f(z)=2*x + 3*y\"")
        func = ""
        if dialog.exec():
            func = dialog.getInputs()

        print(func)

        #будуємо та відображаємо криву
        if func != "":
            x, y, z = compute_points(func, self.settings.x_bounds, self.settings.y_bounds)
            print(type(x), type(y), type(z))
            grid = pv.StructuredGrid(x, y, z)
          
           
            self.plotter.add_mesh(grid, color='blue', line_width=5)
            
            self.meshes.append(Figure(grid, 'curve'))
            self.text_box.addItem(QListWidgetItem(func))
            self.plotter.reset_camera()

    #Функція для побудови параметричної кривої
    def add_curve_by_t(self):
        #визиваємо діалогове вікно для вводу функції
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()

            #обчислюємо точки кривої
            x, y, z = compute_parameter(functions)
            
            #будуємо та відображаємо криву
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='green', line_width=5)
            array = [x[0],y[0],z[0]]
            label = ["Curve " + str(self.temp_curve)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.meshes.append(Figure(grid, 'curve'))
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()

    #Функція для побудови конічної поверхні
    def add_conic_surface(self):
        self.temp_conic += 1
        #def _get_multiplier(directional_coor, anchor_coor, coor_type):
            #if coor_type == "X":
               # bounds = self.settings.x_bounds
            #elif coor_type == "Y":
                #bounds = self.settings.y_bounds
            #elif coor_type == "Z":
                #bounds = self.settings.z_bounds
            
            #if directional_coor == 0:
                #return 1e9 # cannot extend with this coordinate => return infinity

            #if directional_coor < 0:
                #return (bounds[0] - anchor_coor) / directional_coor
            #else:
                #return (bounds[1] - anchor_coor) / directional_coor
            
        dialog = PointDialog("Input point 0")
        point_0 = []
        if dialog.exec():
            point_0 = dialog.getInputs()

        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()

            curve_x, curve_y, curve_z = compute_parameter(functions)
            
            x = np.array([])
            y = np.array([])
            z = np.array([])
            r_values = np.arange(-10, 10, 0.1)
            x_inst = curve_x - point_0[0]
            y_inst = curve_y - point_0[1]
            z_inst = curve_z - point_0[2]
            for r in r_values:
                x = np.append(x, point_0[0] + r * (x_inst))
                y = np.append(y, point_0[1] + r * (y_inst))
                z = np.append(z, point_0[2] + r * (z_inst))
            grid = pv.PolyData(list(zip(x, y, z)))
            self.plotter.add_mesh(grid, color='purple', line_width=5, opacity=0.5)
            self.animate(grid.points)
            self.meshes.append(Figure(grid, 'Conic Surface'))
            array = np.array(
                [[x[0], y[0], z[0]],[curve_x[0],curve_y[0],curve_z[0]], [curve_x[len(curve_x)//2],curve_y[len(curve_y)//2],curve_z[len(curve_z)//2]],
                 [x[-1], y[-1], z[-1]]]
                )
         
            label = ["point c " + str(self.temp_conic), "point p " + str(self.temp_conic),"guide curve " + str(self.temp_conic),"creative line " + str(self.temp_conic)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()

    #Функція для побудови циліндричної поверхні
    def add_cylindrical_surface(self):
        self.temp_cylindric += 1
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        point_0 = [float(i) for i in vector]

        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()
            curve_x, curve_y, curve_z = compute_parameter(functions)
            
            x = np.array([])
            y = np.array([])
            z = np.array([])

            r_values = np.arange(-10, 10, 0.1)
            
            for r in r_values:
                x = np.append(x, point_0[0]*r + curve_x)
                y = np.append(y, point_0[1]*r + curve_y)
                z = np.append(z, point_0[2]*r + curve_z)

            grid = pv.PolyData(list(zip(x, y, z)))
            self.plotter.add_mesh(grid, color='yellow', line_width=5, opacity=0.5)
            self.animate(grid.points)
            self.meshes.append(Figure(grid, 'Cylindrical Surface'))
            array = np.array(
                [[x[0], y[0], z[0]],[curve_x[0],curve_y[0],curve_z[0]], [curve_x[len(curve_x)//2],curve_y[len(curve_y)//2],curve_z[len(curve_z)//2]],
                 [x[-1], y[-1], z[-1]]]
                )
         
            label = ["point c " + str(self.temp_cylindric), "point p " + str(self.temp_cylindric),"guide curve " + str(self.temp_cylindric),"creative line " + str(self.temp_cylindric)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)

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
        
        #Проходимо циклом по всім точкам присітиву та перевіряємо чи належать вони площині
        points = grid_2.mesh.points
        overlap_points = []
        delta = 1e-1
        for point in points:
            if np.abs(A*point[0] + B*point[1] + C*point[2] + D) < delta:
                overlap_points.append(point)

        #Відображаємо знайдений перетин
        intersection = pv.PolyData(overlap_points)
        
        self.plotter.add_mesh(intersection, color='white', point_size=10)
        self.meshes.append(Figure(intersection, 'Intersection'))

    def delete_figures(self):
        items = self.text_box.selectedIndexes()

        indexes = [i.row() for i in items]
        self.meshes = [i for j, i in enumerate(self.meshes) if j not in indexes]
        self.plotter.clear()
        self.plotter.show_grid()
        for i in self.meshes:
            match i.fig_type:
                case 'line':
                    self.plotter.add_mesh(i.mesh, color='black', line_width=5)
                case 'Surface':
                    self.plotter.add_mesh(i.mesh, color='red', opacity=0.7)
                case 'curve':
                    self.plotter.add_mesh(i.mesh, color='blue', line_width=5)
                case 'Conic Surface':
                    self.plotter.add_mesh(i.mesh, color='purple', line_width=5, opacity=0.5)
                case 'Cylindrical Surface':
                    self.plotter.add_mesh(i.mesh, color='yellow', line_width=5, opacity=0.5)
                case 'Intersection':
                    self.plotter.add_mesh(i.mesh, color='white', point_size=10)
                case 'Surface of revolution':
                    self.plotter.add_mesh(i.mesh, color='lightblue', opacity=0.25)

    #Функція для побудови поверхні обертання
    def add_surface_revolution(self):

        self.temp_surface_of_revolution += 1

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
            x_g, y_g, z_g = compute_parameter(functions)

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
            

            #будуємо та відображаємо поверхню
            self.animate(points)

            surface = pv.PolyData(points)
            self.plotter.add_mesh(surface, color="lightblue", opacity=0.25)
            self.meshes.append(Figure(surface, 'Surface of revolution'))
            array = np.array(
                [[x[0],y[0],z[0]],[x_g[0],y_g[0],z_g[0]], [x_g[len(x_g)//2],y_g[len(y_g)//2],z_g[len(z_g)//2]],
                 [x[-1],y[-1],z[-1]]]
                )
         
            label = ["point c " +  str(self.temp_surface_of_revolution), "point p " + str(self.temp_surface_of_revolution),"guide curve " + str(self.temp_surface_of_revolution),"creative line " + str(self.temp_surface_of_revolution)]
            self.plotter.add_point_labels(array,label,italic=True,font_size=20,point_color='red',point_size=20,render_points_as_spheres=True,always_visible=True,shadow=True)
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))

    def animate(self, points, step=1000):
        
        animation_plotter = pv.Plotter()
        animation_plotter.open_gif('points.gif')
        

        for i in range(0, len(points) - step, step):
            poly = pv.PolyData(points[i:i+step])
            
            animation_plotter.add_mesh(poly, opacity=0.25, color="lightblue")

            animation_plotter.render()
            animation_plotter.write_frame()

        #animation_plotter.close()
            



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())