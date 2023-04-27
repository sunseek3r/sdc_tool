import sys

import os
os.environ["QT_API"] = "pyqt5"

from qtpy import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QInputDialog,QMessageBox
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor, MainWindow, BackgroundPlotter
import pyvista as pv
import numpy as np
from figure_classes import *
from inputs import SphereDialog, LineDialog, VectorLineDialog
from settings import Settings

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
        
        line_by_vector_button = QPushButton("Line by vector", self)
        line_by_vector_button.clicked.connect(self.add_vector_line)
        left_layout.addWidget(line_by_vector_button)

        self.plotter.show_grid()


        self.setCentralWidget(main_widget)
        self.show()

    

    def add_line(self):
        dialog = LineDialog(1)
        point1 = []
        if dialog.exec():
            point1 = dialog.getInputs()
        
        dialog = LineDialog(2)
        point2 = []
        if dialog.exec():
            point2 = dialog.getInputs()

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
                
    
        dialog = LineDialog(0)
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
        centre = [float(i) for i in centre]
        radius, ok = QInputDialog.getDouble(self, "Input", "Radius")
        if ok:
            sphere = pv.Sphere(radius, centre)
            self.plotter.add_mesh(sphere, opacity=0.5, show_edges=False)
            self.text_box.append(f"Sphere: centre:{centre}, radius:{radius}")
            self.plotter.reset_camera()

        self.settings.update_bounds(sphere.bounds)

    def add_surface(self):
        pass
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())