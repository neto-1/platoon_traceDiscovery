from InitCPP import InitCPP


class TrivialCPP(InitCPP):
    matrix = None

    def __init__(self, matrix):
        self.matrix = matrix

    def find_initial_solution(self):
        x = [i for i in range((self.matrix.get_dimension()))]
        return x
