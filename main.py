import sys

import os
os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QInputDialog,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit
from pyvistaqt import QtInteractor, MainWindow, BackgroundPlotter
import pyvista as pv
import numpy as np
from figure_classes import *
from inputs import SphereDialog, PointDialog, FunctionDialog, VectorLineDialog, ParameterDialog
from settings import Settings
from instruments import compute_points, compute_parameter

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


        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)


        left_widget = QWidget(main_widget)
        left_layout = QVBoxLayout(left_widget)
        left_widget.setMaximumWidth(300)
        main_layout.addWidget(left_widget)

        self.text_box = QTextEdit()
        left_layout.addWidget(self.text_box)

        
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
        self.text_box.append(f"Line: {point1}, {point2}")
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
                print((bounds[1] - anchor_coor) / directional_coor)
                return (bounds[1] - anchor_coor) / directional_coor
                
    
        dialog = PointDialog(0)
        point0 = []
        if dialog.exec():
            point0 = dialog.getInputs()
        
        dialog = VectorLineDialog()
        vector = []
        if dialog.exec():
            vector = dialog.getInputs()

        point0 = [float(i) for i in point0]
        vector = [float(i) for i in vector]

        print(self.settings.x_bounds)
        mult = min([_get_multiplier(vector[0], point0[0], "X"), _get_multiplier(vector[1], point0[1], "Y"), _get_multiplier(vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        end_point = [point_coor + vector_coor for point_coor, vector_coor in zip(point0, vector)]
    
        mult = min([_get_multiplier(-vector[0], point0[0], "X"), _get_multiplier(-vector[1], point0[1], "Y"), _get_multiplier(-vector[2], point0[2], "Z")])
        vector = [i * mult for i in vector]
        start_point = [point_coor - vector_coor for point_coor, vector_coor in zip(point0, vector)]

        line = pv.Line(start_point, end_point)
        self.plotter.add_mesh(line, color='black', line_width=5)
        self.text_box.append(f"Line by vector: {point0}, {vector}")
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
            self.text_box.append(f"Sphere: centre:{centre}, radius:{radius}")
            self.plotter.reset_camera()

            self.settings.update_bounds(sphere.bounds)

    def add_surface(self):
        dialog = PointDialog("Input point C")

        point_c = []

        if dialog.exec():
            point_c = dialog.getInputs()

        dialog = PointDialog("Input vector N")

        vector_n = []

        if dialog.exec():
            vector_n = dialog.getInputs()

        if len(point_c) != 3 or len(vector_n) != 3:
            return
              
        A = vector_n[0]
        B = vector_n[1]
        C = vector_n[2]
        D = -sum([i*j for i,j in zip(point_c, vector_n)])

        x = np.arange(self.settings.x_bounds[0], self.settings.x_bounds[1], 0.1)
        y = np.arange(self.settings.y_bounds[0], self.settings.y_bounds[1], 0.1)

        x, y = np.meshgrid(x, y)

        z = np.array([A*i + B * j + D for i,j in zip(x, y)])
        z = z / C

        grid = pv.StructuredGrid(x, y, z)
        self.plotter.add_mesh(grid, opacity=0.7, color='red')
        self.text_box.append("surface")
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
            self.text_box.append(func)
            self.plotter.reset_camera()

    def add_curve_by_t(self):
        dialog = ParameterDialog("Input parametric function i.e. in form \"sin(t) and so on\"")
        functions = []
        if dialog.exec():
            functions = dialog.getInputs()

            x,y,z = compute_parameter(functions)

            grid = pv.StructuredGrid(x, y, z)
            self.plotter.add_mesh(grid, color='green', line_width=5)
            self.text_box.append('\n'.join(functions))
            self.plotter.reset_camera()


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())