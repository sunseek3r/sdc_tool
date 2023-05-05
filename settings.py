

class Settings():
    def __init__(self):
        self.x_bounds = [-100, 100]
        self.y_bounds = [-100, 100]
        self.z_bounds = [-100, 100]

    def update_bounds(self, bounds):
        "Input: Bounds from mesh, first two elements are X bounds, second: Y bounds, third: z bounds"

        self.x_bounds[0] = min(self.x_bounds[0], bounds[0])
        self.x_bounds[1] = max(self.x_bounds[1], bounds[1])

        self.y_bounds[0] = min(self.y_bounds[0], bounds[2])
        self.y_bounds[1] = max(self.y_bounds[1], bounds[3])

        self.z_bounds[0] = min(self.z_bounds[0], bounds[4])
        self.z_bounds[1] = max(self.z_bounds[1], bounds[5])