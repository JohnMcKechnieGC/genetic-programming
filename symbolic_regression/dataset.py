from random import random


def get_data_points(n=100):
    data_points = []
    for _ in range(n):
        x = (random() - 0.5) * 2  # -0.5 (inc) to 0.5 (ex)
        y = x ** 5 + x ** 4 + x ** 3 + x ** 1 + x
        data_points.append((x, y))
    return data_points
