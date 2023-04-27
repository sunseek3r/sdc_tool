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
