import tkinter as tk
from tkinter import ttk

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




def draw_plots(plots, ax):
    """
        This function draws all plots
    """
    for figure in plots:
        figure.draw(ax)

    return ax

def main():
    """
    Main launch code
    """

    plots = [Line([0, 1, 2], [2, 3, 5])]    

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")

    # Create main window
    root = tk.Tk()
    root.title("Interactive 3D Plot")

    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.grid(row=0, column=0, padx=5, pady=5)

    # Create plot frame
    frame_plot = ttk.Frame(main_frame)
    frame_plot.grid(row=0, column=0)

    # Create control frame
    frame_control = ttk.Frame(main_frame)
    frame_control.grid(row=0, column=1, padx=5, pady=5)

    def draw_button_pressed():
        global ax
        ax = draw_plots(plots, ax)

    # Add button to draw plot
    btn_draw = ttk.Button(frame_control, text="Draw 3D Plot",
                          command=draw_button_pressed)
    btn_draw.grid(row=0, column=0, pady=5)

    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().grid(row=0, column=0)

    root.mainloop()


if __name__ == '__main__':
    main()
