from unittest import TestCase
from genetic_programming.callables.basic_maths import \
    add, subtract, multiply, protected_divide, sine, cosine, protected_power, protected_log
from gp import mutate, crossover, get_subtree, replace_subtree


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
        c1, c2 = crossover(self.expression1, self.expression2, target1=self.target1, target2=self.target2)
        expected_c1 = ('-', ('pow', ('log', 3, ('*', 2, 1)), 5), ('log', 'x', ('pow', 2, 'x')))
        expected_c2 = ('+', ('%', ('%', ('log', 4, 2), ('-', ('*', 'x', 'x'), 2)), 4), 1)
        self.assertEquals(expected_c1, c1)
        self.assertEquals(expected_c2, c2)
