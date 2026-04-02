import json
import logging
import random
import time
from datetime import datetime
from typing import Tuple, Dict, List

from model.testcase import TestCase
from model.vehicleset import VehicleSet
from util.configuration import Configuration
from vehicledata.depotdistribution import DepotVehicleDistributor
from vehicledata.distributionoverlay import DistributionOverlay
from vehicledata.randomdistribution import RandomVehicleSetCreator
from vehicledata.vehiclesetroadnotes import LocationBasedVehicleSetCreator
from stat_functions.add_info import add_info


# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
blue_text = "\033[34m"
reset_text = "\033[0m"


class TestSuite:
    min_platooning_distance = -1
    max_platooning_distance = -1

    def __init__(self, test_cases: List[TestCase]):
        self.test_cases = test_cases

    @staticmethod
    def _import_json(exp_path: str) -> Tuple[
        Dict[str, int or List], Dict[str, int or List], Dict[str, List[Dict] or Dict]]:
        json_file = json.load(open(exp_path))
        data_parameters = json_file["data_parameters"]
        test_parameters = json_file["test_parameters"]
        test_methods = json_file["test_methods"]
        return data_parameters, test_parameters, test_methods

    @staticmethod
    def _generate_vehicle_sets(data_parameters: Dict[str, int or List]) -> List[VehicleSet]:
        number_of_different_exp = data_parameters["number_of_different_exp"]
        vehicle_sets_info = data_parameters["vehicle_sets_info"]

        vehicle_sets = []
        for i in range(number_of_different_exp):
            if "distributions" in vehicle_sets_info:
                distributions = vehicle_sets_info["distributions"]

                num_of_vehicles = distributions["number_of_vehicles"]
                methods = distributions["methods"]

                for num_of_vehicle in num_of_vehicles:
                    for method in methods:
                        vehicle_creator = None
                        if method == "random":
                            vehicle_creator = RandomVehicleSetCreator(num_of_vehicle, method)
                        if method == "depot":
                            vehicle_creator = DepotVehicleDistributor(num_of_vehicle, method,
                                                                      TestSuite.min_platooning_distance,
                                                                      TestSuite.max_platooning_distance)
                        if method == "poisson":
                            vehicle_creator = None
                        if method == "overlay":
                            vehicle_creator = DistributionOverlay(num_of_vehicle, method, 5)

                        vehicle_set = vehicle_creator.create()  # creates vehicle set and stores it in database
                        vehicle_sets.append(vehicle_set)

            custom_nodes = "custom_nodes"
            if custom_nodes in vehicle_sets_info:
                vehicles_infos = vehicle_sets_info[custom_nodes]
                for vehicles_info in vehicles_infos:
                    start_time = time.time()
                    vehicles_path = Configuration.exp_path + "vehicles/" + vehicles_info

                    vehicles_json = json.load(open(vehicles_path))
                    vehicle_list = vehicles_json["vehicles"]
                    logger.info(
                        f"{orange_text} As per the \"vehicle_sets_info={vehicles_info}\" parameter in \"experiment.json\", {len(vehicle_list)} vehicle(s) and their RouteNodes, will be created into a new vehicle set.{reset_text}")

                    vehicles_info_converted = []
                    for vehicle in vehicle_list:
                        vehicles_info_converted.append(tuple(vehicle))

                    vehicle_creator = LocationBasedVehicleSetCreator(vehicles_info_converted, custom_nodes,
                                                                     vehicles_info)
                    vehicle_set = vehicle_creator.create()

                    vehicle_sets.append(vehicle_set)

                    logger.info(f"{green_text}Completed vehicle generations for \"{vehicles_info}\".{reset_text}")
                    end_time = time.time()
                    # duration = (end_time - start_time).total_seconds()
                
        # DataBag.add("num_of_vehicles", num_of_vehicles[0])
        return vehicle_sets

    # TODO 2024: Continue adapting into platoon trace discovery
    # @staticmethod
    # def _get_trace_analysis(trace_analysis_config: Dict) -> Vehicle:
    #    """
    #    Creates a Vehicle object from the trace analysis configuration dictionary.

    #    :param trace_analysis_config: Dictionary containing vehicle configuration.
    #    :return: Vehicle object with the specified attributes.
    #    """
    #    name = trace_analysis_config.get("name", "DefaultName")
    #    technical_requirements = trace_analysis_config.get("technical_requirements", "DefaultTechReq")
    #    legal_requirements = trace_analysis_config.get("legal_requirements", "DefaultLegalReq")
    #    earliest_departure = trace_analysis_config.get("earliest_departure", datetime.now())
    #    latest_arrival = trace_analysis_config.get("latest_arrival", datetime.now())
    #    speed_min = trace_analysis_config.get("speed_min", 0)
    #    speed_opt = trace_analysis_config.get("speed_opt", 0)
    #    speed_max = trace_analysis_config.get("speed_max", 0)

    #    return Vehicle(name, technical_requirements, legal_requirements, earliest_departure, latest_arrival, speed_min, speed_opt, speed_max)

    @staticmethod
    def create_from_json(exp_path: str = Configuration.exp_full_path, min_platooning_distance: int = 10000,
                         max_platooning_distance: int = 1000000) -> object:
        """
        Create a TestSuite object from a JSON file.

        Args:
            exp_path (str): The path to the JSON file containing the experiment data. Defaults to Configuration.exp_full_path.
            min_platooning_distance (int): The minimum platooning distance. Defaults to 10000.
            max_platooning_distance (int): The maximum platooning distance. Defaults to 1000000.

        Returns:
            TestSuite: The created TestSuite object.
        """

        TestSuite.min_platooning_distance = min_platooning_distance
        TestSuite.max_platooning_distance = max_platooning_distance

        data_parameters, test_parameters, test_methods = TestSuite._import_json(exp_path)

        # generate vehicle sets for given experiment
        vehicle_sets = TestSuite._generate_vehicle_sets(data_parameters)
        logger.info(f"All vehicle sets specified in \"experiment.json\" have been created successfully.{reset_text}")

        number_of_same_exp = test_parameters["number_of_same_exp"]
        # DataBag.add("number_of_companies", number_of_companies)

        test_cases = []
        for vehicle_set in vehicle_sets:
            for same_experiment in range(number_of_same_exp):
                # for trace_analysis in trace_analyses:
                # TODO 2024: Adapt into platoon trace discovery
                # test_case_algorithms = [grouping_method, partitioning_method, routing_method]
                test_case_algorithms = ["trace_discovery"]
                test_case = TestCase(vehicle_set, test_case_algorithms, saving_factor=1)
                # logger.info(f"{green_text}Test case created: {test_case}{reset_text}")
                # print("Test case number: ", len(test_cases))
                test_cases.append(test_case)
                # add_info("testcase_created", f"VehicleSetID={vehicle_set.get_set_id()}", "platoon_stats.csv")
                # add_info("testcase_id11", str(len(test_cases)+ 1), "platoon_stats.csv")

        test_suite = TestSuite(test_cases)
        return test_suite

    def run(self):
        print("\n")
        print(" Test Cases Execution ".center(100, "="))
        logger.info(f"Started running the test suite with {len(self.test_cases)} test case(s){reset_text}")

        """ Shuffled test cases to account for physical effects """
        if Configuration.shuffle_test_cases:
            random.shuffle(self.test_cases)

        # if Configuration.print_vehicles:
        # Database.generate_all_vehicle_sets()

        test_case_counter = 1
        for test_case in self.test_cases:
            # DataBag.add("tc", {})
            date_time_start = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            tmpstr = f"{blue_text} Executing test case {test_case_counter} out of {len(self.test_cases)}{reset_text} "
            print(tmpstr.center(100, "+"))
            # print(f"{reset_text}Executing test case {test_case_counter} out of {len(self.test_cases)}{reset_text}...")
            start_timer_trace = datetime.now()  # Capture start time
            test_case.run()
            end_timer_trace = datetime.now()  # Capture start time
            duration = end_timer_trace - start_timer_trace  # Calculate duration
            logger.info(f"Test case {test_case_counter} complete. Execution duration: {duration}{reset_text}")
            # add_info("testcase_id2", test_case_counter, "platoon_stats.csv")
            test_case_counter = test_case_counter + 1
        logger.info(f"{green_text}Finished executing all the tests in the test suite.{reset_text}")
