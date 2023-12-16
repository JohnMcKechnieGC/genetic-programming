# def mean_absolute_error(f, data):
#     """
#     :param f: a callable expression
#     :param data: a set of (x, y) datapoints
#     :return: the sum of the absolute error of y = f(x) across all datapoints
#     """
#     return sum([abs((point[1] - f(point)())) for point in data]) / len(data)


def get_mean_absolute_error(points):
    def mean_absolute_error(func):
        return sum([abs((point[1] - func(point)())) for point in points]) / len(points)
    return mean_absolute_error
