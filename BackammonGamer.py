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


class NeuralNetwork2(PyroModule):
    def __init__(self, input_nodes=198, hidden_nodes=50):
        print("init neural network")
        super().__init__()
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
        sigma = pyro.sample("sigma", dist.Uniform(0., 0.1))
        with pyro.plate("data", x.shape[0]):
            obs = pyro.sample("obs", dist.Normal(mu, sigma), obs=y)
        return mu


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
        sigma = pyro.sample("sigma", dist.Uniform(0., 0.1))
        with pyro.plate("data", x.shape[0]):
            obs = pyro.sample("obs", dist.Normal(mu, sigma), obs=y)
        return mu


class Evaluator:
    def __init__(self):
        print("setup evaluator")
        self.data = None
        self.isSplit = None
        self.trainings_data = None
        self.test_data = None
        self.boards_test_data = None
        self.winners_test_data = None
        self.boards_trainings_data = None
        self.winners_trainings_data = None
        self.guide = None
        self.model = None

        self.latest_means = []
        self.latest_stds = []
        self.latest_data = []

    def create(self, split=True, model=NeuralNetwork(), load=False, guide=None, n=-1):
        self.isSplit = split
        self.model = model
        if load:
            self.load_model_and_guide()
        else:
            if guide is None:
                guide = AutoDiagonalNormal(model)
            self.create_model_and_guide(guide, n)

    def create_model_and_guide(self, guide, n=-1):

        self.data = load_trainings_data(n)
        shuffle(self.data)
        self.trainings_data = self.data
        if self.isSplit:
            half_size = int(len(self.data) / 2)
            self.trainings_data = self.data[:half_size]
            self.test_data = self.data[half_size:]
            self.boards_test_data, self.winners_test_data = self.__init_data(self.test_data)

        self.boards_trainings_data, self.winners_trainings_data = self.__init_data(self.trainings_data)
        self.guide = self.__init_guide(guide)

        self.save_model_and_guide(self.model, self.guide)

    def __init_guide(self, guide):
        print("setup guide")

        optimizer = pyro.optim.Adam({"lr": 1e-2})  # optimiser for stochastic optimization, use default parameters

        svi = SVI(self.model, guide, optimizer, loss=Trace_ELBO())  # Stochastic Variational Inference

        pyro.clear_param_store()
        [svi.step(self.boards_trainings_data, self.winners_trainings_data) for i in trange(5000)]
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

        self.latest_means = prediction['obs'].T.detach().numpy().mean(axis=1)
        self.latest_stds = prediction['obs'].T.detach().numpy().std(axis=1)

        return self.latest_means


class Analyzing:
    def __init__(self, model, guide=None):
        self.evaluator = Evaluator()
        self.evaluator.create(model=model, guide=guide)
        self.evaluator.predict()

    def analyzing(self):
        means = self.evaluator.latest_means.tolist()
        stds = self.evaluator.latest_stds.tolist()

        min_mean = min(means)
        avg_mean = sum(means) / len(means)
        max_mean = max(means)

        print("mean min", min_mean)
        print("mean avg", avg_mean)
        print("mean max", max_mean)

        min_std = min(stds)
        avg_std = sum(stds) / len(stds)
        max_std = max(stds)

        print("std min", min_std)
        print("std avg", avg_std)
        print("std max", max_std)

        error = []
        for w, m in zip(self.evaluator.winners_test_data, means):
            if w == 0:
                error.append(m)
            else:
                error.append(1 - m)

        min_error = min(error)
        avg_error = sum(error) / len(error)
        max_error = max(error)

        print("error min", min_error)
        print("error avg", avg_error)
        print("error max", max_error)


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
        self.ai = Evaluator()
        self.ai.create(split=False, load=True)
        print("finished int ai")

    def predict(self, data: []):
        return self.ai.predict(torch.tensor(data)).tolist()
