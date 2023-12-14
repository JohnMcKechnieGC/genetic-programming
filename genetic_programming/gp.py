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


def flatten(expression, path=None):
    if path is None:
        path = [0]
    symbols_list = []
    if not isinstance(expression, tuple):
        symbols_list.append((expression, path))
    else:
        symbols_list.append((expression[0], path))
        for i in range(len(expression[1:])):
            new_path = path.copy()
            new_path.append(i)
            symbols_list.extend(flatten(expression[i + 1], new_path))
    return symbols_list


def mutate(expression, target_path, functions, all_symbols, terminal_symbols):
    if len(target_path) == 1:
        return get_random_expression(functions, all_symbols, terminal_symbols)
    branch = target_path.pop(0)
    new_expression = [expression[0]]
    for i in range(len(expression[1:])):
        if i == branch:
            new_expression.append(mutate(expression[i + 1], target_path, functions, all_symbols, terminal_symbols))
        else:
            new_expression.append(expression[i + 1])
    new_expression = tuple(new_expression)
    return new_expression


def solve(data, terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    function_symbols = list(functions.keys())
    terminal_symbols = list(terminals.keys())
    if numeric_constants is not None:
        terminal_symbols.extend(numeric_constants)
    all_symbols = function_symbols + terminal_symbols

    best_error = None
    best_expression = None
    for _ in range(iterations):
        expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
        func = get_callable_expression(functions, terminals, expression)
        error = error_function(func, data)
        if best_error is None or error < best_error:
            best_error = error
            best_expression = expression

    target = choice(flatten(best_expression))[1]

    # Demo of mutation
    mutated_expression = mutate(best_expression, target, functions, all_symbols, terminal_symbols)
    mutated_callable = get_callable_expression(functions, terminals, mutated_expression)
    mutated_expression_error = error_function(mutated_callable, data)
    print(mutated_expression_error, mutated_expression)

    return best_error, best_expression
