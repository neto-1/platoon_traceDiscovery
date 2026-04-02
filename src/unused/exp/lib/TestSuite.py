import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import psycopg2
import platform
import json
import copy
from typing import Tuple, Dict, List
from lib.TestCase import TestCase
from lib.DataSet import DataSet

class TestSuite:
    # load the json data
    def __init__(self, tests: List[TestCase]) -> None:
        self.__tests = tests

    # add a test to the list of tests in the object
    def add_test(self, test: TestCase):
        self.__tests.append(test)

    # get the list of tests
    def get_test_obj(self):
        return self.__tests

    # get the list of instances of the tests
    def get_test_val(self):
        test_values = []
        for test in self.__tests:
            test_values.append(test.get_all_values())
        return test_values

    # this methods runs the hole process of import, instance creating, test-object creating and returning a list of those objects
    @staticmethod
    def create_from_json(json_name: str = "Evaluation") -> object:
        # import the json file and get data-parameter, test-parameter and the methods to be tested
        data_parameters, test_parameters, test_methods = TestSuite._import_json(json_name)

        # create all the different sets to be tested and create them in the database
        list_of_sets = TestSuite._create_set_instances(data_parameters)

        # create the different test-instances through the test-parameters
        tests_instances = TestSuite._create_instances(test_parameters)

        # create the different grouping and routing combinations
        methods_instances = TestSuite._create_methods(test_methods)

        # create the test-objects. every combination of test and methods should be run on each vehicle set, therefore the list of sets and the test-list as well as methods-list will be inputed
        list_of_tests = TestSuite._create_tests(list_of_sets, tests_instances, methods_instances)

        # finally produce a test suite of all tests
        return TestSuite(list_of_tests)


    # static method to import the data
    @staticmethod
    def _import_json(json_name: str = "Evaluation") -> Tuple[Dict[str, List], Dict[str, List], Dict[str, Dict[str, List]]]:
        # load the json file
        json_file = json.load(open(str(json_name) + '.json'))
        # differentiate between methods and parameters
        data_parameters = json_file["Evaluation"]["DataParameters"]
        test_parameters = json_file["Evaluation"]["TestParameter"]
        methods = json_file['Evaluation']["TestMethods"]

        # return as a tuple
        return data_parameters, test_parameters, methods


    # create all test instances for incentives
    @staticmethod
    def _create_instances(parameters: Dict[str, List]) -> List[TestCase]:

        # get the lists (or values) of all parameters from the imported json file
        slicing = parameters["SlicingMethod"]
        savings = parameters["Savings"]
        logging = parameters["Logging"]
        comparison_activated = parameters["Activated"]
        geometric_median_value = parameters["nuStrich"]
        convex_hull = parameters["convexhullparameter"]
        angle = parameters["angle"]

        # create a list of all relevant parameter and methods (in the right order)
        all_parameter_list = [slicing, savings, logging, comparison_activated, geometric_median_value, convex_hull, angle]
        # parameter_names = ["Number_of_different_exp", "number_of_vehicles", "slicing_method", "road_network", "geometric_median", "angle_of_vectors",
        # "convex_hull", "log", "grouping_methods", "savings", "routing_methods", ]

        # iterate the list and create all needed instances
        different_instances = list(itertools.product(*all_parameter_list))

        # return the list of different instances
        return different_instances

    @staticmethod
    def _create_methods(methods: Dict[str, Dict[str, List]]) -> List:
        # !!== get the different methods, which will be applied to the test instances ==!!
        # the grouping methods
        groupings_methods = methods["Grouping_Method"]
        different_grouping = TestSuite._get_method_instances(groupings_methods)

        # the routing methods
        routing_methods = methods["Routing_Method"]
        different_routing = TestSuite._get_method_instances(routing_methods)

        # add the two lists together
        grouping_and_routing_list = [different_grouping, different_routing]

        # get all combinations of the grouping and routing methods
        combination = list(itertools.product(*grouping_and_routing_list))

        return combination

    # get all instances of a dict of methods (this is used for the method part in the json file)
    @staticmethod
    def _get_method_instances(dictionary: dict) -> List[str or int or float]:

        # create empty list for all instances
        list_of_instances = []
        # iterate through the methods dictionary
        for key, value in dictionary.items():
            # create all the different instances of methods and save them into all_instances
            if not value:
                raise AttributeError("In the input file, every list should have at least one value! \n A placeholder may be used!")

            all_instances = list(itertools.product(*[[key]], value))
            # add every instance to a list (this step is needed to prevent nesting of lists)
            for single_instance in all_instances:
                list_of_instances.append(single_instance)
        return list_of_instances

    # create the tests-objects by converting the instances into tests
    @staticmethod
    def _create_tests(list_of_sets: List[DataSet], tests_instances: List[Tuple], methods_instances: List[Tuple[Tuple]]) -> List[TestCase]:
        # create empty list to fill with the test objects
        test_cases = list(itertools.product(*[tests_instances, methods_instances]))

        # create
        test_list = []
        # iterate through the list of instances
        for instance in test_cases:
            print("Actual test instance: " + str(instance))

            # convert the instance into arguments and create a test object
            # data_set_list: List[DataSet], slicing: str, saving_factor: float, saving_factor_median: float, angle_of_cos: float,
            #  type_of_hull: str, log: bool, grouping_active: bool, identify_groups_by: Tuple[str, ], routing_method: Tuple[str, ])
            test = TestCase(list_of_sets, instance[0][0], instance[0][1], instance[0][2], instance[0][3], instance[0][4], instance[0][5], instance[0][6], instance[1][0], instance[1][1])

            # save the object in the list "test_list"
            test_list.append(test)

        # return the list of tests
        return test_list

    # create a list of all sets to be created
    @staticmethod
    def _create_set_instances(data_parameters: Dict[str, List]) -> List[DataSet]:

        # make a list of the different attributes for the set creating
        data_parameter_list = [data_parameters["ExpRepetition"], data_parameters["NumberOfDifferentExp"], data_parameters["NumberOfVeh"], data_parameters["DistributionOfVeh"], data_parameters["RoadNetwork"]]

        # get all combinations of the prior list
        sets_to_create_from_tuple = list(itertools.product(*data_parameter_list))

        # create all sets from the tuple-list of data sets
        sets_list = DataSet.create_all_sets(sets_to_create_from_tuple)

        # return a list of all sets, which have to be created
        return sets_list

    # run the tests
    def run_tests(self):
        # iterate through all tests in the test suite
        for test in self.get_test_obj():
            test.run()
