import sys

import os
os.environ["QT_API"] = "pyqt5"

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
from instruments import compute_points, compute_parameter, structured_grid_to_vtk_grid, get_bounds
from scipy.spatial import cKDTree


# Function to create and display the 3D plot


"""
TODO:
    !!!!!!!!!! CLEAR DOCUMENTATION !!!!!!!!!!!!!!!!!!!!
    - create classes for different types of input:
    1) Line
    2) Curve
    3) Plain
    4) Rotational Figures
    5) Conic Figures
    6) Cillyndric Figures
    - create input field
    - Customization tool i.e. zalivka
    - Intersections tool
    - save to file
    - animations
"""


class Window(MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self, parent=None)
        self.settings = Settings()
    
        self.setWindowTitle("SDC Tool")
        self.setGeometry(50, 50, 800, 600)

        self.meshes = []

        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)

        

        left_widget = QWidget(main_widget)
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(300)
        main_layout.addWidget(left_widget)

        self.text_box = QListWidget(self)
        self.text_box.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        left_layout.addWidget(self.text_box)

        
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('File')
        exitButton = QtWidgets.QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.triggered.connect(self.close)
        fileMenu.addAction(exitButton)

        tools_menu = mainMenu.addMenu('Tools')
        intersect_button = QtWidgets.QAction('Intersection', self)
        intersect_button.triggered.connect(self.intersect)
        tools_menu.addAction(intersect_button)

        right_widget = QWidget(main_widget)
        right_layout = QVBoxLayout(right_widget)
        main_layout.addWidget(right_widget)
        


        self.plotter = BackgroundPlotter()
        right_layout.addWidget(self.plotter)


        sphere_button = QPushButton("Sphere", self)
        sphere_button.clicked.connect(self.add_sphere)
        left_layout.addWidget(sphere_button)

        line_button = QPushButton("Line", self)
        line_button.clicked.connect(self.add_line)
        left_layout.addWidget(line_button)

        surface_button = QPushButton("Surface", self)
        surface_button.clicked.connect(self.add_surface)
        left_layout.addWidget(surface_button)
        

        line_by_vector_button = QPushButton("Line by vector", self)
        line_by_vector_button.clicked.connect(self.add_vector_line)
        left_layout.addWidget(line_by_vector_button)

        curve_button = QPushButton("Curve", self)
        curve_button.clicked.connect(self.add_curve)
        left_layout.addWidget(curve_button)

        parameters_button = QPushButton("Curve by parameter", self)
        parameters_button.clicked.connect(self.add_curve_by_t)
        left_layout.addWidget(parameters_button)

        conic_curve_button = QPushButton("Conic surface", self)
        conic_curve_button.clicked.connect(self.add_conic_surface)
        left_layout.addWidget(conic_curve_button)

        cylindrical_curve_button = QPushButton("Cylindrical surface", self)
        cylindrical_curve_button.clicked.connect(self.add_cylindrical_surface)
        left_layout.addWidget(cylindrical_curve_button)

        self.plotter.show_grid()


        self.setCentralWidget(main_widget)
        self.show()

    

    def add_line(self):
        dialog = PointDialog("Input point 1")
        point1 = []
        if dialog.exec():
            point1 = dialog.getInputs()
        
        dialog = PointDialog("Input point 2")
        point2 = []
        if dialog.exec():
            point2 = dialog.getInputs()
        if len(point1) != 3 or len(point2) != 3:
            return
        point1 = [float(i) for i in point1]
        point2 = [float(i) for i in point2]

        line = pv.Line(point1, point2)
        self.plotter.add_mesh(line, color='black', line_width=5)
        self.meshes.append(Figure(line, type='line'))
        self.text_box.addItem(QListWidgetItem(f"Line: {point1}, {point2}"))
        self.plotter.reset_camera()

    def add_vector_line(self):
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
                
        dialog = PointDialog("Input point 0")

        point0 = []
        if dialog.exec():
            point0 = dialog.getInputs()
        
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        point0 = [float(i) for i in point0]
        vector = [float(i) for i in vector]

        mult = min([_get_multiplier(vector[0], point0[0], "X"), _get_multiplier(vector[1], point0[1], "Y"), _get_multiplier(vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        end_point = [point_coor + vector_coor for point_coor, vector_coor in zip(point0, vector)]
    
        mult = min([_get_multiplier(-vector[0], point0[0], "X"), _get_multiplier(-vector[1], point0[1], "Y"), _get_multiplier(-vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        start_point = [point_coor - vector_coor for point_coor, vector_coor in zip(point0, vector)]

        line = pv.Line(start_point, end_point)
        self.plotter.add_mesh(line, color='black', line_width=5)
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

    def add_surface(self):
        dialog = PointDialog("Input point C")

        point_c = []

        if dialog.exec():
            point_c = [float(i) for i in dialog.getInputs()]

        dialog = PointDialog("Input vector N")

        vector_n = []

        if dialog.exec():
            vector_n = [float(i) for i in dialog.getInputs()]

        if len(point_c) != 3 or len(vector_n) != 3:
            return
              
        A = vector_n[0]
        B = vector_n[1]
        C = vector_n[2]
        D = -(point_c[0] * A + point_c[1] * B + point_c[2] * C)

        x = np.arange(self.settings.x_bounds[0], self.settings.x_bounds[1], 0.3)
        y = np.arange(self.settings.y_bounds[0], self.settings.y_bounds[1], 0.3)

        x, y = np.meshgrid(x, y)
        z = -(A * x + B * y + D) / C
        grid = pv.StructuredGrid(x, y, z)
        self.plotter.add_mesh(grid, opacity=0.7, color='red')
        self.meshes.append(Surface(A, B, C, D, grid))
        self.text_box.addItem(QListWidgetItem("surface"))
        self.plotter.reset_camera()

    def add_curve(self):
        dialog = FunctionDialog("Input a function in form i.e. \"f(z)=2*x + 3*y\"")
        func = ""
        if dialog.exec():
            func = dialog.getInputs()

        print(func)

        if func != "":
            x, y, z = compute_points(func, self.settings.x_bounds, self.settings.y_bounds)
            print(type(x), type(y), type(z))
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='blue', line_width=5)
            self.meshes.append(Figure(grid, 'curve'))
            self.text_box.addItem(QListWidgetItem(func))
            self.plotter.reset_camera()

    def add_curve_by_t(self):
        
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()

            x, y, z = compute_parameter(functions)
            
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='green', line_width=5)
            self.meshes.append(Figure(grid, 'curve'))
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()

    def add_conic_surface(self):
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
            for i, j, k in zip(curve_x, curve_y, curve_z):
                #mul_x = _get_multiplier(point_0[0] - i, i, "X")
                #mul_y = _get_multiplier(point_0[1] - j, j, "Y")
                #mul_z = _get_multiplier(point_0[2] - k, k, "Z")
                x = np.append(x, [i, point_0[0]])
                y = np.append(y, [j, point_0[1]])
                z = np.append(z, [k, point_0[2]])
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='purple', line_width=5, opacity=0.5)
            self.meshes.append(Figure(grid, 'Conic Surface'))
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()

    def add_cylindrical_surface(self):
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        vector = [float(i) for i in vector]

        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()
            curve_x, curve_y, curve_z = compute_parameter(functions)
            
            x = np.array([])
            y = np.array([])
            z = np.array([])

            for i, j, k in zip(curve_x, curve_y, curve_z):
                x = np.append(x, [i, (i + vector[0])])
                y = np.append(y, [j, (j + vector[1])])
                z = np.append(z, [k, (k + vector[2])])
            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='yellow', line_width=5, opacity=0.5)
            self.meshes.append(Figure(grid, 'Cylindrical Surface'))
            self.text_box.addItem(QListWidgetItem('\n'.join(functions)))
            self.plotter.reset_camera()
    
    def intersect(self):
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
        
        points = grid_2.mesh.points
        overlap_points = []
        delta = 1e-1
        for point in points:
            if np.abs(A*point[0] + B*point[1] + C*point[2] + D) < delta:
                overlap_points.append(point)

        intersection = pv.PolyData(overlap_points)
        
        self.plotter.add_mesh(intersection, color='yellow', point_size=10)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())