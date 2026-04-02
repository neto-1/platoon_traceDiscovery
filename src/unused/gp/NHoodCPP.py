from pandas import *
import random
from scipy import special
from collections import Counter
import copy

"""Clique Solver Class
Maximum diverse grouping problem
"""

__author__ = """ Dietrich Steinmetz, Felix Merz """


class NHoodCPP:
    """Clique Solver Class"""

    """ Multiple Execution
        Factory Pattern
    """
    def __init__(self, matrix):
        self.matrix = matrix


    """Insert node to group"""
    def LSInsert(self, x, sc, f):
        for i in range(len(x)):
            for g in range(len(x)):
                if x[i] != g:
                    """ 
                        sc[i][g] edge costs to the potentially new group(g)
                        sc[i][x[i]] edge costs to the current group(x[i])
                        df = node i in potentially new group(cost of edges of i node in new group) - node i in current group(cost of edges of i node in current group)
                    """
                    df = sc[i][g] - sc[i][x[i]]

                    # df > 0 maximizing of cost
                    if df > 0:
                        for j in range(len(x)):
                             sc[j][x[i]] -= self.matrix.get_with_penalty(j, i)
                             sc[j][g] += self.matrix.get_with_penalty(j, i)
                        x[i] = g

                        # UPDATE sc
                        # sc = self.calcSC(x)

                        # update objective function value, old ofv + delta
                        f = f + df
        return x, sc, f

    """Swap two nodes from different groups"""
    def LSSwap(self, x, sc, f):
        # try to swap all pairs
        for i in range(len(x)):
            for j in range(i):
                if str(x[j]) != str(x[i]):
                    
                    # sc[2][0] importance of node 2 to group 0
                    # delta function
                    df = sc[i][x[j]] + sc[j][x[i]] - sc[i][x[i]] - sc[j][x[j]] - 2 * self.matrix.get_with_penalty(i, j)

                    # swap nodes i,j iff the swapped solution improve the function value
                    if df > 0:
                        # swap nodes i and j
                        self.swap(x, i, j)

                        # UPDATE sc
                        sc = self.calcSC(x)

                        # update objective function value, old ofv + delta
                        f = f + df

        return x, sc, f;

    """Variable neighborhood descent"""
    def VND(self, x, sc, f):
        # function values
        f_v = []

        # do-while
        max_f = f-1

        while f > max_f:
            while f > max_f:
                max_f = f
                x, sc, f = self.LSInsert(x, sc, f)
                #print "Insert: " + str(f)
                f_v.append(f)
            x, sc, f = self.LSSwap(x, sc, f)
            #print "Swap: " + str(f)
            f_v.append(f)

        # while f > max_f:
        #     max_f = f
        #     x, sc, f = self.LSInsert(x, sc, f)
        #     print "Insert: " + str(f)
        #     f_v.append(f)
        # x, sc, f = self.LSSwap(x, sc, f)
        # print "Swap: " + str(f)
        # f_v.append(f)

        return x, sc, f, f_v

    """Skewed General Variable Neighborhood Search"""
    def SGVNS(self, x_c, alpha, k_min, k_max, k_step):
        # verify initial solution
        self.verify(x_c)

        # nodes X groups matrix
        # update sc_c, f_c
        sc_c = self.calcSC(x_c)
        f_c = self.calcF(x_c)

        # track local maximum solutions
        local_max = []
        local_max_f = []
        function_value = []

        # 1 VND
        x_c, sc_c, f_c, f_v = self.VND(x_c, sc_c, f_c)
        function_value = function_value + f_v

        # 1 storing of local maximum solution after VND execution
        local_max.append(x_c)
        local_max_f.append(f_c)

        # current solution is a best solution
        # (x_b, sc_b, f_b) = (x_c, sc_c, f_c)
        # explicit copy of lists
        x_b = copy.copy(x_c)
        sc_b = copy.copy(sc_c)
        f_b = f_c

        # k_best = [[0 for g in range(len(x))] for i in range(len(x))]
        k_best = []
        k_best.append([x_b, f_b])
        iteration = 20
        while iteration > 0:
            # (x_n, sc_n, f_n) = (x_c, sc_c, f_c)
            # explicit copy of lists
            x_n = copy.copy(x_c)
            sc_n = copy.copy(sc_c)
            f_n = f_c

            # Shake new solution
            x_n, sc_n, f_n = self.shake(10, x_n, sc_n, f_n)

            # 2 VND
            x_n, sc_n, f_n, f_v = self.VND(x_n, sc_n, f_n)
            # 2 storing of local maximum solution after VND execution
            local_max.append(x_c)
            local_max_f.append(f_c)
            function_value = function_value + f_v

            # compare a distance between shaken(_n) and current(_c) solution
            if (f_n + alpha * NHoodCPP.d(x_n, x_c) * abs(f_c) > f_c) and (f_n + alpha * NHoodCPP.d(x_n, x_b) * abs(f_b) > f_b):
                # (x_c, sc_c, f_c) = (x_n, sc_n, f_n)
                # explicit copy of lists
                x_c = copy.copy(x_n)
                sc_c = copy.copy(sc_n)
                f_c = f_n

                e = 0.000001
                if f_c > f_b + e:
                    # (x_b, sc_b, f_b) = (x_c, sc_c, f_c)
                    # explicit copy of lists
                    x_b = copy.copy(x_c)
                    sc_b = copy.copy(sc_c)
                    f_b = f_c

                    k_best.append([x_b, f_b])

            iteration = iteration - 1
        return x_b, f_b, sc_b, k_best, local_max, local_max_f, function_value

    """Compute distance between solutions x_n and x_b"""
    @staticmethod
    def d(x_n, x_b):

        c_b = (Counter(x_n).items())
        sum_g = sum(special.binom(c_b[i][1], 2) for i in range(len(Counter(x_n))))
        g_abs = 0

        for j in range(len(x_n)):
            for i in range(j):
                if ((x_b[i] == x_b[j]) and (x_n[i] != x_n[j])) or ((x_b[i] != x_b[j]) and (x_n[i] == x_n[j])):
                    g_abs =+ 1
        try:
            result = g_abs / sum_g
        except ValueError:
            print "No group can be found, all vehicles drive alone"

        return result

    """Shake give solution k times"""
    def shake(self, k, x, sc, f):
        # Repeat shake k-times
        while k > 0:
            # Choose two random nodes
            (i, j) = (random.randrange(0, len(x), 1),  random.randrange(0, len(x), 1))
            # Stop shake for one group
            if len(Counter(x)) <= 1:
                return x, sc, f
            # Swap two random nodes from different groups
            if x[i] != x[j]:
                self.swap(x, i, j)
                k = k - 1
        # UPDATE sc, f
        sc = self.calcSC(x)
        f = self.calcF(x)

        return x, sc, f

    """Swap elements i and j"""
    def swap(self, x, i, j):
        g1 = x[i]
        x[i] = x[j]
        x[j] = g1
        return x

    """SC calculations"""
    def calcSC(self, x):
        # sc matrix computation Number of Groups g X Number of Nodes
        sc = [[0 for g in range(len(x))] for i in range(len(x))]
        """ 
            i nodes
            g groups
        """
        for i in range(len(x)):
            for g in range(len(x)):
                # how important node i for group g, j represents all nodes of group g
                sc[i][g] = sum(self.matrix.get_with_penalty(i, j) for j in range(len(x)) if x[j] == g)
        return sc

    """Calculations of objective value of solution x"""
    def calcF(self, x):
        f = 0
        for i in range(len(x)):
            for j in range(i+1, len(x)):
                if x[i] == x[j]:
                    f += self.matrix.get_with_penalty(i, j)
        return f

    def verify(self, x):
        if self.matrix.get_dimension() != len(x):
            raise ValueError("Wrong dimension of solution: " + str(x))
        if max(x) >= len(x):
            raise ValueError("Inconsistent solution: " + str(x))

