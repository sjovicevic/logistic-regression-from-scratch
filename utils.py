import numpy as np


class DatasetLoader:
    def __init__(self, dataset, multiclass_flag=False):
        self.dataset = dataset
        self.multiclass_flag = multiclass_flag

    def run(self):
        return self.multiclass_flag, self.dataset.data, self.dataset.target


def softmax(z):
    return np.exp(z) / np.sum(np.exp(z), axis=1, keepdims=True)


def relu(z, derivative=False):
    if derivative:
        z = np.where(z < 0, 0, z)
        z = np.where(z >= 0, 1, z)
        return z
    return np.maximum(0, z)


def sigmoid(z, derivative=False):
    if derivative:
        return (np.exp(-z)) / ((np.exp(-z) + 1) ** 2)
    return 1 / (1 - np.exp(-z))


def accuracy(y_p, y_t):
    return np.sum(y_p == y_t) / len(y_t)
