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
from typing import Tuple, Dict, List


class DataSet:

    def __init__(self, number_diff_exp: int, number_veh: int, distribution: str, road_network: str):

        self._number_diff_exp = number_diff_exp
        self._number_veh = number_veh
        self._distribution = distribution
        self._road_network = road_network
        self._set_id = []


    def get_number_diff_exp(self):
        return self._number_diff_exp

    def get_number_veh(self):
        return self._number_veh

    def get_distribution(self):
        return self._distribution

    def get_road_network(self):
        return self._road_network

    def get_set(self):
        return self._set_id

    def add_set(self, new_set):
        self._set_id.append(new_set)


    # check if the right database is running
    def check_road_network(self, road_network_applied: str) -> str:
        # Load configurations
        src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host = Basics.load_config()

        # check if the road network is the right one
        if self.get_road_network() == road_network_applied:
            # if its right: just give back the GraphDatabase
            db = GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)
        # else:
            # if it is wrong: relaunch the database with the self.__road_network
            # Database.relaunch_db(self.get_road_network())  # Todo
        return self.get_road_network()

    # create the set for the test in the database and return the applied database
    def create_set_on_database(self, road_network_applied: str = "None") -> str:

        # check if the right road network is running
        database = self.check_road_network(road_network_applied)

        # count the sets for same parameters, if there is the need for different tests of same parameters
        number_created_sets = 0

        src = Basics.load_config()[0] # todo

        # create sets "number_of_different_exp"-times to create sets with same parameters
        while self.get_number_diff_exp() > number_created_sets:
            # prepare the command "cmd" to create sets
            cmd = "python " + src + "/vehicleSet/CreatingVehicleSet.py" + " " + str(self.get_number_veh()) \
                  + " " + str(self.get_distribution()) + " " + str(self.get_road_network())
            return_set_id = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            return_set_creating = Basics().get_process_return_value(return_set_id, True)
            set_id = return_set_creating['set_id']

            # save the set id to the test object
            self.add_set(set_id)

            # increase the number of set-counter
            number_created_sets += 1
        return database

    # create all data sets in the database
    @staticmethod
    def create_all_sets(data_sets: List[Tuple], road_network_applied: str = "None"):
        # create empty list for the sets
        all_sets = []

        # iterate through all data parameter sets
        for data_set in data_sets:

            # create the data set
            new_set = DataSet(data_set[1], data_set[2], data_set[3], data_set[4])
            # create data set in database

            road_network_applied = new_set.create_set_on_database(road_network_applied)
            # add the set to the list of sets
            all_sets.append(new_set)

        # return a list of data_set-objects
        return all_sets
