try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx
from NHoodCPP import NHoodCPP

class SolutionGraph:
    def __init__(self, solutions, solver):
        self.solver = solver
        self.solutions = solutions

    def graph_constuction(self):
        G = nx.Graph()

        for i in range(len(self.solutions)-1):
            for j in range(i, len(self.solutions)):
                if i != j:
                    print(i, j)
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

        plt.axis('off')
        plt.savefig("weighted_graph.png")  # save as png
        plt.show()  # display

