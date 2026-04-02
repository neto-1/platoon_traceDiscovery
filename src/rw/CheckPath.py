from igraph import *
from py2neo import Graph as pGraph

road_point_label = "RoadPoint"
road_segment_name = "ROAD_SEGMENT"

i_graph = Graph(1)

graph = pGraph("http://neo4j:12345678@localhost:7474/db/data/")


neighbours = graph.run("MATCH (a:" + str(road_point_label) + ")-[r:" + str(road_segment_name) + "]->(b:" + str(
        road_point_label) + ") RETURN id(a), id(b), r.distance_meter").data()

edges = []
for edge in neighbours:
        edges.append([str(edge['id(b)']), str(edge['id(a)']), edge["r.distance_meter"]])

print(edges)
igraph = i_graph.TupleList(edges, False, "name", None, True)

path = igraph.shortest_paths_dijkstra('22', '0', "weight", "ALL")
path_s = igraph.shortest_paths('22', '0', "weight", "ALL")
path_p = igraph.get_shortest_paths(22,to=0,mode=ALL,output='vpath')


print(igraph)
print(path)
print(path_s)
print(path_p)
