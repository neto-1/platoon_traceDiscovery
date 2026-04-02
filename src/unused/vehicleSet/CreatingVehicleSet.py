from neo4jrestclient.client import GraphDatabase
from gurobipy import *
import numpy as np
import random
import math
from NormalDistributionTestData import NormalDistribution
from GammaDistributionTestData import GammaDistribution
from RandomTestData import RandomData
from LognormalDistributionTestData import LognormalDistribution
from RegionsTestData import RegionsData
from PartitioningTestData import PartitioningTestData
from RandomPartTestData import RandomPartTestData
import json


# input arguments from experiments.py
distribution = sys.argv[2]  # the type of distribution
vehicle_number = int(sys.argv[1])  # the size of the vehicle set
road_network = sys.argv[3]  # the road network applied
longest_shortest = 100.5  # the maximal length path
scale_factor = 0.8  # the scaling facter for the longest path
# the 4 inputs for the regions
# northregion1
# northregion2
# southregion1
# southregion2
if road_network == "saarland_simple":
    longest_shortest = 100.5
elif road_network == "thueringen_simple":
    longest_shortest = 223.6
elif road_network == "niedersachsen_simple":
    longest_shortest = 332.2
elif road_network == "bayern_simpe":
    longest_shortest = 438.8


db_user = "neo4j"  # is also already in experiments.py
db_pass = "12345678"  # is also already in experiments.py
db = GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)  # is also already in experiments.py


def random_veh(size):
    # print("random distribution")
    x = RandomData(db)  # (database connection)
    #x = PartitioningTestData(db)  # (database connection)
    x.create_vehicle(size)


def normal(size, max_length, scale_length):
    print("normal distribution")
    x = NormalDistribution(db, max_length, scale_length)  # (database connection)
    x.create_vehicle(size)


def gamma(size, max_length, scale_length):
    print("gamma distribution")
    x = GammaDistribution(db, max_length, scale_length)  # (database connection)
    x.create_vehicle(size)


def log_normal(size, max_length, scale_length):
    print("log_normal distribution")
    x = LognormalDistribution(db, max_length, scale_length)  # (database connection)
    x.create_vehicle(size)


def region():
    print("region distribution")
    x = RegionsData(db, region1up, region1down, region2up, region2down)  # (database connection)
    x.create_vehicle(size)


options = {
    "random_veh": random_veh,  # needs no more arguments
    "normal": normal,  # needs 2 more arguments (longest path and a scale element [0,1]
    "log_normal": log_normal,  # needs 2 more arguments (longest path and a scale element [0,1]
    "gamma": gamma,  # needs 2 more arguments (longest path and a scale element [0,1]
    "region": region,  # needs 4 more arguments, which determinate the 2 regions, every argument
                       # is a number, which slices the graph at that coordinate (2 arguments for every region)
}

# run the set creating
# this if clause selects the "right" options function, since the number of arguments vary
# if (distribution == "random_veh"):
#     options[distribution](size)
if distribution == "region":
    options[distribution](vehicle_number, northregion1, northregion2, southregion1, southregion2)
elif distribution == "random_veh":
    options[distribution](vehicle_number)
else:
    options[distribution](vehicle_number, longest_shortest, scale_factor)

query = "MATCH (n:VehicleSet) RETURN MAX(n.id)"
result = db.query(query)

output_data = {'set_id':result[0][0], 'longest_shortest': longest_shortest}

print json.dumps(output_data)
