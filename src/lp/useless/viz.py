import networkx as nx
import matplotlib.pyplot as plt



G = nx.Graph()

G.add_node('Hamburg', pos=(53.5672, 10.0285))
G.add_node('Berlin', pos=(52.51704, 13.38792))

nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True, node_size=0)

plt.show()