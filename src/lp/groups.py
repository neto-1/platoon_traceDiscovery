import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import lppl
import lpplTime
import fg
import psycopg2
import platform
import json
from networkx.readwrite import json_graph


def create_platoon_path_of_vehicle(database, vehicle_node_id, path_nodes, group_id):
    route_node_list = []
    count = -1
    for node_val in path_nodes:
        if count == -1:
            query_line = "MATCH (pathnode:loc),(vehiclenode:Vehicle) where ID(pathnode)=" + str(node_val) + \
                  " and ID(vehiclenode)=" + str(vehicle_node_id) + " " \
                  "CREATE (routenode:RouteNode{time:0, group: " + str(group_id) + "}) " \
                  "CREATE (routenode)-[pnode:PNODE]->(pathnode) " \
                  "CREATE (vehiclenode)-[sp:PR]->(routenode) " \
                  "RETURN ID(routenode)"
        else:
            route_node_id = route_node_list.__getitem__(count)
            query_line = "MATCH (pathnode:loc),(preroutenode:RouteNode),(preroutenode:RouteNode)-" \
                         "[prepnode:PNODE]->(prepathnode:loc),(prepathnode)-[r:NEIGHBOUR]-(pathnode) " \
                         "where ID(pathnode)=" + str(node_val) + " and ID(preroutenode)=" + str(route_node_id) + " " \
                         "CREATE (routenode:RouteNode{time:0, group: " + str(group_id) + "}) " \
                         "CREATE (routenode)-[pnode:PNODE]->(pathnode) " \
                         "CREATE (preroutenode)-[next:NEXT{cost:r.distance}]->(routenode) " \
                         "RETURN ID(routenode)"
        res = database.query(query_line)
        route_node_list.append(res[0][0])
        count = count + 1
    # print "Platoon path is computed. All nodes and relations based on Data Model are created successfully"

time_total = time.clock()
time_init = time.clock()
# init database
db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")

query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle),(e:loc)-[:END]-(v)-[:START]-(s:loc)" \
        "RETURN DISTINCT id(v), id(e), id(s)"

results = db.query(query)

vehicles = []
s = {}
t = {}
for r in results:
    vehicles.append(r[0])
    s[r[0]] = r[2]
    t[r[0]] = r[1]

query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle) RETURN id(g), id(v)"
results = db.query(query)

groups = {}
for r in results:
    groupId = r[0]
    vehicleId = r[1]
    if groupId not in groups:
        groups[groupId] = []
    groups[groupId].append(vehicleId)

time_init = time.clock() - time_init
time_start = time.clock()
p = {}
groupInfo = {}
ing = 0
outg = 0
number_of_groups = len(groups)
platooning_paths = {}
print("number of groups: " + str(number_of_groups))
graph_parameter = {}
print("---------------------------------------------------------------------------")
if len(groups) > 0:
    for key, group in groups.items():
        query = "MATCH (g:Group)-[r:UNION]->(p:Polygon) WHERE id(g) = " + str(key) + " RETURN p.Poly"
        results = db.query(query)
        query = "WITH 'POLYGON(("
        for r in results:
            for i in range(0, len(r[0])):
                query = query + " " + str(r[0][i])
                if (i % 2 != 0) & (i < (len(r[0]) - 1)):
                    query = query + ", "
        query = query + "))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as " \
                        "n1 with n1 MATCH (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"

        results = db.query(query)
        G = nx.DiGraph()

        for r in results:
            G.add_edge(r[0], r[1], c=r[2], id=r[3])
            G.add_edge(r[1], r[0], c=r[2], id=r[3])

        print("group ", key, group)
        # (val, paths, eids) = lpplTime.lp(group, G, s, t, 0.1) # this also calculates the times
        # and not only routing, but performs really bad
        time_solve_this_group = time.clock()
        (val, paths, eids) = lppl.lp(group, G, s, t, 0.1)
        time_solve_this_group = time.clock() - time_solve_this_group

        # save relevant data for analysis
        graph_parameter[key] = {"number of edges": len(G.edges()), 'number of nodes': len(G.nodes()), 'vehicles': group, 'time': time_solve_this_group, '_degree_graph_': str(G.degree())}

        # save the platooning path of the vehicles into a set
        platooning_paths[key] = {}
        for vehicle in group:
            platooning_paths[key][vehicle] = paths[vehicle]

        shortestPathValue = 0
        query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle) WHERE id(g)= " + str(key) + \
                "  RETURN sum(v.shortestpath_cost) as sp"
        results = db.query(query)
        for r in results:
            shortestPathValue = r[0]

        p[key] = round(shortestPathValue - val, 10)
        saving = round((p[key]*100/shortestPathValue), 10)

        print("saving group " + str(key) + ":", round(p[key], 10), " SP: " + str(shortestPathValue) + " PSP: "
              + str(val) + " saving: " + str(round((p[key]*100/shortestPathValue), 10)))
        groupInfo[key] = [round(p[key], 10), shortestPathValue, val, round((p[key]*100/shortestPathValue), 10), group]
        if saving > 0.0000001:
            ing = ing + 1
        else:
            outg = outg + 1

    calc_group_savings = (time.clock() - time_start)

    time_disjoint_groups = time.clock()
    (model, groups, g) = fg.lp(vehicles, groups, p)
    time_disjoint_groups = time.clock() - time_disjoint_groups

    time_elapsed = (time.clock() - time_start)

    sumSP = 0
    sumPSP = 0
    usedVehicles = []
    solution_groups = []

    for (key, group) in groups.items():
        if g[key].X > 0.99:
            usedVehicles.extend(group)
            sumSP += groupInfo[key][1]
            sumPSP += groupInfo[key][2]
            solution_groups.append(key)

    # create nodes for the platooning path
    store_platoon_routes = time.clock()
    for group in platooning_paths:
        for vehicle in platooning_paths[group]:
            create_platoon_path_of_vehicle(db, vehicle, platooning_paths[group][vehicle], group)
    store_platoon_routes = time.clock() - store_platoon_routes
    time_total_routing = time.clock() - time_total

    # prepare the output
    output_data = {
        'times': {
            'calc_group_savings': calc_group_savings,  # time to calculate all group savings
            'determine_disjunct_groups': time_disjoint_groups,  # time to determine the disjoint groups
            'routing': time_total_routing,  # complete time of calculating the savings of all created groups
            'storing_routes': store_platoon_routes  # the time to store all platooning routes of the respectively groups
        },
        'group_sets': {
            'calculated_number_of_groups': number_of_groups,  # the number of groups
            'vehicles_in_groups': len(usedVehicles),  # the number of vehicles in groups in the solution
            'vehicles_not_in_groups': 'not filled yet',  # the number of vehicles, which arent driving in a group
            'successfull_groups': ing,  # the number of groups, which have savings bigger than zero
            'unsuccessfull_groups': outg,  # the number of groups, where savings couldnt be achieved
            'group_savings': sumSP - sumPSP,  # the total savings, which can be gained with the applied groups
            'parameter': graph_parameter  # the vehicles considered in the respectively group and the number of edges
        }
    }

    routing_data = {'routing': []}
    for key, group_routing in groupInfo.iteritems():
        routing = {
            'routing': {
                'group_id': key,  # the id of the group
                'savings': group_routing[1] - group_routing[2],  # the gained savings in this group
                'shortest_path': group_routing[1],  # the shortest path of all vehicles in this group
                'algorithm': 'ILP',  # the name of this procedure
                'parameter': 'None',  # ready
            }
        }
        routing_data['routing'].append(routing['routing'])

    output_data.update(routing_data)

print(json.dumps(output_data))
