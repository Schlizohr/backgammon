import json
import os
from random import shuffle, sample

import pyro
import pyro.distributions as dist
import torch
import torch.nn as nn
from pyro.infer import SVI, Trace_ELBO, Predictive
from pyro.infer.autoguide import AutoDiagonalNormal
from pyro.nn import PyroModule, PyroSample
from tqdm.auto import trange, tqdm

from mapper import TrainingsData


class NeuralNetwork(PyroModule):
    def __init__(self, input_nodes=198, hidden_nodes=50):
        print("init neural network")
        super().__init__()
        self.input_features = input_nodes
        self.fc1 = PyroModule[nn.Linear](input_nodes, hidden_nodes)
        self.fc1.weight = PyroSample(dist.Normal(0., 1.).expand([hidden_nodes, input_nodes]).to_event(2))
        self.fc1.bias = PyroSample(dist.Normal(0., 1.).expand([hidden_nodes]).to_event(1))
        self.fc2 = PyroModule[nn.Linear](hidden_nodes, 1)
        self.fc2.weight = PyroSample(dist.Normal(0., 1.).expand([1, hidden_nodes]).to_event(2))
        self.fc2.bias = PyroSample(dist.Normal(0., 1.).expand([1]).to_event(1))
        self.relu = nn.ReLU()

    def forward(self, x, y=None):
        x = self.relu(self.fc1(x))
        mu = self.fc2(x).squeeze(-1)
        sigma = pyro.sample("sigma", dist.Uniform(0., 1.))
        with pyro.plate("data", x.shape[0]):
            obs = pyro.sample("obs", dist.Normal(mu, sigma), obs=y)
        return mu


class Evaluator:
    def __init__(self, data: [TrainingsData], split=True, model=NeuralNetwork()):
        print("setup evaluator")
        self.data = data
        shuffle(self.data)
        self.trainings_data = self.data
        self.isSplit = split
        if split:
            half_size = int(len(self.data) / 2)
            self.trainings_data = self.data[:half_size]
            self.test_data = self.data[half_size:]
            self.boards_test_data, self.winners_test_data = self.__init_data(self.test_data)

        self.boards_trainings_data, self.winners_trainings_data = self.__init_data(self.trainings_data)

        self.set_model_and_guide(model, load=False)

        self.latest_means = []
        self.latest_stds = []
        self.latest_data = []

    def set_model_and_guide(self, model, load=False):
        if load:
            self.model = model
            self.load_model_and_guide()
        else:
            self.model = model
            self.guide = self.__init_guide()

            self.save_model_and_guide(self.model, self.guide)

    def __init_guide(self):
        print("setup guide")
        guide = AutoDiagonalNormal(
            self.model)  # automatic guide generation http://docs.pyro.ai/en/0.2.1-release/contrib.autoguide.html

        optimizer = pyro.optim.Adam({"lr": 1e-2})  # optimiser for stochastic optimization, use default parameters

        svi = SVI(self.model, guide, optimizer, loss=Trace_ELBO())  # Stochastic Variational Inference

        pyro.clear_param_store()
        [svi.step(self.boards_trainings_data, self.winners_trainings_data) for i in trange(1000)]
        guide.requires_grad_(False)
        return guide

    def save_model_and_guide(self, model, guide):
        torch.save({"model": model.state_dict(), "guide": guide}, "model/backgammon_model.pt")
        pyro.get_param_store().save("model/backgammon_params.pt")

    def load_model_and_guide(self):
        saved_model_dict = torch.load("model/backgammon_model.pt")
        self.model.load_state_dict(saved_model_dict['model'])
        self.guide = saved_model_dict['guide']
        pyro.get_param_store().load("model/backgammon_params.pt")

    @staticmethod
    def __init_data(data: [TrainingsData]):
        print("init data")
        boards = []
        winners = []
        for test_data in data:
            boards.append(test_data.board)
            winners.append(test_data.winner)
        return torch.tensor(boards), torch.tensor(winners)

    def predict(self, data=None):
        self.latest_data = data
        print("evaluate model")
        predictor = Predictive(self.model, guide=self.guide, num_samples=5000)
        # print("predictor", predictor)

        if data is None:
            data = self.boards_test_data

        prediction = predictor(data)
        # print("prediction", prediction)

        self.latest_means = prediction['obs'].T.detach().numpy().mean(axis=1)
        self.latest_stds = prediction['obs'].T.detach().numpy().std(axis=1)

        # print("mean", self.latest_means)
        # print("std", self.latest_stds)

        return self.latest_means


def load_trainings_data(n=-1):
    directory = "protocol/trainingsboards/"
    files = os.listdir(directory)
    if n != -1:
        files = sample(files, n)

    trainings_data = []

    for filename in tqdm(files):
        path = os.path.join(directory, filename)
        # print("Opening:"+path)
        with open(path, "r") as fp:
            data: str = json.load(fp, object_hook=lambda d: TrainingsData(**d))
            data: [TrainingsData] = json.loads(data, object_hook=lambda d: TrainingsData(**d))
            trainings_data.extend(data)

    return trainings_data


class AI():
    def __init__(self):
        print("being init AI")
        data = load_trainings_data()
        self.ai = Evaluator(data, False)
        print("finished int ai")

    def predict(self, data: []):
        return self.ai.predict(torch.tensor(data)).tolist()
