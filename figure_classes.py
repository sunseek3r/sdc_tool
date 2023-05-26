"""
    A file for figure classes
"""

class Figure():
    def __init__(self, mesh, fig_type, labels, color):
        self.mesh = mesh
        self.fig_type = fig_type
        self.labels = labels
        self.color = color


class PointLabel():
    def __init__(self, label, array):
        self.label = label
        self.array = array

class ArrowLabel():
    def __init__(self, arrow, color='blue'):
        self.arrow = arrow
        self.color = color



class ConicSurface(Figure):
    def __init__(self, mesh, labels, curve_x, curve_y, curve_z, point_0, color):
        Figure.__init__(self, mesh, 'Conic Surface', labels, color)
        self.curve_x = curve_x
        self.curve_y = curve_y
        self.curve_z = curve_z
        self.point_0 = point_0
        self.color = color

class CylindricSurface(Figure):
    def __init__(self, mesh, labels, curve_x, curve_y, curve_z, point_0, color):
        Figure.__init__(self, mesh, 'Cylindrical Surface', labels, color)
        self.curve_x = curve_x
        self.curve_y = curve_y
        self.curve_z = curve_z
        self.point_0 = point_0
        self.color = color

class Surface(Figure):
    def __init__(self, A, B, C, D, mesh, labels, color):
        Figure.__init__(self, mesh, 'Surface', labels, color)
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        #self.fig_type = 'Surface'
        self.color = color

