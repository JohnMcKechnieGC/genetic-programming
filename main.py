from symbolic_regression.terminals import x
from symbolic_regression.dataset import get_data_points
from symbolic_regression.gp import calculate_error
from genetic_programming.gp import solve
from genetic_programming.callables.basic_maths import \
    add, subtract, multiply, protected_divide, sine, cosine, protected_power, protected_log

functions = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '%': protected_divide,
    'sin': sine,
    'cos': cosine,
    'pow': protected_power,
    'log': protected_log,
}

terminals = {
    'x': x
}


if __name__ == '__main__':
    data_points = get_data_points()
    solve(data_points, terminals, functions, calculate_error, [1, 2, 3, 4, 5])
