import math


def add(arg1, arg2):
    def callable_add():
        return arg1() + arg2()
    return callable_add


def subtract(arg1, arg2):
    def callable_subtract():
        return arg1() - arg2()
    return callable_subtract


def multiply(arg1, arg2):
    def callable_multiply():
        return arg1() * arg2()
    return callable_multiply


def protected_divide(arg1, arg2):
    def callable_protected_divide():
        try:
            return arg1() / arg2()
        except ZeroDivisionError:
            return 1.0
    return callable_protected_divide


def sine(arg):
    def callable_sine():
        return math.sin(arg())
    return callable_sine


def cosine(arg):
    def callable_cosine():
        return math.cos(arg())
    return callable_cosine


def protected_power(arg1, arg2):
    def callable_protected_power():
        try:
            return math.pow(arg1(), arg2())
        except (ValueError, ZeroDivisionError):
            return 1.0
    return callable_protected_power


def protected_log(arg1, arg2):
    def callable_protected_log():
        try:
            return math.log(arg1(), arg2())
        except (ValueError, ZeroDivisionError):
            return 1.0
    return callable_protected_log
