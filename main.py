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
from inputs import SphereDialog, PointDialog, FunctionDialog
from settings import Settings
from instruments import compute_points

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
        


        self.plotter = QtInteractor()
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
        
        curve_button = QPushButton("Curve", self)
        curve_button.clicked.connect(self.add_curve)
        left_layout.addWidget(curve_button)


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
        self.plotter.add_mesh(grid, opacity=0.7)
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


        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())