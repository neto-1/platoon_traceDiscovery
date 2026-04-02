from neo4jrestclient.client import GraphDatabase
from columngeneration.model.vehicle import Vehicle
from typing import List
from columngeneration.initpaths.initpathsinterface import InitPathsInterface
from columngeneration.initpaths.initshortestpath import InitShortestPath
from columngeneration.masterproblem.mpinterface import MPInterface
from columngeneration.masterproblem.masterproblem import MasterProblem
from columngeneration.masterproblem.masternotime import MasterNoTime
from columngeneration.subproblem.subproblem import SubProblem
from columngeneration.subproblem.subproblemnotime import SubProblemNoTime


# class ColumnGeneration(RoutingMethod):
class ColumnGeneration:

    def __init__(self, initiation_methods: List[InitPathsInterface], master_problems: MPInterface):
        self._set_id = -1
        self._savings = None
        self._db_connection = None
        self._vehicles = []  # List[Vehicle]
        self._init_methods = initiation_methods
        self._master_problem = master_problems
        # self._obj_values = Dict[int: Tuple[float, float]]

    # interface!!!!
    def create(self, vehicle_set_id: int):
        # initiate self values
        self._initiate(vehicle_set_id)

        # create paths for every vehicle
        self._init_paths()

        # run the master problem and sub problem
        self._solve_master()

    # load the database connection and store it in self._db_connection
    def _get_db_connection(self) -> None:
        # self._db_connection = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")
        self._db_connection = GraphDatabase("http://localhost:7474", username="neo4j", password="1234567890")

    # get the vehicles from database and save them into self._vehicles
    def _get_vehicles(self) -> None:
        # get vehicles from database
        # query = "MATCH (g:VehicleSet)-[r:INSET]->(v:Vehicle),(e:loc)-[:END]-(v)-[:START]-(s:loc) WHERE g.id = " + str(self._set_id) + " RETURN DISTINCT id(v), id(e), id(s), id(g)"
        query = "MATCH (g:Group)-[r:INGROUP]->(v:Vehicle), (e:location)-[:END]-(v) - [:START]-(s:location) RETURN DISTINCT id(v), id(e), id(s), id(g)"

        results = self._db_connection.query(query)

        # create all vehicles and store them to the object
        for r in results:
            self._vehicles.append(Vehicle(self._db_connection, r[0], r[2], r[1]))

    # encapsulation for the whole initiation
    def _initiate(self, set_id: int):
        self._set_id = set_id
        self._get_db_connection()
        self._get_vehicles()

    # initiate the vehicles through all init methods
    def _init_paths(self):
        for method in self._init_methods:
            method.init_paths(self._vehicles, self._db_connection)

    def _solve_master(self):
        self._master_problem.solve_master(self._vehicles, self._db_connection)

    # method from the interface
    def stringify(self) -> str:
        raise NotImplementedError("Interface")

    def _get_set(self):
        return self._set_id

# #################### TESTING!!!! DELETE FOR LATER AND AD THE RIGHT CLASS (the right class-line in the code) WITH INTERFACE IN TOP!!!

# input !!!!!! INTERFACE !!!!!!
set_idx = 8674
# call from test suit:
savings = 0.1

init_method = [InitShortestPath()]

# the subproblems
sub_method = [SubProblemNoTime(savings)]
# sub_method = [SubProblem(savings)]

# the masterproblems
master_method = MasterNoTime(savings, sub_method)
# master_method = MasterProblem(savings, sub_method)

# initiate a variable for the object
test_instance_to_test = ColumnGeneration(init_method, master_method)

# run the whole process
test_instance_to_test.create(set_idx)



# the old function
# old function
# def column_generation_platooning(saving=0.1, id_set=0, init_shortest_path=1, init_best_pair=0,
#                                  init_best_pair_callback=0, delete_path=1, output_showing=0):
#     # create a set for relevant column-generation-parameter
#     parameter_column_generation = {'global': {}}
#     # save the enabled initial paths
#     parameter_column_generation['global']['initial_paths_used'] = [init_shortest_path, init_best_pair,
#                                                                    init_best_pair_callback, delete_path]
#     # create a set to save relevant times
#     times_column_generation = {'global_times': {}}
#     # save the initial time
#     time_init = time.clock()
#
#     # ======================================== INITIALIZATION ========================================
#     # ===== initial parameters =====
#     # create shortest path initially
#     include_shortest_path = init_shortest_path
#     # create best pair paths initially
#     include_two_veh_sub = init_best_pair
#     # create all relevant paths with the intersections of two vehicles
#     include_relevant_paths = init_best_pair_callback
#     # delete the Paths of the vehicles after the optimization
#     delete_path_after_optimization = delete_path
#
#     # names of the database....later only in config, this is for testing purposes only
#     vehicle_set = "VehicleSet"
#     vehicle_group = "Group"
#     vehicle_name = "Vehicle"
#     in_set_name = "INSET"
#     in_group_name = "INGROUP"
#     location_name = "loc"
#     start_location = "START"
#     end_location = "END"
#     union_name = "UNION"
#     polygon_name = "Polygon"
#     poly_attribute_name = "Poly"
#     # hull_name = "HULL"
#
#     # all_names = [vehicle_group, vehicle_name, in_set_name, in_group_name, location_name, start_location, end_location,
#     #             union_name, polygon_name, poly_attribute_name, hull_name]
#
#     # initialization of graph database neo4j
#     db = GraphDatabase("http://localhost:7474", username="neo4j", password="12345678")
#
#     # first get the set of vehicles to get all vehicles considered (not only the groups)
#     query = "MATCH (g:" + vehicle_set + ")-[r:" + in_set_name + "]->(v:" + vehicle_name +\
#             "),(e:" + location_name + ")-[:" + end_location + "]-(v)-[:" + start_location +\
#             "]-(s:" + location_name + ") WHERE g.id = " + str(id_set) + " RETURN DISTINCT id(v), id(e), id(s), id(g)"
#     results = db.query(query)
#
#     # create a list of all vehicles and a list for the starting nodes and a list for the ending nodes
#     vehicles = []
#     s = {}
#     t = {}
#     for r in results:
#         vehicles.append(r[0])
#         s[r[0]] = r[2]
#         t[r[0]] = r[1]
#
#     # counting variable for index of Routes (the second and third help to determine paths created per group
#     index_route = 0
#     already_created_number_of_paths = 0
#
#     # create a empty list for all vehicles
#     all_vehicles = []
#
#     # create objects for every vehicle and save them to a list
#     for vehicle in vehicles:
#         # create every vehicle as an object
#         veh = Vehicle(db, vehicle, s[vehicle], t[vehicle])
#
#         # append the vehicle to the list of vehicles
#         all_vehicles.append(veh)
#     # get the ids of all groups
#     query = "MATCH (n:" + vehicle_group + ") RETURN id(n)"
#     group_ids = db.query(query)
#
#     # initiate group_info, to save the grouping data
#     group_info = {}
#
#     # number of times the column generation produces NOT the global optimum
#     unsuccessful_column_generation = 0
#
#     # the total value of CG objective of all groups and the total objective of the ILP
#     total_objective_column_generation = 0
#     total_objective_ilp = 0
#
#     # save the time to initiate the column generation process
#     times_column_generation['global_times']["time_init"] = time.clock() - time_init
#     # ======================================== End of Initialization ========================================
#
#     # ===========================================!!! MAIN LOOP !!!===========================================
#     # save the start time for calculating all group savings
#     calc_group_savings_start = time.clock()
#     # iterate through the groups
#     for actual_id in group_ids:
#         parameter_column_generation[actual_id[0]] = {}
#         times_column_generation[actual_id[0]] = {}
#
#         # time to initiate a single group
#         time_init_group = time.clock()
#
#         # get the groups and the polygon of the group
#         query = "MATCH (g:"+vehicle_group+")-[:"+union_name+"]->(p:"+polygon_name+") WHERE id(g) = "\
#                 + str(actual_id[0]) + " RETURN p."+poly_attribute_name
#         results = db.query(query)
#
#         query = "WITH 'POLYGON(("
#         for r in results:
#             for i in range(0, len(r[0])):
#                 query = query + " " + str(r[0][i])
#                 if (i % 2 != 0) & (i < (len(r[0]) - 1)):
#                     query = query + ", "
#         query = query + "))' as polygon CALL spatial.intersects('geom',polygon) YIELD node as n1 with n1 MATCH" \
#                         " (n1)-[r:NEIGHBOUR]->(n2) RETURN id(n1), id(n2), r.distance, id(r)"
#         results = db.query(query)
#
#         # create the graph for the group
#         graph = nx.DiGraph()
#         for r in results:
#             graph.add_edge(r[0], r[1], c=r[2], id=r[3])
#             graph.add_edge(r[1], r[0], c=r[2], id=r[3]+0.5)
#
#         # get the relevant vehicle information of the actual group
#         query = "MATCH (g:"+vehicle_group+")-[:"+in_group_name+"]->(v:"+vehicle_name+") WHERE id(g) = " \
#                 + str(actual_id[0]) + " Return id(v), v.shortestpath_cost"
#         results = db.query(query)
#         vehicles = []
#         group_veh = []
#         val_shortest_path = 0
#         # create a list of the vehicle IDs
#         for vehic in results:
#             val_shortest_path += vehic[1]
#             vehicles.append(vehic[0])
#         # create a list of the vehicle objects
#         for veh in all_vehicles:
#             if veh.getID() in vehicles:
#                 group_veh.append(veh)
#
#         # ===== calculate the REAL optimum and the shortest path optimum of the platooning problem =====
#         # start time to calculate global optimum
#         time_opt_solutions = time.clock()
#         # create the optimal solution with LP
#         (valOpt, pathsOpt, eidsOpt) = lppl.lp(vehicles, graph, s, t, saving)
#         # save the time of calculating the global optimum of this group
#         times_column_generation['global_times']["time_opt_solutions"] = time.clock() - time_opt_solutions
#
#         # ========================= Initial Path creating =========================
#         # save the time for initial path creating
#         time_init_path_creating = time.clock()
#         # store actual index of routes to calculate the number of path created for this group
#         initial_number_paths = index_route
#
#         # create the shortest path
#         if include_shortest_path:
#             index_route = createInitPaths.shortest_path(group_veh, index_route, s, t, db)
#
#         # create best path of respectively two vehicles of the set of vehicles considered
#         if include_two_veh_sub:
#             index_route = createInitPaths.sub_best_pair_lp(group_veh, vehicles, graph, saving, index_route)
#
#         if include_relevant_paths:
#             index_route = createInitPaths.sub_best_pair_lp_callback(group_veh, vehicles, graph, saving, index_route)
#
#         # save the number of new path created initially
#         parameter_column_generation[actual_id[0]]['initial_created_paths'] = index_route - initial_number_paths
#         # save the time of initial path creating for the respectively group
#         times_column_generation['global_times']["time_initial_path_creating"] = time.clock() - time_init_path_creating
#         # =============== End Initial Path creating ===============
#
#         # create a variable which saves the sum of all shortest path for this group
#         sum_of_shortest_path = 0
#         # add the shortest path up to the created variable
#         for veh_objects in group_veh:
#             # add the shortest path to the sum of shortest paths
#             sum_of_shortest_path += sum(veh_objects.getPaths()[0].getDistance())
#
#         # time of initialising a group
#         times_column_generation[actual_id[0]]["time_init_group"] = time.clock() - time_init_group
#
#         # ==================== Main ITERATION ====================
#         # create empty lists, to save the objectives and the paths of the objectives
#         objectives = []
#         path_of_objective = []
#         # cancel condition which checks, if there is a new path generated (initially true)
#         found_new_path = True
#         # counter for the iterations of the main loop
#         iteration_of_main = 0
#         # time main loop for a group
#         time_main_iteration = time.clock()
#
#         # The iteration process of solving the MP and creating new Path with the SP
#         while found_new_path:
#             # count the number of iterations
#             iteration_of_main += 1
#             # run the master problem
#             (valMaster, paths, vehicleShadowpPrices) = lpMaster.master_problem_lp(group_veh, graph, saving)
#
#             if output_showing:
#                 print("------ %% ColGen iterative Objective of group " + str(actual_id[0]) + ": ( " + str(
#                     valMaster) + " which is between [" + str(valOpt)+", " + str(val_shortest_path)+"]) %% ------")
#
#             # save the actual obj and path
#             objectives.append(valMaster)
#             path_of_objective.append(paths)
#
#             # run the dual sub problem
#             (index_route, found_new_path) = lpSubDual.subproblem_dual_lp(group_veh, graph,
#                                                                          index_route, vehicleShadowpPrices)
#         # ======================================================================
#         # save the number of paths created, the iterations needed for the output
#         parameter_column_generation[actual_id[0]]['number_of_paths_created'] = \
#             index_route - already_created_number_of_paths
#         already_created_number_of_paths = index_route
#         parameter_column_generation[actual_id[0]]['iteration_of_main'] = iteration_of_main
#         parameter_column_generation[actual_id[0]]['gap'] = round(valMaster - valOpt, 10)
#         # save the output of every group into group_info
#         group_info[actual_id[0]] = [val_shortest_path - valMaster, val_shortest_path, valMaster,
#                                     round((val_shortest_path - valMaster)/100, 10), group_info]
#
#         if valMaster - valOpt > 0.00001:
#             unsuccessful_column_generation += 1
#             print("ERRRRRROR - not the global optimum (CG val worse than global) - CG: "
#                   + str(valMaster) + " Global: " + str(valOpt) + " in percent: " + str(100*(valMaster-valOpt)/valOpt))
#         if valOpt - valMaster > 0.00001:
#             print("ERRRRRROR - not the global optimum (CG too good) - CG: " + str(valMaster)
#                   + " Global: " + str(valOpt))
#         # the time all iterations for this group takes
#         times_column_generation[actual_id[0]]['time_main_iteration'] = time.clock() - time_main_iteration
#
#         # add the values of the objectives
#         total_objective_column_generation += valMaster
#         total_objective_ilp += valOpt
#
#         # delete the calculated paths of all vehicles in the group to start new
#         if delete_path_after_optimization:
#             for vehicle in group_veh:
#                 vehicle.deletePaths()
#         # ========================= END MAIN ITERATION =========================
#     calc_group_savings = time.clock() - calc_group_savings_start
#
#     # save the total time elapsed
#     time_elapsed_total = time.clock() - time_init
#
#     parameter_column_generation['global']['number_of_path_total'] = index_route
#     parameter_column_generation['global']['gap'] = round(total_objective_column_generation - total_objective_ilp, 10)
#
#     # create output
#     output_data = {
#         'times': {
#             'calc_group_savings': calc_group_savings,  # time to calculate all group savings
#             'determine_disjunct_groups': 0,  # ready
#             'routing': time_elapsed_total,  # complete time of calculating the savings of all created groups
#             'storing_routes': 0  # Todo
#         },
#         'group_sets': {
#             'calculated_number_of_groups': len(group_ids),  # the number of groups
#             'vehicles_in_groups': 0,  # can not be determined by column generation
#             'vehicles_not_in_groups': 'not filled yet',  # ready
#             'successfull_groups': len(group_ids) - unsuccessful_column_generation,  # ready
#             'unsuccessfull_groups': unsuccessful_column_generation,  # ready
#             'group_savings': total_objective_column_generation - total_objective_ilp,  # ready
#             'parameter': {'times': times_column_generation,
#                           'parameters': parameter_column_generation
#                           },  # ready
#         }
#     }
#     # creating routing data
#     routing_data = {'routing': []}
#     for key, group_routing in group_info.iteritems():
#         routing = {
#                 'group_id': key,  # the id of the group
#                 'savings': round(group_routing[1] - group_routing[2], 10),  # the gained savings in this group
#                 'shortest_path': group_routing[1],  # the shortest path of all vehicles in this group
#                 'algorithm': 'CG',  # the name of this procedure
#                 'parameter': 'None',  # ready
#         }
#         routing_data['routing'].append(routing)
#     # merge routing_data with output_data
#     output_data.update(routing_data)
#
#     # return statement
#     return output_data
