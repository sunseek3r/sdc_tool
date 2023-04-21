import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTextEdit, QPushButton, QDialog, QInputDialog,QMessageBox
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from figure_classes import *


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
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

 
        self.setWindowTitle("PyQt Matplotlib 3D plot")
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

      
        fig = plt.figure()
        self.ax = fig.add_subplot(111, projection="3d")


        self.canvas = FigureCanvas(fig)
        right_layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

 
        update_button = QPushButton("Update 3D plot", self)
        update_button.clicked.connect(self.update_plot)
        left_layout.addWidget(update_button)

 
        line_button = QPushButton("Line", self)
        line_button.clicked.connect(self.add_line)
        left_layout.addWidget(line_button)

      
        self.setCentralWidget(main_widget)
        self.show()

    def update_plot(self):

        input_text = self.text_box.toPlainText()
        lines = input_text.strip().split('\n')

        # Clear 3D plot
        self.ax.clear()

      
        for line in lines:
            
            coords = line.split(',')
            x1, y1, z1, x2, y2, z2 = map(float, coords)


            self.ax.plot([x1, x2], [y1, y2], [z1, z2])

        self.ax.set_xlabel("X Label")
        self.ax.set_ylabel("Y Label")
        self.ax.set_zlabel("Z Label")

    
        self.canvas.draw()

    def add_line(self):
  
        msg_box = QMessageBox()
        msg_box.setText("Enter the coordinates of the two points for the line:")
        x1, ok1 = QInputDialog.getDouble(self, "Input", "X1:")
        y1, ok2 = QInputDialog.getDouble(self, "Input", "Y1:")
        z1, ok3 = QInputDialog.getDouble(self, "Input", "Z1:")
        x2, ok4 = QInputDialog.getDouble(self, "Input", "X2:")
        y2, ok5 = QInputDialog.getDouble(self, "Input", "Y2:")
        z2, ok6 = QInputDialog.getDouble(self, "Input", "Z2:")

  
        if ok1 and ok2 and ok3 and ok4 and ok5 and ok6:
            line_text = f"{x1}, {y1}, {z1}, {x2}, {y2}, {z2}"
            self.text_box.append(line_text)
            self.update_plot()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())