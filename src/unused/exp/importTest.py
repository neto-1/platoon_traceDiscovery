import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import psycopg2
import platform
import json
import copy


def import_test_data():
    # load the json data
    iterable = json.load(open('Evaluation.json'))

    # convert the data to build up a list of all permutations
    # general (static) data (numberExp: Number of SAME experiments; number_diff_exp:
    # number of different exo with same amount of veh;
    number_exp = iterable["Evaluation"]["NumberOfExp"]
    number_diff_exp = iterable["Evaluation"]["NumberOfDifferentExp"]
    number_veh = iterable["Evaluation"]["NumberOfVeh"]

    # create a list to determine how many vehicle sets are needed
    set_creating = [number_veh, number_diff_exp]
    # save all values in permuatationList
    permutation_list = [number_exp]
    # save the name of the list to identify the respectively values
    permutation_name = ["numberExp"]

    # The Road network assumed
    road_network = iterable["Evaluation"]["RoadNetwork"]
    # permutation_list.append(road_network)
    # permutation_name.append("RoadNetwork")

    # Slicing Method
    slicing = iterable["Evaluation"]["SlicingMethod"]
    permutation_list.append(slicing)
    permutation_name.append("slicing")

    # Methods of pairwise incentive creation
    veh_compare = iterable["Evaluation"]["VehicleCompare"]
    # parameters for pairwise incentives
    permutation_list.append(veh_compare["nuStrich"])
    permutation_name.append("nuStrich")
    permutation_list.append(veh_compare["angle"])
    permutation_name.append("angle")
    permutation_list.append(veh_compare["convexhullparameter"])
    permutation_name.append("convexhullParameter")
    permutation_list.append(veh_compare["Activated"])
    permutation_name.append("Activated")

    # should the result be saved in SQL
    loggin = iterable["Evaluation"]["Logging"]
    permutation_list.append(loggin)
    permutation_name.append("log")

    # Routing Method
    routing = iterable["Evaluation"]["Routing"]  # type of routing
    permutation_list.append(routing)
    permutation_name.append("routing")

    # Savings
    savings = iterable["Evaluation"]["Savings"]
    permutation_list.append(savings)
    permutation_name.append("savings")

    # distribution
    distribution = iterable["Evaluation"]["DistributionOfVeh"]   # type of distribution
    # permutation_list.append(distribution["Statistical"])       # type of statistical distribution
    # permutation_name.append("Statistical")
    set_creating.append(distribution["Statistical"])

    # !!!!!!!!! the changing data for permutations !!!!!!!!!
    # Grouping Method
    grouping = iterable["Evaluation"]["GroupingMethod"]   # type of grouping method

    # create a list for every grouping method, because else there would be redundant cases of the permutations
    permutation_greedy = []
    permutation_sp = []
    permutation_wtp = []
    permutation_dima = []

    # add 'groupingMethod' and 'numberOfGroups' to the names for identifying
    permutation_name.append('groupingMethod')
    permutation_name.append('numberOfGroups')

    if 'greedy' in grouping:
        permutation_list_greedy = copy.copy(permutation_list)
        permutation_name_greedy = copy.copy(permutation_name)
        permutation_list_greedy.append(["greedy"])
        permutation_list_greedy.append(grouping["greedy"])
        permutation_name_greedy.append("greedy")
        permutation_greedy = list(itertools.product(*permutation_list_greedy))

    if 'dima' in grouping:
        permutation_list_dima = copy.copy(permutation_list)
        permutation_name_dima = copy.copy(permutation_name)
        permutation_list_dima.append(["dima"])
        permutation_list_dima.append(grouping["dima"])
        permutation_name_dima.append("dima")
        permutation_dima = list(itertools.product(*permutation_list_dima))

    if 'wtp' in grouping:
        permutation_list_wtp = copy.copy(permutation_list)
        permutation_name_wto = copy.copy(permutation_name)
        permutation_list_wtp.append(["wtp"])
        permutation_list_wtp.append(grouping["wtp"])
        permutation_name_wto.append("wtp")
        permutation_wtp = list(itertools.product(*permutation_list_wtp))

    if 'sp' in grouping:
        permutation_list_sp = copy.copy(permutation_list)
        permutation_name_sp = copy.copy(permutation_name)
        permutation_list_sp.append(["sp"])
        permutation_list_sp.append(grouping["sp"]["NumberOfGroups"])
        permutation_name_sp.append("SPGroups")
        permutation_list_sp.append(grouping["sp"]["NumberOfCommunities"])
        permutation_name_sp.append("SPCommunity")
        permutationName.append('numberOfCommunity')
        permutation_sp = list(itertools.product(*permutation_list_sp))

    # Distribution Data
    # distribution = iterable["Evaluation"]["DistributionOfVeh"]   # type of distribution
    # if 'Statistical' in distribution:
    #     permutation_list.append(distribution["Statistical"])       # type of statistical distribution
    #     permutationName.append("Statistical")
    # if 'Region' in distribution:
    #     permutation_list.append(distribution["Region"])
    #     permutationName.append("Region")

    # finally add all lists up
    all_permutations = permutation_sp + permutation_greedy + permutation_wtp + permutation_dima
    different_sets = list(itertools.product(*set_creating))

    return all_permutations, permutation_name, different_sets, road_network
