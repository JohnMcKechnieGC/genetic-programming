from inspect import getfullargspec
from random import choice, randint, random
from genetic_programming.callables.basic_maths import number
from copy import deepcopy


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


def mutate(expression, target_path, functions, all_symbols, terminal_symbols, replacement=None):
    if len(target_path) == 1:
        return get_random_expression(functions, all_symbols, terminal_symbols, max_level=3) \
            if replacement is None else replacement

    root = expression[0]
    operands = list(expression[1:])
    branch = target_path[1]
    operands[branch] = mutate(operands[branch], target_path[1:], functions, all_symbols, terminal_symbols, replacement)
    new_expression = [root]
    new_expression.extend(operands)
    new_expression = tuple(new_expression)

    return new_expression


def get_subtree(expression, target_path):
    if len(target_path) == 1:
        return expression
    else:
        operands = list(expression[1:])
        branch = target_path[1]
        return get_subtree(operands[branch], target_path[1:])


def replace_subtree(expression, target_path, replacement):
    if len(target_path) == 1:
        return replacement

    root = expression[0]
    operands = list(expression[1:])
    branch = target_path[1]
    operands[branch] = replace_subtree(operands[branch], target_path[1:], replacement)
    new_expression = [root]
    new_expression.extend(operands)
    new_expression = tuple(new_expression)

    return new_expression


def crossover(expression1, expression2, target1=None, target2=None):
    target1 = choice(flatten(expression1))[1] if target1 is None else target1
    target2 = choice(flatten(expression2))[1] if target2 is None else target2
    subtree1 = get_subtree(expression1, target1)
    subtree2 = get_subtree(expression2, target2)
    crossed1 = replace_subtree(expression1, target1, subtree2)
    crossed2 = replace_subtree(expression2, target2, subtree1)
    return crossed1, crossed2


def setup(data, functions, numeric_constants, terminals):
    function_symbols = list(functions.keys())
    terminal_symbols = list(terminals.keys())
    if numeric_constants is not None:
        terminal_symbols.extend(numeric_constants)
    all_symbols = function_symbols + terminal_symbols
    training_data = data[:int(len(data) / 2)]
    test_data = data[int(len(data) / 2):]
    return all_symbols, terminal_symbols, test_data, training_data


def get_random_target(expression):
    nodes = flatten(expression)
    selected_node = choice(nodes)
    target = selected_node[1]
    return target


def solve_mutation(data, terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    all_symbols, terminal_symbols, test_data, training_data = setup(data, functions, numeric_constants, terminals)

    best_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
    best_error = error_function(get_callable_expression(functions, terminals, best_expression), training_data)

    for i in range(iterations):
        target = get_random_target(best_expression)
        new_expression = mutate(best_expression, target, functions, all_symbols, terminal_symbols)
        callable_expression = get_callable_expression(functions, terminals, new_expression)
        training_set_error = error_function(callable_expression, training_data)

        if training_set_error < best_error:
            best_error = training_set_error
            best_expression = new_expression
            test_set_error = error_function(callable_expression, test_data)
            print(i, training_set_error, test_set_error, new_expression)

    return best_error, best_expression


def solve_random(data, terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    all_symbols, terminal_symbols, test_data, training_data = setup(data, functions, numeric_constants, terminals)

    best_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
    best_error = error_function(get_callable_expression(functions, terminals, best_expression),
                                training_data)

    for i in range(iterations):
        new_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
        callable_expression = get_callable_expression(functions, terminals, new_expression)
        training_set_error = error_function(callable_expression, training_data)

        if training_set_error < best_error:
            best_error = training_set_error
            best_expression = new_expression
            test_set_error = error_function(callable_expression, test_data)
            print(i, training_set_error, test_set_error, new_expression)

    return best_error, best_expression


def solve(data, terminals, functions, error_function,
          numeric_constants=None, iterations=5, max_level=5, population_size=10, crossover_rate=0.7, mutation_rate=0.1):
    all_symbols, terminal_symbols, test_data, training_data = setup(data, functions, numeric_constants, terminals)

    population = [get_random_expression(functions, all_symbols, terminal_symbols, max_level=max_level)
                  for _ in range(population_size)]
    population = [(population[i],
                   error_function(get_callable_expression(functions, terminals, population[i]), training_data))
                  for i in range(population_size)]
    next_generation = []

    for _ in range(iterations):
        for _ in range(population_size // 2):
            r1 = randint(0, population_size - 1)
            r2 = randint(0, population_size - 1)
            parent1 = population[r1][0] if population[r1][1] > population[r2][1] else population[r2][0]
            r1 = randint(0, population_size - 1)
            r2 = randint(0, population_size - 1)
            parent2 = population[r1][0] if population[r1][1] > population[r2][1] else population[r2][0]
            if random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1 = deepcopy(parent1)
                child2 = deepcopy(parent2)
            if random() < mutation_rate:
                mutation_target = get_random_target(child1)
                child1 = mutate(child1, mutation_target, functions, all_symbols, terminal_symbols)
            if random() < mutation_rate:
                mutation_target = get_random_target(child2)
                child2 = mutate(child2, mutation_target, functions, all_symbols, terminal_symbols)
            next_generation.append(child1)
            next_generation.append(child2)
        population = next_generation
        population = [(population[i],
                       error_function(get_callable_expression(functions, terminals, population[i]), training_data))
                      for i in range(population_size)]
        next_generation = []
    population = sorted(population, key=lambda x: x[1])
    return population[0][1], population[0][0]
