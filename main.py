from genetic_programming.gp import solve
from genetic_programming.callables.basic_maths import \
    add, subtract, multiply, protected_divide, sine, cosine, protected_power, protected_log
from symbolic_regression.terminals import x
from symbolic_regression.dataset import get_data_points
from symbolic_regression.gp import mean_absolute_error

domain_functions = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '%': protected_divide,
    'sin': sine,
    'cos': cosine,
    'pow': protected_power,
    'log': protected_log,
}

domain_terminals = {
    'x': x
}


if __name__ == '__main__':
    data_points = get_data_points(n=200)
    numeric_constant_terminals = [1, 2, 3, 4, 5]
    error, expression = solve(data_points, domain_terminals, domain_functions, mean_absolute_error,
                              numeric_constants=numeric_constant_terminals)
    print(error, expression)
