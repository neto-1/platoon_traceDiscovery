from __future__ import print_function
import collections
import subprocess
from neo4jrestclient.client import GraphDatabase
import time
import yaml
import psycopg2
import platform
from importTest import import_test_data
import json
import platform
from database import Experiment
from gurobipy import *
from lib.TestSuite import TestSuite
from lib.TestCase import TestCase
from lib.Basics import Basics
from lib.Database import Database


# initiate the database by testing, if its already running
Database.test_and_connect()


# in basics all values can be stored to be passed around (e.g. names of the different algorithms)
basic = Basics()
basic.save_config()

# dummy variable for the "old" road Network
old_network = "no_initial_road_network"


log = False  # the logging

print(" Starting Experiment- ")

# start the experiment
# experiment = Experiment(logging=True)

# create a file containing the times to create the specific set
init_set_creating_times = {}

list_of_tests = TestSuite.create_from_json("Evaluation2")

# create all sets for all tests
list_of_tests.run_tests()




output_data = Basics.create_output_data(parameter_list, times_incentive, grouping_times, objectives, init_set_creating_times)



# end experiment
#experiment.end()
