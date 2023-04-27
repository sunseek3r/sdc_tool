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
from inputs import SphereDialog


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

        self.plotter.show_grid()


        self.setCentralWidget(main_widget)
        self.show()

    

    def add_line(self):
        pass
    
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
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())