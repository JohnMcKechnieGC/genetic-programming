from inspect import getfullargspec
from random import choice
from genetic_programming.callables.basic_maths import number


def get_callable_expression(functions, terminals, val):
    def leaf_node(point):
        if str(val).isnumeric():
            return number(val)
        else:
            return terminals[val](point)

    def branch_node(point):
        symbol = val[0]
        function = functions[symbol]
        args = []
        for arg in val[1:]:
            args.append(get_callable_expression(functions, terminals, arg)(point))
        return function(*args)

    def callable_expression(point):
        if isinstance(val, tuple):
            return branch_node(point)
        else:
            return leaf_node(point)

    return callable_expression


def tree(all_symbols, terminal_symbols, functions, symbol, level, max_level):
    function_callable = functions[symbol]
    arity = len(getfullargspec(function_callable).args)
    result = [symbol]
    result.extend([get_random_expression(functions, all_symbols, terminal_symbols, level + 1, max_level)
                   for _ in range(arity)])
    result = tuple(result)
    return result


def get_random_expression(functions, all_symbols, terminal_symbols, level=1, max_level=3):
    symbol = choice(all_symbols) if level < max_level \
        else choice(terminal_symbols)
    return symbol if symbol in terminal_symbols \
        else tree(all_symbols, terminal_symbols, functions, symbol, level, max_level)


def solve(data_points, terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    function_symbols = list(functions.keys())
    terminal_symbols = list(terminals.keys())
    if numeric_constants is not None:
        terminal_symbols.extend(numeric_constants)
    all_symbols = function_symbols + terminal_symbols

    best_so_far = None
    for _ in range(iterations):
        expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
        func = get_callable_expression(functions, terminals, expression)
        error = error_function(func, data_points)
        if best_so_far is None or error < best_so_far:
            best_so_far = error
            print(error, expression)
