import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import datasets
import matplotlib.pyplot as plt
from tqdm import tqdm
import utils


class Layer:

    def __init__(self,
                 _input,
                 n_neurons,
                 activation_f):
        self.input = _input
        self.n_neurons = n_neurons
        self.activation_f = activation_f
        self.memory = {}
        self.n_features = _input.shape[1]
        self.n_samples = _input.shape[0]
        self.weights = np.random.uniform(low=-1, high=1, size=(self.n_features, self.n_neurons))
        self.bias = np.zeros(self.n_neurons)
        self.learning_rate = 0

    def __add__(self, other: dict):
        return Layer(
            self.forward(self.input),
            other['neurons'],
            other['activation_f'])

    def forward(self, x):
        self.input = x
        self.memory['Z'] = np.dot(self.input, self.weights) + self.bias
        self.memory['Activation'] = self.activation_f(self.memory['Z'])

        return self.memory['Activation']

    def backward(self, previous_derivative, req_delta=False):
        da_dz = self.activation_f(self.memory['Z'], derivative=True)
        w_grad = np.dot(self.input.T, previous_derivative * da_dz)
        b_grad = np.sum(previous_derivative * da_dz, axis=0)
        self.weights += -self.learning_rate * w_grad
        self.bias += -self.learning_rate * b_grad

        return np.dot(previous_derivative * da_dz, self.weights.T) if req_delta else None


class NeuralNetwork:

    def __init__(self, layers, x_train, x_test, y_train, y_test):
        self.X_train = x_train
        self.X_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.loss_history = []
        self.layers = self.clean(layers)

    def train(self, epochs, learning_rate):
        """
        'main' function of neural network.
        Cleaning layers, making prediction, calculating loss, getting loss derivative and then back propagating.
        Weights and biases are being updated on Layer level.
        Doing this 'epoch' times. You can set specific learning rate.
        """
        self.set_lr(learning_rate, self.layers)

        for _ in tqdm(range(epochs), desc="Training progress: "):
            prediction = self.propagation(0, False)
            temp_loss = utils.loss(prediction, self.y_train, self.X_train.shape[0])
            self.loss_history.append(temp_loss)
            loss_derivative = utils.loss_derivative(self.y_train, prediction)
            self.backpropagation(loss_derivative)

    @staticmethod
    def set_lr(alpha, layers):
        """
        Static method for setting learning rate for all layers.
        """
        for layer in layers:
            layer.learning_rate = alpha

        return layers

    def backpropagation(self, tmp_derivative):
        """
        Backpropagation through every layer.
        """
        for idx in range(len(self.layers) - 1, -1, -1):
            tmp_derivative = self.layers[idx].backward(tmp_derivative, idx != 0)

    def propagation(self, x_test, test=False):
        """
        Forward propagation through every layer.
        """
        if test:
            self.layers[0].input = x_test
        for index in range(len(self.layers) - 1):
            if index == 0:
                self.layers[0].forward(self.layers[0].input)
            tmp_hat = self.layers[index + 1].forward(self.layers[index].memory['Activation'])

        return tmp_hat

    def clean(self, layers):
        """
        Method used to help set layers, extracting data from dictionary to a format suitable for use.

        tmp = Layer(self.X_train, layers[0]['neurons'], layers[0]['activation_f'])
        layers_out = [tmp]

        for index in range(len(layers) - 1):
            layers_out.append(tmp.__add__(layers[index+1]))
            tmp = layers_out[-1]

        return layers_out
        """

        return [Layer(layers['neurons'], layers['activation_f']) for layer in layers]

    def predict(self, x_test, y_test):
        y_predicted = np.argmax(self.propagation(x_test, test=True), axis=1)
        print(f'Predicted values: {y_predicted}')
        print(f'Actual values:    {y_test}')
        return utils.accuracy(y_predicted, y_test)

    def plot_loss(self):
        """
        Simple plotting.
        """
        for loss in self.loss_history[0:-1:5]:
            print(f'Loss value: {loss:.5f}')

        plt.plot(self.loss_history, c='orange')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.show()


ldr = utils.DatasetLoader(dataset=datasets.load_iris(), multiclass_flag=True)
multiclass, X, y = ldr.run()
X_train, X_test, Y_train, Y_test = train_test_split(X, y, test_size=0.2, random_state=1234)

layers_in = [
            {'neurons': 64, 'activation_f': utils.relu},
            {'neurons': 32, 'activation_f': utils.tanh},
            {'neurons': 16, 'activation_f': utils.tanh},
            {'neurons': 3, 'activation_f': utils.softmax}
            ]

nn = NeuralNetwork(layers_in, X_train, X_test, Y_train, Y_test)
nn.train(epochs=500, learning_rate=0.00001)
print(f'Accuracy score: {nn.predict(X_test, Y_test)}')
nn.plot_loss()

