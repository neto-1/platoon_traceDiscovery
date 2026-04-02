import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client


# this is the lp formulation of the problem and is used to calculate the results
def lp(vehicles, G, s, t, saving):

    # LP
    m = Model("Platooning")
    m.setParam("OutputFlag", False)

    # Assoz. array - dict
    x = {}
    y = {}
    for e in G.edges():
        x[e] = {}
        y[e] = m.addVar(vtype=GRB.BINARY, obj=saving*G[e[0]][e[1]]['c'])
        for h in vehicles:
            x[e][h] = m.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=(1-saving)*G[e[0]][e[1]]['c'])
    m.update()

    for v in G.nodes():
        for h in vehicles:
            if v == s[h]:
                b = 1
            elif v == t[h]:
                b = -1
            else:
                b = 0
            m.addConstr(quicksum(x[e][h] for e in G.out_edges(v)) - quicksum(x[e][h] for e in G.in_edges(v)) == b)

    for e in G.edges():
        for h in vehicles:
            m.addConstr(x[e][h] <= y[e])

    # m.setObj()
    m.optimize()

    #print("status : ", m.getAttr(GRB.Attr.Status))
    #Ausgabe
    p = {}
    eids = {}

    for h in vehicles:
        succ = {}
        succedges = []
        for e in G.edges():
            if x[e][h].X > 0.99:
                succ[e[0]] = e[1]
                succedges.append ( G[e[0]][e[1]]['id'] )
            elif x[e][h].X > 0.01:
                print("ERROR")
                exit(0)
        p[h] = [s[h]]

        eids[h] = succedges

        while p[h][-1] in succ:
            p[h].append(succ[p[h][-1]])

    return m.ObjVal, p, eids

# init the database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="1234567890")

# !!!!! first we need to get all vehicles and their start and end nodes
# formulate the query
query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle),(e:location)-[:END]-(v)-[:START]-(s:location)" \
        "RETURN DISTINCT id(v), id(e), id(s)"
# run the query
results = db.query(query)
# create empty list for vehicles and dictionaries for their start (s) and ending points (e) d
vehicles = []
s = {}
t = {}
# save the id (r[0]) the start (r[2]) and the ending points (r[1]) in the dicts
for r in results:
    vehicles.append(r[0])
    s[r[0]] = r[2]
    t[r[0]] = r[1]

# !!!!! now we need to create a dict of all groups and their vehicles
# make the query to get the information
query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle) RETURN id(g), id(v)"
results = db.query(query)
# create empty dict
groups = {}
# fill up the dict with this for loop
for r in results:
    groupId = r[0]
    vehicleId = r[1]
    # for every "new" group, we add a new key to the dict. if the group already exists we just add the vehicle to the list
    if groupId not in groups:
        groups[groupId] = []
    groups[groupId].append(vehicleId)

# !!!! create some empty dicts for the result and output
# this saves the value of absolute savings of a group
absolute_savings = {}
# in groupInfo the savings, the value of shortest paths and platooning paths, the savings in percent and the ids of the vehicles will be saved
groupInfo = {}
# in platooning_paths the information about the paths (sequence of nodes) is saved
platooning_paths = {}
# in shortest_paths the information of the shortest paths (sequence of nodes) is saved
shortest_paths = {}

# iterate through all groups (in the grid network, there should be only one group
if len(groups) > 0:
    for key, group in groups.items():

        # get the graph from neo4j to
        query = "MATCH (n1:location)-[r:neighbourEdges]->(n2:location) RETURN id(n1), id(n2), r.distance, id(r)"
        results = db.query(query)
        # create a graph for gurobi
        G = nx.DiGraph()
        # add edges to the gurobi model as a connection betweern two nodes (r[0] and r[1]) with costs (c=r[2]) and an id (id=r[3])
        for r in results:
            G.add_edge(r[0], r[1], c=r[2], id=r[3])
            G.add_edge(r[1], r[0], c=r[2], id=r[3])

        # this calculates the exact paths for all vehicles in the group with savings = 0.1
        (val, paths, eids) = lp(group, G, s, t, 0.1)
        # this calculates the shortest paths of all vehicles in the group (savings=0)
        (valSP, pathsSP, eidsSP) = lp(group, G, s, t, 0)

        # save the sum of all shortest paths of the vehicle in the group
        shortestPathValue = valSP

        # create the keys in the dicts to save the paths of the solution and the shortest paths
        platooning_paths[key] = {}
        shortest_paths[key] = {}
        for vehicle in group:
            # add platooning path of vehicle
            platooning_paths[key][vehicle] = paths[vehicle]
            # add shortest path of vehicle
            shortest_paths[key][vehicle] = pathsSP[vehicle]

        # round the solution (otherwise there would be something like 4.5*10^(-14) and not simply 0...
        absolute_savings[key] = round(shortestPathValue - val, 10)
        saving = round((absolute_savings[key]*100/shortestPathValue), 10)

        # collect the information and save in groupInfo
        groupInfo[key] = [absolute_savings[key], shortestPathValue, val, round((absolute_savings[key]*100/shortestPathValue), 10), group]


        # !!!! JUST OUTPUT FROM HERE ON
        print("---!!!--- Output Start ---!!!---")
        # the information of the solution
        print("Group Solution Information: " + str(groupInfo))

        # the paths of the vehicles in the following format: {group_id: {vehicle_id: [list_of_nodes]}}
        print("Vehicle Paths: " + str(platooning_paths))

        # the paths of the vehicles in the following format: {group_id: {vehicle_id: [list_of_nodes]}}
        print("Vehicle Paths: " + str(shortest_paths))
