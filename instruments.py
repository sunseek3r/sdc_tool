import numpy as np
import re
from sympy import symbols, lambdify

def parse_function(function_str):
    function_str = function_str.split('=')
    variables = re.findall(r'\b([a-z])\b', function_str[-1])
    variables = list(set(variables))
    expression = function_str[-1].strip()
    return variables, expression

def compute_points(function_str, x_range, y_range):
    variables, expression = parse_function(function_str)

    if len(variables) != 2:
        raise ValueError(f"The function must contain exactly two variables, {variables} given")
    
    x, y = symbols(variables[0] + ' ' + variables[1])
    f = lambdify((x, y), expression, 'numpy')

    x_values = np.arange(x_range[0], x_range[1], 0.1)
    y_values = np.arange(y_range[0], y_range[1], 0.1)

    Z = f(x_values, y_values)

    return x_values, y_values, Z

def compute_parameter(functions):
    t = symbols('t')
    ts = np.arange(-50, 50, 0.1)
    f_x = lambdify(t, functions[0], 'numpy')
    f_y = lambdify(t, functions[1], 'numpy')
    f_z = lambdify(t, functions[2], 'numpy')

    x_values = f_x(ts)
    y_values = f_y(ts)
    z_values = f_z(ts)

    for i in range(len(x_values)):
        if (x_values[i] > 1000 or x_values[i] < -1000 or y_values[i] > 1000 or y_values[i] < -1000 
            or z_values[i] > 1000 or z_values[i] < -1000):
                x_values.pop(i)
                y_values.pop(i)
                z_values.pop(i)

    return x_values, y_values, z_values