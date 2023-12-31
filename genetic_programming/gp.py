from inspect import getfullargspec
from random import choice, randint, random
from genetic_programming.basic_maths_functions import number
from copy import deepcopy
from collections import namedtuple
Solution = namedtuple("Solution", "expression error")


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


def get_random_expression(functions, all_symbols, terminal_symbols, level=1, max_level=3):
    def tree():
        function = functions[symbol]
        arity = len(getfullargspec(function).args)
        result = [symbol]
        result.extend([get_random_expression(functions, all_symbols, terminal_symbols, level + 1, max_level)
                       for _ in range(arity)])
        result = tuple(result)
        return result

    symbol = choice(all_symbols) if level < max_level \
        else choice(terminal_symbols)
    return symbol if symbol in terminal_symbols \
        else tree()


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


def crossover(expression1, expression2, terminal_symbols, max_total_depth=18, target1=None, target2=None):
    def select_crossover_candidate(expression, max_subtree_depth=None, prob_internal=0.9):
        def get_subtree_depth(candidate):
            return max([len(el[1]) for el in target_candidates
                                 if el[1][:len(candidate[1])] == candidate[1]])\
                            - len(candidate[1]) + 1

        target_candidates = flatten(expression)
        if random() <= prob_internal:
            if max_subtree_depth is not None:
                depths = [get_subtree_depth(candidate) for candidate in target_candidates]
                target_candidates = [target_candidates[i] for i in range(len(target_candidates))
                                     if depths[i] <= max_subtree_depth]
            internal_candidates = [candidate for candidate in target_candidates if candidate[0] not in terminal_symbols]
            if len(internal_candidates) > 0:
                target_candidates = internal_candidates
        else:
            target_candidates = [candidate for candidate in target_candidates if candidate[0] in terminal_symbols]
        return choice(target_candidates)[1]

    target1 = select_crossover_candidate(expression1) if target1 is None else target1

    # The mutation operator can still grow tress deeper than max_total_depth,
    # so ensure max_depth of the subtree is positive
    max_depth = max(max_total_depth - len(target1) + 1, 1)

    target2 = select_crossover_candidate(expression2, max_subtree_depth=max_depth) if target2 is None else target2
    subtree = get_subtree(expression2, target2)
    child = replace_subtree(expression1, target1, subtree)
    return child


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


def get_symbols(functions, numeric_constants, terminals):
    function_symbols = list(functions.keys())
    terminal_symbols = list(terminals.keys())
    if numeric_constants is not None:
        terminal_symbols.extend(numeric_constants)
    all_symbols = function_symbols + terminal_symbols
    return all_symbols, terminal_symbols


def solve(terminals, functions, calculate_error, numeric_constants=None, max_iterations=50, max_level=5,
          population_size=500, crossover_rate=0.9, mutation_rate=0.01, using_elitism=False, verbose=True):
    def get_initial_generation():
        expressions = [get_random_expression(functions, all_symbols, terminal_symbols, max_level=max_level)
                       for _ in range(population_size)]
        first_generation = [Solution(expressions[i],
                                     calculate_error(get_callable_expression(functions, terminals, expressions[i])))
                             for i in range(population_size)]
        return first_generation

    def get_next_generation():
        def select_parent(tournament_size=5):
            candidates = [randint(0, len(population) - 1) for _ in range(tournament_size)]
            winner = min(candidates, key=lambda i: population[i].error)
            return population[winner].expression

        def create_child():
            def apply_mutation():
                def get_random_target():
                    nodes = flatten(expression)
                    selected_node = choice(nodes)
                    target = selected_node[1]
                    return target

                expression = select_parent()
                mutation_target = get_random_target()
                return mutate(expression, mutation_target, functions, all_symbols, terminal_symbols)

            def apply_crossover():
                parent1 = select_parent()
                parent2 = select_parent()
                return crossover(parent1, parent2, terminal_symbols)

            r = random()
            if r <= crossover_rate:
                child = apply_crossover()
            elif r <= (crossover_rate + mutation_rate):
                child = apply_mutation()
            else:
                child = deepcopy(select_parent())
            return child

        expressions = [best_so_far] if using_elitism else []
        while len(expressions) < population_size:
            expressions.append(create_child())
        next_generation = evaluate_expressions(expressions)
        return next_generation

    def evaluate_expressions(expressions):
        return [Solution(expressions[i],
                         calculate_error(get_callable_expression(functions, terminals, expressions[i])))
                for i in range(len(expressions))]

    def get_best_solution():
        return min(population, key=lambda solution: solution.error)

    def report(generation):
        if verbose:
            print(generation, best_so_far.error, best_so_far.expression)

    def progress(current, total):
        if not verbose:
            if current > 1:
                print('\b' * total, end='')
            print('#' * current, end='')
            print('.' * (total - current), end='')
            if current == total:
                print('\b' * total, end='')

    all_symbols, terminal_symbols = get_symbols(functions, numeric_constants, terminals)
    population = get_initial_generation()
    best_so_far = get_best_solution()
    report(0)

    for iteration in range(1, max_iterations + 1):
        population = get_next_generation()
        best_in_generation = get_best_solution()
        if best_in_generation.error < best_so_far.error:
            best_so_far = best_in_generation
            report(iteration)
        progress(iteration, max_iterations)
    return best_so_far.expression, best_so_far.error


def solve_random(terminals, functions, calculate_error, numeric_constants=None, iterations=100, max_level=5):
    all_symbols, terminal_symbols = get_symbols(functions, numeric_constants, terminals)

    best_expression = get_random_expression(functions, all_symbols, terminal_symbols, max_level=max_level)
    best_error = calculate_error(get_callable_expression(functions, terminals, best_expression))

    for i in range(iterations):
        new_expression = get_random_expression(functions, all_symbols, terminal_symbols, max_level=max_level)
        callable_expression = get_callable_expression(functions, terminals, new_expression)
        training_set_error = calculate_error(callable_expression)

        if training_set_error < best_error:
            best_error = training_set_error
            best_expression = new_expression
            test_set_error = calculate_error(callable_expression)
            print(i, training_set_error, test_set_error, new_expression)

    return best_error, best_expression

# TODO: max_level applies only to initial random trees, and it's not possible to control the maximum depth
#       from the application.
# TODO: Review the default values of control parameters in Koza GP1 and ensure consistency.
# TODO: Control depth in mutation. Only crossover controlled at the moment.
