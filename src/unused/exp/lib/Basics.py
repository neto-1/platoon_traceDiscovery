import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import psycopg2
import platform
import json
import yaml
import copy
from typing import Tuple, Dict, List


# class contains all common information like config data or general functions
class Basics:

    # init the basics
    def __init__(self):
        self._src = None
        self._db_prefix = None
        self._db_plugins = None
        self._db_config = None
        self._experiments = None
        self._pg_name = None
        self._pg_pass = None
        self._pg_db_name = None
        self._pg_host = None
        self._algorithms = ['convex.r', 'groups.py', 'sd.R', 'platoon.py', 'convexTime.r',
              'HubHeuristic.py', 'CreatingVehicleSet.py', 'expCG.py', 'grouping.R', 'integratemain.py', 'RScript', 'cpp_greedy', 'cpp_ilp' , 'python2']

    def get_src(self):
        return self._src

    def get_db_prefix(self):
        return self._db_prefix

    def get_db_plugins(self):
        return self._db_plugins

    def get_db_config(self):
        return self._db_config

    def get_experiments(self):
        return self._experiments

    def get_pg_name(self):
        return self._pg_name

    def get_pg_pass(self):
        return self._pg_pass

    def get_db_name(self):
        return self._pg_db_name

    def get_pg_host(self):
        return self._pg_host

    def algorithms(self):
        return self._algorithms

    # save the config into the object
    def save_config(self) -> None:
        # import config
        src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host = Basics.load_config()
        # save in the object
        self._src = src
        self._db_prefix = db_prefix
        self._db_plugins = db_plugins
        self._db_config = db_config
        self._experiments = experiments
        self._pg_name = pg_name
        self._pg_pass = pg_pass
        self._pg_db_name = pg_db_name
        self._pg_host = pg_host

    # import the config data
    @staticmethod
    def load_config(config:str = "config"):
        with open(str(config) + ".yaml", 'r') as yaml_file:
            cfg = yaml.load(yaml_file)
        src = (cfg["src"])
        db_prefix = (cfg["dbprefix"])
        db_plugins = (cfg["dbplugins"])
        db_config = (cfg["dbconfig"])
        db_user = (cfg["usernameneo4j"])
        db_pass =(cfg["neo4jPW"])
        experiments = (cfg["experiments"])
        pg_name = (cfg["pgname"])
        pg_pass = (cfg["pgpass"])
        pg_db_name = (cfg["pgdbname"])
        pg_host = (cfg["pghost"])

        return src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host

    # format the output of the popen process after calling another procedure
    @staticmethod
    def get_process_return_value(process, verbose=False):
        """
        Get the return value of process (i.e. the last print statement)
        :param process: The process returned from subprocess.popen
        :param verbose: Whether or not the output of the process should be printed
        """
        output = None

        # poll will return the exit code if the process is completed otherwise it returns null
        while process.poll() is None:
            line = process.stdout.readline()
            if not line:
                break
            output = line  # last print statement
            if verbose:
                print(line.rstrip().decode('utf-8'))

        return json.loads(output)  # parse JSON

    # format the output and return formated data to be uploaded into a database
    @staticmethod
    def create_output_data(input_parameter, incentive_times, groups_times, output_routing, set_creating_times):
        # input_parameter = [vehicle0, roadNetwork1, slicing2, saving_factor_median3, saving_factor4, angle_of_cos5,
        # type_of_hull6, log7, distribution8, identify_groups_by9, min_groups10, routing_method11, grouping_active12,
        # number_of_different_exp13, setID14]
        i = 4

        data = {
            'test': {
                'vehicle_set_id': input_parameter[14],  # ready
                'number_of_edges': db.query("MATCH p=()-[r:NEIGHBOUR]->() RETURN count(p)")[0][0],  # ready
                'number_of_vehicles': db.query("match (s:VehicleSet)-[:INSET]-(v:Vehicle) where s.id = " + str(setID) + " return count(v)")[0][0],  # ready
                'number_of_groups': db.query("match (g:Group) return count(g)")[0][0],  # ready
                'enable_grouping': input_parameter[12],  # ready
                'identify_group_by': input_parameter[9],  # ready
                'distribution': input_parameter[8],  # ready
                'database': input_parameter[1],  # ready
                'longest_shortest_path': return_set_creating['longest_shortest'],  # ready
                'shortest_path_total': db.query("match (s:VehicleSet)-[:INSET]-(v:Vehicle) where s.id = " + str(setID) + " return sum(v.shortestpath_cost)")[0][0],  # ready
            },
            'group_sets': {
                'calculated_number_of_groups': db.query("match (g:Group) return count(g)")[0][0],  # ready
                'vehicles_in_groups': len(db.query("match (g:Group)-[:INGROUP]-(v:Vehicle) return distinct id(v)")),  # readym
                'vehicles_not_in_groups': input_parameter[0] - len(db.query("match (g:Group)-[:INGROUP]-(v:Vehicle) return distinct id(v)")),  # ready
                'successfull_groups': output_routing['group_sets']['successfull_groups'],  # ready
                'unsuccessfull_groups': output_routing['group_sets']['unsuccessfull_groups'],  # ready
                'group_savings': output_routing['group_sets']['group_savings'],  # ready
                'parameter': output_routing['group_sets']['parameter'],  # ready
            },
            'times': {
                'init_considered_set': set_creating_times[input_parameter[1]][input_parameter[14]],  # ready
                'init_total': init_set_creating_times['experiment_init'],  # ready
                'creating_incentives': incentive_times['time_data'][2],  # ready
                'storing_incentives': incentive_times['time_data'][3],  # ready
                'creating_groups': groups_times['time_data'][1],  # ready
                'storing_groups': groups_times['time_data'][2],  # ready
                'calc_group_savings': output_routing['times']['calc_group_savings'],  # ready
                'determine_disjunct_groups': output_routing['times']['determine_disjunct_groups'],  # ready
                'storing_routes': output_routing['times']['storing_routes'],  # ready
                'routing': output_routing['times']['routing']  # ready
            },
            'slicing': [
                {
                    'vehicles': [i + 1, i],  # TODO
                    'parameter': [1, 2 * i, 3, 4 * i],  # TODO
                    'method': 'greedy',  # TODO
                    'slices': 2  # TODO
                }
            ]
        }

        # vehicle data output
        vehicle_data = {'vehicles': []}
        all_vehicles = db.query("MATCH (n:VehicleSet)-[:INSET]-(v:Vehicle) where n.id = " + str(input_parameter[14]) + " RETURN id(v) as vID")
        for veh in all_vehicles:
            shortest_path_of_veh = db.query("MATCH (v:Vehicle)-[:START]-(n:loc)-[:PNODE]-(r:RouteNode)-[:SP]-(v:Vehicle) where id(v) = " + str(veh[0]) +
                                            " with r match (r)-[:NEXT*]-(p:RouteNode) with p match (p)-[:PNODE]-(m:loc) return id(m) as mID")
            route_nodes = []
            for route_node in shortest_path_of_veh:
                route_nodes.append(route_node[0])

            vehicles = {
                'id': veh[0],  # ready
                'shortest_path_value': db.query("match (s:VehicleSet)-[:INSET]-(v:Vehicle) where id(v) = " + str(veh[0]) + " return v.shortestpath_cost")[0][0],  # ready
                'shortest_path': route_nodes,  # ready
                'platoon_path_value': 0,  # TODO
                'platoon_path': [0]  # TODO
            }
            vehicle_data['vehicles'].append(vehicles)
        # merge with data
        data.update(vehicle_data)

        # group data output
        all_groups = db.query("match(g:Group) return id(g) as gID")
        groups_data = {'groups': []}
        for single_group in all_groups:
            all_veh_in_group = db.query(
                "match (g:Group)-[:INGROUP]-(v:Vehicle) where id(g) = " + str(single_group[0]) + " return id(v) as vID")
            all_incentive_ids_of_group = db.query(
                "match (g:Group)-[:INGROUP]-(v:Vehicle)-[:PAIR]-(p:PlatooningUtility)-[:PAIR]-(v2:Vehicle)-[:INGROUP]-(g:Group) where id(g) = " + str(
                    single_group[0]) + " return distinct id(p)")
            all_veh = []
            all_incentives = []
            for veh in all_veh_in_group:
                all_veh.append(veh[0])
            for incentive in all_incentive_ids_of_group:
                all_incentives.append(incentive[0])

            group = {
                'id': single_group[0],  # ready
                'vehicles': all_veh,  # ready
                'groups_shortest_path_sum': db.query("match (g:Group)-[:INGROUP]-(v:Vehicle) where id(g) = " + str(
                    single_group[0]) + " return sum(v.shortestpath_cost)")[0][0],  # ready
                'group_incentives': all_incentives,  # ready
                'parameter': {'alpha_cut': 0.0},  # TODO
            }
            groups_data['groups'].append(group)
        # merge with data
        data.update(groups_data)

        # routing data output
        routing_data = {'routing': output_routing['routing']}
        # merge with data
        data.update(routing_data)

        # incentive data output
        incentives_data = {'incentives': []}
        incentive_set = db.query(
            "match (v:Vehicle)-[:PAIR]-(p:PlatooningUtility)-[:PAIR]-(v2:Vehicle) return id(p) as pID, id(v) as vID1,id(v2) as vID2, p.vector_degree as vector_degree, p.gradient as gradient, p.overlapVol as overlapVol, "
            "p.overlapArea as overlapArea")
        incentive_id_list = []
        for incentive in incentive_set:
            if incentive[0] not in incentive_id_list:
                # query the start and end points of both vehicles to store them in criteria
                vehicle_points = db.query("match (le:loc)-[:END]-(v:Vehicle)-[:START]-(ls:loc) where id(v) = " + str(incentive[1]) + " or id(v) = " + str(
                    incentive[2]) + " return ls.lon as lslon, ls.lat as lslat, le.lon as lelon, le.lat as lelat")
                incentives = {
                    'vehicles': [incentive[1], incentive[2]],  # ready
                    'incentives': [incentive[3], incentive[4], incentive[5], incentive[6]],  # ready
                    'criteria': {'vector_degree': input_parameter[5], 'gradient': input_parameter[3], 'type_of_hull': input_parameter[6], 'start_end_points': [vehicle_points[0], vehicle_points[1]]}  # ready
                }
                incentive_id_list.append(incentive[0])
                incentives_data['incentives'].append(incentives)
        # merge with data
        data.update(incentives_data)

        # time_sql_end = time.clock() - time_sql
        # print(time_sql_end)

        return data
