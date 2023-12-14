from inspect import getfullargspec
from random import choice
from callables.basic_maths import add, subtract, multiply, protected_divide, sine, cosine, \
    protected_power, protected_log, number
from symbolic_regression.terminals import x
from symbolic_regression.dataset import get_data_points


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

function_symbols = list(functions.keys())
terminal_symbols = list(terminals.keys())
terminal_symbols.extend([1, 2, 3, 4, 5])
all_symbols = function_symbols + terminal_symbols


def get_callable_expression(val):
    def callable_expression(point):
        if isinstance(val, tuple):
            symbol = val[0]
            function = functions[symbol]
            args = []
            for arg in val[1:]:
                args.append(get_callable_expression(arg)(point))
            return function(*args)
        else:
            if str(val).isnumeric():
                return number(val)
            else:
                return terminals[val](point)
    return callable_expression


def get_random_expression(level=1, max_level=3):
    if level < max_level:
        symbol = choice(all_symbols)
    else:
        symbol = choice(terminal_symbols)

    if symbol in terminal_symbols:
        return symbol
    else:
        function_callable = functions[symbol]
        arity = len(getfullargspec(function_callable).args)
        result = [symbol]
        result.extend([get_random_expression(level + 1, max_level=max_level) for _ in range(arity)])
        result = tuple(result)
        return result


if __name__ == '__main__':
    evaluated_functions = []
    data_points = get_data_points()
    for _ in range(10):
        expression = get_random_expression(max_level=5)
        func = get_callable_expression(expression)
        # Calculate the sum of the absolute errors
        error = sum([abs((point[1] - func(point)())) for point in data_points])
        evaluated_functions.append((error, expression))
    evaluated_functions = sorted(evaluated_functions, key=lambda point: point[0])
    for evaluated_function in evaluated_functions:
        print(evaluated_function)
