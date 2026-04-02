import matplotlib.pyplot as plt
import networkx as nx

from util.databasecontainer import DatabaseContainer


# from util.databasecontainer import DatabaseContainer

def main():
    DatabaseContainer.launch("germany", db_output_flag=False)
    from algorithms.grouping.database import Database

    vehicles = Database.get_vehicles_new(1884006)
    incentives = Database.get_incentives_new(1884006)

    G = nx.Graph()

    edge_tuple = []
    for incentive in incentives:
        v1 = incentive[0]
        v2 = incentive[1]
        ic = incentive[2]

        print(v1, ic, v2)

        edge_tuple.append((v1, v2, round(ic, 3)))

    G.add_weighted_edges_from(edge_tuple)

    draw_graph(G)

    # i_m = Database.get_incentive_matrix(1884006, 0.001, 0)
    # matrix = i_m.get_matrix_copy_with_penalty()
    # print(matrix)


def draw_graph(G):
    pos = nx.random_layout(G)  # positions for all nodes

    print(pos)

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=300)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=1)
    # nx.draw_networkx_edges(G, pos, edgelist=esmall,
    #                       width=6, alpha=0.5, edge_color='b', style='dashed')

    # labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # plt.axis('off')
    # plt.savefig("weighted_graph.png")  # save as png
    plt.show()  # display


class SolutionGraph:
    def __init__(self, solutions, solver):
        self.solver = solver
        self.solutions = solutions

    def graph_constuction(self):
        G = nx.Graph()

        for i in range(len(self.solutions) - 1):
            for j in range(i, len(self.solutions)):
                if i != j:
                    # print(i, j)
                    print(self.solutions[i], self.solutions[j])
                    G.add_edge(str(i), str(j), weight=self.solver.d(self.solutions[i], self.solutions[j]))

        pos = nx.spring_layout(G)  # positions for all nodes

        # nodes
        nx.draw_networkx_nodes(G, pos, node_size=700)

        # edges
        nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=1)
        # nx.draw_networkx_edges(G, pos, edgelist=esmall,
        #                       width=6, alpha=0.5, edge_color='b', style='dashed')

        # labels
        nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
        labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

        # plt.axis('off')
        # plt.savefig("weighted_graph.png")  # save as png
        # plt.show()  # display


if __name__ == "__main__":
    main()
