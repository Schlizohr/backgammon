import itertools
import json
from random import shuffle

import pyro
import pyro.distributions as dist
import torch
import torch.nn as nn
from pyro.infer import SVI, Trace_ELBO, Predictive
from pyro.infer.autoguide import AutoDiagonalNormal
from pyro.nn import PyroModule, PyroSample

from Backgammon import Board, Field, Checker
from helper.Trainingsdata import load_trainings_data


class TrainingsData:

    def __init__(self, board: [float], winner: int):
        """
        :param board: At the bginning for each field in board 8 vales. first 4 for white second 4 for black.
                    The first one is set to 1 if at least on checker is on this field. second is set if at least 2 checkers are present
                    the third for three checkers and the 4 is count/ of checkers if more then 3.

                    Then the which players move it is currently.
                    Then the number of checkers on the bar for both players
                    finally the number of checkers each player has already removed form the board.
        :param winner: who wins the game. 1 if white wins 0 if black wins
        :type int
        """
        self.board: [int] = board
        self.winner: int = winner


class NNMapper:
    @staticmethod
    def json_to_trainings_data(s: str):
        data = json.loads(s)
        return TrainingsData(data["board"], data["winner"])

    def to_trainings_data(self, board: Board, next_player: Checker, winner: Checker) -> TrainingsData:
        return TrainingsData(self.to_nodes(board, next_player), self.winner(winner))

    def to_nodes(self, board: Board, next_player: Checker) -> []:
        node_values = []
        for i in range(1, len(board.board)):
            node_values.extend(self.field_to_nodes(board.board[i]))
        node_values.extend(self.players(next_player))
        node_values.extend(self.checkers_on_bar(board))
        node_values.extend(self.removed_checkers(board))

        return list(itertools.chain(*node_values))

    def field_to_nodes(self, field: Field) -> [[], []]:
        content = field.content
        if len(content) == 0:
            return [[0, 0, 0, 0], [0, 0, 0, 0]]
        if content[0] == Checker.WHITE:
            return [self.content_to_nodes(content), [0, 0, 0, 0]]
        if content[0] == Checker.BLACK:
            return [[0, 0, 0, 0], self.content_to_nodes(content)]

    @staticmethod
    def content_to_nodes(content: [Checker]) -> []:
        node_values = [0, 0, 0, 0]

        if len(content) >= 1:
            node_values[0] = 1
        if len(content) >= 2:
            node_values[1] = 1
        if len(content) >= 3:
            node_values[2] = 1
        if len(content) >= 4:
            node_values[3] = (len(content) - 3) / 2

        return node_values

    def removed_checkers(self, board: Board) -> [[], []]:
        return [
            [self.removed_checkers_for_color(board, Checker.WHITE)],
            [self.removed_checkers_for_color(board, Checker.BLACK)]
        ]

    @staticmethod
    def removed_checkers_for_color(board: Board, color) -> int:
        count = 0
        for i in board.get_checkers_position_of(color=color):
            count += len(board.checkers_at_field(i).content)
        return 15 - count

    @staticmethod
    def players(checker: Checker) -> [[], []]:
        if checker == Checker.WHITE:
            return [[1], [0]]
        return [[0], [1]]

    @staticmethod
    def winner(checker: Checker) -> [[], []]:
        winner = 0
        if checker == Checker.WHITE:
            winner = 1
        return winner

    @staticmethod
    def checkers_on_bar(board: Board) -> [[], []]:
        out = board.out
        total_count = len(out)
        white_count = len([x for x in out if x == Checker.WHITE])
        return [[white_count / 2], [(total_count - white_count) / 2]]


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
    def __init__(self, data: [TrainingsData]):
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
        self.model = NeuralNetwork()
        self.guide = self.__init_guide()
        self.latest_means = []
        self.latest_stds = []

    def __init_guide(self):
        print("setup guide")
        guide = AutoDiagonalNormal(
            self.model)  # automatic guide generation http://docs.pyro.ai/en/0.2.1-release/contrib.autoguide.html

        optimizer = pyro.optim.Adam({"lr": 1e-2})  # optimiser for stochastic optimization, use default parameters

        svi = SVI(self.model, guide, optimizer, loss=Trace_ELBO())  # Stochastic Variational Inference

        pyro.clear_param_store()
        [svi.step(self.boards_trainings_data, self.winners_trainings_data) for i in range(5000)]
        pyro.get_param_store().save("model/model_save")
        guide.requires_grad_(False)
        return guide

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
        print("evaluate model")
        predictor = Predictive(self.model, guide=self.guide, num_samples=1000)
        print("predictor", predictor)

        if data is None:
            data = self.boards_test_data

        prediction = predictor(data)
        print("prediction", prediction)

        self.latest_means = prediction['obs'].T.detach().numpy().mean(axis=1)
        self.latest_stds = prediction['obs'].T.detach().numpy().std(axis=1)

        print("mean", self.latest_means)
        print("std", self.latest_stds)


class AI():
    def __init__(self):
        print("being init AI")
        data = load_trainings_data()
        self.ai = Evaluator(data)
        print("finished int ai")

    def predict(self, data):
        return self.ai.predict(data)
