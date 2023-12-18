import math
import functools


def number(val):
    @functools.wraps(number)
    def number_wrapper():
        return float(val)
    return number_wrapper


def add(arg1, arg2):
    @functools.wraps(add)
    def add_wrapper():
        return arg1() + arg2()
    return add_wrapper


def subtract(arg1, arg2):
    @functools.wraps(subtract)
    def subtract_wrapper():
        return arg1() - arg2()
    return subtract_wrapper


def multiply(arg1, arg2):
    @functools.wraps(multiply)
    def multiply_wrapper():
        return arg1() * arg2()
    return multiply_wrapper


def protected_divide(arg1, arg2):
    @functools.wraps(protected_divide)
    def protected_divide_wrapper():
        try:
            return arg1() / arg2()
        except ZeroDivisionError:
            return 1.0
    return protected_divide_wrapper


def sine(arg):
    @functools.wraps(sine)
    def sine_wrapper():
        try:
            return math.sin(arg())
        except ValueError:
            return 1.0
    return sine_wrapper


def cosine(arg):
    @functools.wraps(cosine)
    def cosine_wrapper():
        try:
            return math.cos(arg())
        except ValueError:
            return 1.0
    return cosine_wrapper


def protected_power(arg1, arg2):
    @functools.wraps(protected_power)
    def protected_power_wrapper():
        try:
            return math.pow(arg1(), arg2())
        except (ValueError, ZeroDivisionError, OverflowError):
            return 1.0
    return protected_power_wrapper


def protected_log(arg):
    @functools.wraps(protected_log)
    def protected_log_wrapper():
        try:
            return math.log(arg())
        except (ValueError, ZeroDivisionError):
            return 1.0
    return protected_log_wrapper


def exp(arg):
    @functools.wraps(exp)
    def exp_wrapper():
        try:
            return math.e ** arg()
        except OverflowError:
            return 1.0
    return exp_wrapper

# TODO: Default value is wrong in some of the protected functions. Research and fix.
