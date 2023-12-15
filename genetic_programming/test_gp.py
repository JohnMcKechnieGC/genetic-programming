from unittest import TestCase
from genetic_programming.callables.basic_maths import \
    add, subtract, multiply, protected_divide, sine, cosine, protected_power, protected_log
from gp import mutate


class Test(TestCase):
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
