from unittest import TestCase
from genetic_programming.basic_maths_functions import \
    add, subtract, multiply, protected_divide, sine, cosine, protected_power, protected_log
from gp import mutate, crossover, get_subtree, replace_subtree

from koza_symbolic_regression import get_data_points, mean_absolute_error, x_val
from gp import get_callable_expression


class TestMutation(TestCase):
    def setUp(self):
        self.functions = {'+': add, '-': subtract, '*': multiply, '%': protected_divide, 'sin': sine, 'cos': cosine,
                          'pow': protected_power, 'log': protected_log}
        self.all_symbols = ['+', '-', '*', '%', 'sin', 'cos', 'pow', 'log', 'x', 1, 2, 3, 4, 5]
        self.terminal_symbols = ['x', 1, 2, 3, 4, 5]

    def test_mutate_root_node(self):
        expression = ('+', 2, 1)
        target = [0]
        replacement = ('%', ('%', 'x', 1), ('log', 2, 5))
        expected_result = ('%', ('%', 'x', 1), ('log', 2, 5))
        result = mutate(expression,
                        target,
                        self.functions,
                        self.all_symbols,
                        self.terminal_symbols,
                        replacement=replacement)
        self.assertEquals(expected_result, result)

    def test_mutate_deep_node(self):
        expression = ('%', ('sin', ('pow', ('+', 'x', ('sin', 4)), 2)), ('-', 'x', 2))
        target = [0, 0, 0, 0, 1, 0]
        replacement = 1
        expected_result = ('%', ('sin', ('pow', ('+', 'x', ('sin', 1)), 2)), ('-', 'x', 2))
        result = mutate(expression,
                        target,
                        self.functions,
                        self.all_symbols,
                        self.terminal_symbols,
                        replacement=replacement)
        self.assertEquals(expected_result, result)

    def test_mutate_intermediate_node(self):
        expression = ('+', 'x', ('sin', 4))
        target = [0, 1, 0]
        replacement = 1
        expected_result = ('+', 'x', ('sin', 1))
        result = mutate(expression,
                        target,
                        self.functions,
                        self.all_symbols,
                        self.terminal_symbols,
                        replacement=replacement)
        self.assertEquals(expected_result, result)


class TestCrossover(TestCase):
    def setUp(self):
        self.expression1 = ('-', ('pow', ('log', 3, ('*', 2, 1)), 5), ('log', 'x', ('pow', ('*', 'x', 'x'), 'x')))
        self.target1 = [0, 1, 1, 0]
        # ('-',
        #   ('pow', ('log', 3, ('*', 2, 1)), 5),
        #   ('log',
        #       'x',
        #       ('pow',
        #           ('*', 'x', 'x'),  <-- target1
        #           'x')))
        self.expression2 = ('+', ('%', ('%', ('log', 4, 2), ('-', 2, 2)), 4), 1)
        self.target2 = [0, 0, 0, 1, 0]
        # ('+',
        #   ('%',
        #       ('%',
        #           ('log', 4, 2)
        #           ('-',
        #               2,  <-- target2
        #               2)),
        #       4),
        #   1)

    def test_replace_subtree(self):
        replacement = 2
        result = replace_subtree(self.expression1, self.target1, replacement)
        expected_result = ('-', ('pow', ('log', 3, ('*', 2, 1)), 5), ('log', 'x', ('pow', 2, 'x')))
        self.assertEquals(expected_result, result)

    def test_get_deep_subtree(self):
        result = get_subtree(self.expression1, self.target1)
        expected_result = ('*', 'x', 'x')
        self.assertEquals(expected_result, result)

    def test_get_root_subtree(self):
        expression = ('*', 'x', 'x')
        result = get_subtree(expression, [0])
        expected_result = ('*', 'x', 'x')
        self.assertEquals(expected_result, result)

    def test_crossover(self):
        child = crossover(self.expression1, self.expression2, [], target1=self.target1, target2=self.target2)
        expected_child = ('-', ('pow', ('log', 3, ('*', 2, 1)), 5), ('log', 'x', ('pow', 2, 'x')))
        self.assertEquals(expected_child, child)


class TestEvaluation(TestCase):
    def test_evaluation_function(self):
        training_data = get_data_points(n=20)
        # numeric_constant_terminals = [1, 2, 3, 4, 5]
        error_function = mean_absolute_error([point for point in training_data])
        x2 = ('*', 'x', 'x')
        x3 = ('*', 'x', x2)
        x4 = ('*', 'x', x3)
        x2_plus = ('+', x2, 'x')
        x3_plus = ('+', x3, x2_plus)
        x4_plus = ('+', x4, x3_plus)
        terminals = {'x': x_val}
        functions = {'+': add, '*': multiply}

        func = get_callable_expression(functions, terminals, x4_plus)
        error = error_function(func)
        self.assertAlmostEquals(error, 0.0)
