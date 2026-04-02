import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import psycopg2
import platform
import json
import copy
import yaml
import subprocess
from lib.Basics import Basics
from lib.Database import Database
from lib.DataSet import DataSet
from typing import Tuple, Dict, List


class TestCase:
    # load the json data
    iterable = json.load(open('Evaluation.json'))

    def __init__(self, data_set_list: List[DataSet], slicing: str, saving_factor: float, log: bool, grouping_active: bool, saving_factor_median: float,
                 type_of_hull: str, angle_of_cos: float, identify_groups_by: Tuple[str, ], routing_method: Tuple[str, ]):

        self._data_set_list = data_set_list
        self._slicing = slicing
        self._saving_factor = saving_factor
        self._log = log
        self._grouping_active = grouping_active
        self._saving_factor_median = saving_factor_median
        self._type_of_hull = type_of_hull
        self._angle_of_cos = angle_of_cos
        self._identify_groups_by = identify_groups_by
        self._routing_method = routing_method


    def get_data_sets(self) -> List[DataSet]:
        return self._data_set_list

    def get_slicing(self) -> str:
        return self._slicing

    def get_road_network(self) -> str:
        return self._road_network

    def get_saving_factor_median(self):
        return self._saving_factor_median

    def get_angle_of_cos(self) -> float:
        return self._angle_of_cos

    def get_type_of_hull(self) -> str:
        return self._type_of_hull

    def get_log(self) -> bool:
        return self._log

    def get_saving_factor(self) -> float:
        return self._saving_factor

    def get_grouping_active(self) -> bool:
        return self._grouping_active

    def get_identify_groups_by(self) -> Tuple[str]:
        return self._identify_groups_by

    def get_routing_method(self) -> Tuple[str]:
        return self._routing_method

    def get_all_values(self) -> Tuple:
        return self.get_slicing(), self.get_road_network(), self.get_saving_factor_median(), self.get_angle_of_cos(), self.get_type_of_hull(), self.get_log(), self.get_identify_groups_by(), self.get_saving_factor(), \
               self.get_routing_method(), self.get_grouping_active()


    # !!!!!!!!!!! Functions to be applied on the tests !!!!!!!!!!!

    # check if the right database is running
    def check_road_network(self, road_network: str) -> str:
        # Load configurations
        with open("config.yaml", 'r') as yaml_file:
            cfg = yaml.load(yaml_file)
        db_prefix = (cfg["dbprefix"])
        db_plugins = (cfg["dbplugins"])
        db_config = (cfg["dbconfig"])

        # check if the road network is the right one
        if self._road_network == road_network:
            # if its right: just give back the GraphDatabase
            db = GraphDatabase("http://localhost:7474", username='neo4j', password='12345678')
        else:
            # if it is wrong: relaunch the database with the self.__road_network
            db = TestCase.relaunch_db(db_prefix, self._road_network, "neo4j", "12345678", db_plugins, db_config)
        return db


    # compute incentive for the single test instance
    def calculate_incentives(self, compare_vehicle_vector: bool = True, gradient_method: bool = True, convex_hull: bool = True):
        # load basic information of the paths
        src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host = Basics.load_config()
        # iterate through all sets of the test instance
        times_incentives = {}
        for single_data_set in self.get_data_sets():
            times_incentives[single_data_set] = {}
            for single_set in single_data_set.get_set():

                # prepare the statement, which will be given to the "Popen"- function
                cmd = "Rscript " + 'convexTime.r ' + str(single_data_set.get_number_veh()) + " " + str(10) + " " + src + " " + \
                      self.get_type_of_hull() + " " + str(self.get_angle_of_cos()) + " " + str(self.get_saving_factor_median()) + " " + str(single_set) + \
                      " " + str(int(compare_vehicle_vector)) + " " + str(int(gradient_method)) + " " + str(int(convex_hull)) \
                      + " " + str(self.get_grouping_active())

                # call R to calculate incentives of the given instance
                return_incentive = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
                times_incentive = Basics().get_process_return_value(return_incentive)
                # wait for the process to finish
                return_incentive.wait()
                times_incentives[single_data_set][single_set] = times_incentive

        # return the times
        return times_incentives
    """
    def _calculate_groups_greedy(self) -> Tuple[float, float]:
        cmd = basics.algorithms()[10] + " " + basics.algorithms()[8] + " " + basics.get_src() + " " + \
              self.get_identify_groups_by()[0] + " " + str(self.get_identify_groups_by()[1]) + " " + str(single_set)

    def _calculate_groups_cpp_greedy(self) -> Tuple[float, float]:
        import ...
        start_time = time.time()
        i_m = DB.get_incentive_matrix()
        # choose an initial solution generator: None or InitCPP
        # init_cpp = None
        # init_cpp = TrivialCPP(i_m)
        # init_cpp = RandomCPP(i_m)
        init_cpp = GreedyCPP(i_m)
        x_greedy = init_cpp.find_initial_solution()
        g_iccp = Util.get_groups(x_greedy)
        runtime_grouping = time.time() - start_time
        start_time = time.time()
        DB.store
        runtime_store = time.time() - start_time
        return runtime_grouping, runtime_store
    """

    def calculate_groups(self):
        # get common information like paths and names of algorithms and scripts
        basics = Basics()
        basics.save_config()
        grouping_times_all = {}
        # iterate through all set ids (every test has a number of DataSets and every DataSet has a number of VehicleSets
        for single_data_set in self.get_data_sets():
            grouping_times_all[single_data_set] = {}
            for single_set in single_data_set.get_set():

                # identify the respectively grouping method
                # get groups by alpha cut
                if self.get_identify_groups_by()[0] == "greedy":
                    cmd = basics.algorithms()[10] + " " + basics.algorithms()[8] + " " + basics.get_src() + " " + self.get_identify_groups_by()[0] + " " + str(self.get_identify_groups_by()[1]) + " " + str(single_set)
                    print(cmd)
                # get groups by Bron Kerbasch
                if self.get_identify_groups_by()[0] == "cpp_greedy":
                    cmd = basics.algorithms()[13] + " " + basics.algorithms()[11] + " " + basics.get_src() + " " + self.get_identify_groups_by()[0]
                # get groups by
                if self.get_identify_groups_by()[0] == "cpp_ilp":
                    cmd = basics.algorithms()[13] + " " + basics.algorithms()[12] + " " + basics.get_src() + " " + self.get_identify_groups_by()[0]

                time_from_grouping = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

                grouping_times = Basics.get_process_return_value(time_from_grouping)
                grouping_times_all[single_data_set][single_set] = grouping_times
                time_from_grouping.wait()
                print(grouping_times_all)
        return grouping_times_all  # Todo: adjust the output

    def calculate_routing(self):

        # get common information like paths and names of algorithms and scripts
        basics = Basics()
        basics.save_config()

        # iterate through all set ids (every test has a number of DataSets and every DataSet has a number of VehicleSets
        for single_data_set in self.get_data_sets():
            for single_set in single_data_set.get_set():

                # query for greedy
                if self.get_routing_method()[0] == "ILP":
                    cmd = "python2 " + basics.get_src() + "/lp/" + basics.algorithms()[1] + " " + str(single_data_set.get_number_veh())
                    returnValueILP = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
                    objectives = Basics().get_process_return_value(returnValueILP, True)
        # return relevant test information
        return objectives

    # runs the incentive calculation, grouping and routing of a test for all sets
    def run(self):
        # calculate the incentives
        self.calculate_incentives()

        # calculate the groups
        self.calculate_groups()

        # calculate routing
        self.calculate_routing()
