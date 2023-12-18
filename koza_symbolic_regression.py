from genetic_programming.gp import solve
from genetic_programming.basic_maths_functions import \
    add, subtract, multiply, protected_divide, sine, cosine, exp, protected_log
from random import random


# Domain specific dataset
def get_data_points(n=100):
    data_points = []
    for _ in range(n):
        x = (random() - 0.5) * 2  # -0.5 (inc) to 0.5 (ex)
        y = x ** 4 + x ** 3 + x ** 2 + x
        data_points.append((x, y))
    return data_points


# Domain specific terminal functions
def x(x_value):
    def callable_x():
        return x_value
    return callable_x


# Domain specific error function
def mean_absolute_error(data):
    def callable_mean_absolute_error(gp_func):
        return sum([abs((y_val - gp_func(x_val)())) for (x_val, y_val) in data]) / len(data)
    return callable_mean_absolute_error


# Map symbols to callable functions for this domain
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


# Map symbols to terminals for this domain
domain_terminals = {
    'x': x
}


# Run the genetic programming
if __name__ == '__main__':
    NO_OF_RUNS = 10
    training_data = get_data_points(n=20)
    # numeric_constant_terminals = [1, 2, 3, 4, 5]
    error_function = mean_absolute_error([point for point in training_data])
    for run in range(1, NO_OF_RUNS + 1):
        expression, training_error = solve(domain_terminals, domain_functions, error_function, verbose=False)
        print(run, training_error, expression)
