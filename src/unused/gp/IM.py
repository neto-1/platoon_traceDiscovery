from copy import deepcopy


class IM:
    def __init__(self, matrix, penalty=None):
        self.matrix = deepcopy(matrix)
        self.dimension = len(matrix)
        self.verify()
        if penalty is None:
            self.penalty = -len(matrix)
        else:
            self.penalty = penalty
        self.matrix_with_penalty = None

    def get_matrix_copy(self):
        return deepcopy(self.matrix)

    def get(self, i, j):
        return self.matrix[i][j]

    def get_matrix_copy_with_penalty(self):
        if self.matrix_with_penalty is not None:
            return self.matrix_with_penalty
        matrix = deepcopy(self.matrix)
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                if i != j and matrix[i][j] == 0:
                    matrix[i][j] = self.penalty
        self.matrix_with_penalty = matrix
        return matrix

    def get_with_penalty(self, i, j):
        if self.matrix_with_penalty is None:
            self.get_matrix_copy_with_penalty()
        return self.matrix_with_penalty[i][j]

    def get_dimension(self):
        return self.dimension

    def verify(self):
        for i in range(len(self.matrix)):
            if self.dimension != len(self.matrix[i]):
                raise ValueError("Matrix dimension is inconsistent: " + str(self.matrix))
            for j in range(self.dimension):
                if self.matrix[i][j] < 0:
                    raise ValueError("Negative values in class IncentiveMatrix: " + str(self.matrix))
            for j in range(i+1, self.dimension):
                if self.matrix[i][j] != self.matrix[j][i]:
                    raise ValueError("Matrix is not symmetric: " + str(self.matrix))

    def delete_edge(self, i, j):
        self.matrix[i][j] = 0
        self.matrix[j][i] = 0
        if self.matrix_with_penalty is not None:
            self.matrix_with_penalty[i][j] = self.penalty
            self.matrix_with_penalty[j][i] = self.penalty
