from genetic_programming.gp import solve
from genetic_programming.callables.basic_maths import \
    add, subtract, multiply, protected_divide, sine, cosine, exp, protected_log
from symbolic_regression.terminals import x
from symbolic_regression.dataset import get_data_points
from symbolic_regression.gp import get_mean_absolute_error

domain_functions = {
    '+': add,
    '-': subtract,
    '*': multiply,
    '%': protected_divide,
    'sin': sine,
    'cos': cosine,
    'exp': exp,
    'log': protected_log,
}

domain_terminals = {
    'x': x
}


if __name__ == '__main__':
    training_data = get_data_points(n=20)
    # numeric_constant_terminals = [1, 2, 3, 4, 5]
    error_function = get_mean_absolute_error([point for point in training_data])
    training_error, expression = solve(domain_terminals, domain_functions, error_function)
    print(training_error, expression)
