from igraph import *
from copy import deepcopy
from InitCPP import InitCPP


class GreedyCPP(InitCPP):
    matrix = None
    """ Multiple Execution
        Factory Pattern
    """
    def __init__(self, matrix):
        self.matrix = deepcopy(matrix)

    def find_initial_solution(self):
        """ Define trivial cliques """
        x = [i for i in range(self.matrix.get_dimension())]

        """ Greedy Approach to determine Weighted Disjoint Cliques 
            Result returns vector x 
        """

        g = Graph()
        # while do construct
        has_cliques = True
        while has_cliques:
            # Update graph
            g = g.Weighted_Adjacency(self.matrix.get_matrix_copy(), mode=ADJ_UNDIRECTED, attr="weight", loops=False)

            # Maximal cliques by Bron Kerbosch Algorithm
            m_cliques = g.maximal_cliques(min=2, max=0)

            if len(m_cliques) > 0:
                q_b = Graph.subgraph(g, m_cliques[0])
                best_clique = m_cliques[0]

                # Determine maximal weighted clique
                for q in range(1, len(m_cliques)):
                    q_c = Graph.subgraph(g, m_cliques[q])
                    if sum(q_c.es["weight"]) > sum(q_b.es["weight"]):
                        q_b = q_c
                        best_clique = m_cliques[q]

                # Produce unused group index
                groupidx = max(x) + 1
                for i in range(len(best_clique)):

                    # Assign clique nodes to one group
                    x[best_clique[i]] = groupidx

                    # Delete neighbour edges of clique nodes
                    for j in range(self.matrix.get_dimension()):
                        self.matrix.delete_edge(best_clique[i], j)
            else:
                has_cliques = False

        # normalize group indexes
        new_group_ids = {}
        group_num = 0
        for i in range(len(x)):
            if x[i] not in new_group_ids:
                new_group_ids[x[i]] = group_num
                group_num += 1

        for i in range(len(x)):
            x[i] = new_group_ids[x[i]]

        return x
