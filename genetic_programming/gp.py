from inspect import getfullargspec
from random import choice, randint, random
from genetic_programming.callables.basic_maths import number
from copy import deepcopy


def get_callable_expression(functions, terminals, val):
    def leaf_node(x_value):
        if str(val).isnumeric():
            return number(val)
        else:
            return terminals[val](x_value)

    def branch_node(x_value):
        symbol = val[0]
        function = functions[symbol]
        args = []
        for arg in val[1:]:
            args.append(get_callable_expression(functions, terminals, arg)(x_value))
        return function(*args)

    def callable_expression(x_value):
        if isinstance(val, tuple):
            return branch_node(x_value)
        else:
            return leaf_node(x_value)

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


def select_crossover_candidate(expression, terminal_symbols, prob_internal=0.9):
    target_candidates = flatten(expression)
    if random() < prob_internal:
        internal_candidates = [candidate for candidate in target_candidates if candidate[0] not in terminal_symbols]
        if len(internal_candidates) > 0:
            target_candidates = internal_candidates
    else:
        target_candidates = [candidate for candidate in target_candidates if candidate[0] in terminal_symbols]
    return choice(target_candidates)[1]


def crossover(expression1, expression2, terminal_symbols, target1=None, target2=None):
    target1 = select_crossover_candidate(expression1, terminal_symbols) if target1 is None else target1
    target2 = select_crossover_candidate(expression2, terminal_symbols) if target2 is None else target2
    subtree1 = get_subtree(expression1, target1)
    subtree2 = get_subtree(expression2, target2)
    crossed1 = replace_subtree(expression1, target1, subtree2)
    crossed2 = replace_subtree(expression2, target2, subtree1)
    return crossed1, crossed2


def setup(functions, numeric_constants, terminals):
    function_symbols = list(functions.keys())
    terminal_symbols = list(terminals.keys())
    if numeric_constants is not None:
        terminal_symbols.extend(numeric_constants)
    all_symbols = function_symbols + terminal_symbols
    return all_symbols, terminal_symbols


def get_random_target(expression):
    nodes = flatten(expression)
    selected_node = choice(nodes)
    target = selected_node[1]
    return target


def solve_mutation(terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    all_symbols, terminal_symbols = setup(functions, numeric_constants, terminals)

    best_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
    best_error = error_function(get_callable_expression(functions, terminals, best_expression))

    for i in range(iterations):
        target = get_random_target(best_expression)
        new_expression = mutate(best_expression, target, functions, all_symbols, terminal_symbols)
        callable_expression = get_callable_expression(functions, terminals, new_expression)
        training_set_error = error_function(callable_expression)

        if training_set_error < best_error:
            best_error = training_set_error
            best_expression = new_expression
            test_set_error = error_function(callable_expression)
            print(i, training_set_error, test_set_error, new_expression)

    return best_error, best_expression


def solve_random(terminals, functions, error_function, numeric_constants=None, iterations=100, max_level=5):
    all_symbols, terminal_symbols = setup(functions, numeric_constants, terminals)

    best_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
    best_error = error_function(get_callable_expression(functions, terminals, best_expression))

    for i in range(iterations):
        new_expression = get_random_expression(functions, all_symbols, terminal_symbols, 1, max_level)
        callable_expression = get_callable_expression(functions, terminals, new_expression)
        training_set_error = error_function(callable_expression)

        if training_set_error < best_error:
            best_error = training_set_error
            best_expression = new_expression
            test_set_error = error_function(callable_expression)
            print(i, training_set_error, test_set_error, new_expression)

    return best_error, best_expression


def select_parent(population):
    candidates = [randint(0, len(population) - 1) for _ in range(10)]
    winner = min(candidates, key=lambda x: population[x][1])
    return population[winner][0]


def random_population(population_size, functions, all_symbols, terminal_symbols, terminals, max_level, error_function):
    population = [get_random_expression(functions, all_symbols, terminal_symbols, max_level=max_level)
                  for _ in range(population_size)]
    population = [(population[i], error_function(get_callable_expression(functions, terminals, population[i])))
                  for i in range(population_size)]
    return population


def apply_crossover(parent1, parent2, crossover_rate, terminal_symbols):
    if random() < crossover_rate:
        child1, child2 = crossover(parent1, parent2, terminal_symbols)
    else:
        child1 = deepcopy(parent1)
        child2 = deepcopy(parent2)
    return child1, child2


def apply_mutation(expression, mutation_rate, functions, all_symbols, terminal_symbols):
    if random() < mutation_rate:
        mutation_target = get_random_target(expression)
        expression = mutate(expression, mutation_target, functions, all_symbols, terminal_symbols)
    return expression


def get_best_in_generation(population):
    return min(population, key=lambda x: x[1])


def initialise_next_generation(elitism_rate, best_so_far):
    next_generation = []
    if random() < elitism_rate:
        next_generation.append(best_so_far[0])
    return next_generation


def populate_next_generation(population, elitism_rate, best_so_far, crossover_rate, mutation_rate,
                             functions, all_symbols, terminal_symbols):
    next_generation = initialise_next_generation(elitism_rate, best_so_far)
    for _ in range(len(population) // 2):
        parent1 = select_parent(population)
        parent2 = select_parent(population)
        child1, child2 = apply_crossover(parent1, parent2, crossover_rate, terminal_symbols)
        child1 = apply_mutation(child1, mutation_rate, functions, all_symbols, terminal_symbols)
        child2 = apply_mutation(child2, mutation_rate, functions, all_symbols, terminal_symbols)
        next_generation.append(child1)
        next_generation.append(child2)
    return next_generation


def evaluate_next_generation(next_generation, functions, terminals, error_function):
    population = next_generation
    population = [(population[i],
                   error_function(get_callable_expression(functions, terminals, population[i])))
                  for i in range(len(population))]
    return population


def solve(terminals, functions, error_function, numeric_constants=None, iterations=50, max_level=5,
          population_size=500, crossover_rate=0.9, reproduction_rate=0.1, mutation_rate=0, elitism_rate=0):
    all_symbols, terminal_symbols = setup(functions, numeric_constants, terminals)
    population = random_population(population_size, functions, all_symbols, terminal_symbols, terminals, max_level,
                                   error_function)
    best_so_far = get_best_in_generation(population)
    for i in range(iterations):
        next_generation = populate_next_generation(population, elitism_rate, best_so_far, crossover_rate,
                                                   mutation_rate, functions, all_symbols, terminal_symbols)
        population = evaluate_next_generation(next_generation, functions, terminals, error_function)
        best_in_generation = get_best_in_generation(population)
        if best_in_generation[1] < best_so_far[1]:
            best_so_far = best_in_generation
            print(i, best_in_generation[1], best_in_generation[0])
    return best_so_far
