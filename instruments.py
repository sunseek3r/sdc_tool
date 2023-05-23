import numpy as np
import re
from sympy import symbols, lambdify
import vtk

#Функція для парсингу введеної користувачем функції
def parse_function(function_str):
    function_str = function_str.split('=')
    variables = re.findall(r'\b([a-z])\b', function_str[-1])
    variables = list(set(variables))
    expression = function_str[-1].strip()
    return variables, expression

#Функція для обчислення точок кривої
def compute_points(function_str, x_range, y_range):
    variables, expression = parse_function(function_str)

    if len(variables) != 2:
        raise ValueError(f"The function must contain exactly two variables, {variables} given")
    
    #перетворюємо введену користувачем функцію у лямбда-вираз
    x, y = symbols(variables[0] + ' ' + variables[1])
    f = lambdify((x, y), expression, 'numpy')

    #обчислюємо координати точок по осях x та y
    x_values = np.arange(x_range[0], x_range[1], 0.1)
    y_values = np.arange(y_range[0], y_range[1], 0.1)

    #обчислюємо координати точок по осі z
    Z = f(x_values, y_values)

    return x_values, y_values, Z

#Функція для обчислення точок параметричної кривої
def compute_parameter(functions):
    t = symbols('t')

    #задаємо межі параметра t
    ts = np.arange(-50, 50, 0.1)

    #перетворюємо введені користувачем функції у лямбда-вирази
    for i in range(3):
        if 't' not in functions[i]:
            raise ValueError(f"No t parameter in {i+1}th function. If you want to specify a constant use 0*t+C")
    f_x = lambdify(t, functions[0], 'numpy')
    f_y = lambdify(t, functions[1], 'numpy')
    f_z = lambdify(t, functions[2], 'numpy')

    #обчислюємо координати точок по кожній осі
    x_values = f_x(ts)
    y_values = f_y(ts)
    z_values = f_z(ts)

    #знаходимо точки що лежать за межами побудови
    mask = np.ones_like(x_values, dtype=bool)
    to_delete = []
    for ind, (x,y,z) in enumerate(zip(x_values, y_values, z_values)):
        if (x > 100 or x < -100) or (y > 100 or y < -100) or (z > 100 or z < -100):
            to_delete.append(ind)

    #видаляємо точки що лежать за межами побудови
    mask[to_delete] = False
    x_values = x_values[mask]
    y_values = y_values[mask]
    z_values = z_values[mask]

    return x_values, y_values, z_values

#Функція, що повертає межі побудови
def get_bounds(grid):
    xmin, xmax, ymin, ymax, zmin, zmax = grid.bounds
    return np.array([[xmin, xmax], [ymin, ymax], [zmin, zmax]])

def rotation_matrix_from_vector(vec1, vec2):
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def sort_points(points):
    points = np.array(points)
    centroid = np.mean(points, axis=0)
    
    normal = np.cross(points[1] - points[0], points[2] - points[1])
    normal = normal / np.linalg.norm(normal)

    rotation_matrix = rotation_matrix_from_vector(normal, [0, 0, 1])
    rotated_points = np.dot(points - centroid, rotation_matrix)
    # Now, calculate the angles in 2D
    angles = np.arctan2(rotated_points[:,1], rotated_points[:,0])

    # If there's a need to convert angles from [-pi, pi] to [0, 2pi]
    angles = np.where(angles >= 0, angles, angles + 2 * np.pi)

    # Now let's sort the points by these angles
    sorted_indices = np.argsort(angles)
    sorted_points = points[sorted_indices]
    return sorted_points

#Функція для обчислення матриці поворота
def get_rotational_matrix(theta, vector):
    u_x = vector[0]
    u_y = vector[1]
    u_z = vector[2]
    cos = np.cos(theta)
    sin = np.sin(theta)
    R = np.array([
        [cos + (u_x**2)*(1-cos), u_x*u_y*(1-cos) - u_z * sin, u_x*u_z*(1-cos) + u_y * sin],
        [u_y*u_x*(1-cos) + u_z * sin, cos + (u_y**2)*(1-cos), u_y*u_z*(1-cos) - u_x * sin],
        [u_z*u_x*(1-cos) - u_y * sin, u_z * u_y*(1-cos) + u_x*sin, cos + (u_z**2)*(1-cos)]
    ])

    return R