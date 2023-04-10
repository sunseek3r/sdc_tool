import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to create and display the 3D plot

plots = []

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

def simple_function():
    """
      This function doesn't do notging
      ------
      Inputs:
      
      -------
      Returns:
    """
    
def on_click(event):
    widget = event.widget
    index = widget.index("@%s,%s" % (event.x, event.y))
    if index:
        tag = widget.tag_names(index)
        print("Clicked on tag:", tag)
def draw_3d_plot():
    ax = fig.add_subplot(111, projection="3d")

    point1 = [1, 3, 2]
    point2 = [-1, 4, -8]

    x_values = [point1[0], point2[0]]
    y_values = [point1[1], point2[1]]
    z_values = [point1[2], point2[2]]

    ax.plot(x_values, y_values, z_values, 'bo', linestyle='-')

    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")

    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=1)

# Create main window
fig = plt.figure(figsize=(15,9.7))
ax = fig.add_subplot(111, projection="3d")
root = tk.Tk()
root.title("Interactive 3D Plot")
root.geometry("1920x1080")
# Create main frame
main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=1, padx=0, pady=0)

# Create plot frame
frame_plot = ttk.Frame(main_frame)
frame_plot.grid(row=0, column=1, padx = 10, pady= 0)

# Create control frame
frame_control = ttk.Frame(main_frame)
frame_control.grid(row=1, column=1, padx=0, pady=0)
main_frame.grid()
# Add button to draw plot
btn_draw = tk.Button(frame_control, text="Draw 3D Plot", command=draw_3d_plot, height = 5, width=213).grid(row=1,column=0)
textbox = tk.Text(root,height=66, width = 70).grid(row = 0, column = 0)
canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas.get_tk_widget().grid(row=0, column= 1)
root.mainloop()



