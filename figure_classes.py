"""
    A file for figure classes (look TODO in main.py)
"""

class Figure():
    def __init__(self, mesh, fig_type='Figure', labels=[]):
        self.mesh = mesh
        self.fig_type = fig_type
        self.labels = labels

class Line(Figure):
    """
        This is a class for Line figure
    """


    def __init__(self, d1, d2, mesh):
        Figure.__init__(self, mesh)
        self.d1 = d1
        self.d2 = d2
        self.type = 'Line'


    def draw(self, ax):
        x_values = [self.d1[0], self.d2[0]]
        y_values = [self.d1[1], self.d2[1]]
        z_values = [self.d1[2], self.d2[2]]


class Surface(Figure):
    def __init__(self, A, B, C, D, mesh):
        Figure.__init__(self, mesh)
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.fig_type = 'Surface'


