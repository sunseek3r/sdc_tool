"""
    A file for figure classes (look TODO in main.py)
"""


class Line():
    """
        This is a class for Line figure
    """


    def __init__(self, d1, d2):
        self.d1 = d1
        self.d2 = d2


    def draw(self, ax):
        x_values = [self.d1[0], self.d2[0]]
        y_values = [self.d1[1], self.d2[1]]
        z_values = [self.d1[2], self.d2[2]]




        


