from InitCPP import InitCPP
import random


class RandomCPP(InitCPP):
    matrix = None

    def __init__(self, matrix):
        self.matrix = matrix

    def find_initial_solution(self):
        x = [random.randrange(self.matrix.get_dimension()) for i in range((self.matrix.get_dimension()))]

        return x
