from inspect import getfullargspec
from random import choice
from callables.basic_maths import add, subtract, multiply, protected_divide, sine, cosine, \
    protected_power, protected_log
from symbolic_regression.terminals import x


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
        result.extend([get_random_expression(level + 1) for _ in range(arity)])
        result = tuple(result)
        return result


if __name__ == '__main__':
    expression = get_random_expression()
    func = get_callable_expression(expression)
    print(expression)
    test_point = (0.1, 0.2)
    print(func(test_point)())
