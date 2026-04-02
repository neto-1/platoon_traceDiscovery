import logging
import time
from typing import List

from algorithms.algorithm import Algorithm
from algorithms.trace_discovery.algorithm import TraceDiscovery
from model.database import Database
from model.vehicleset import VehicleSet

# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"


class TestCase:
    def __init__(self, vehicle_set: VehicleSet, algorithms: List[Algorithm], saving_factor: float):
        # TODO 2024: Adapt into platoon trace discovery
        """
        :param algorithms: the order must be observed
        """
        self.vehicle_set = vehicle_set
        self.algorithms = algorithms
        self.saving_factor = saving_factor

    def run(self):
        # TODO 2024: Adapt into platoon trace discovery
        # self.vehicle_set.clean_up()
        # print("running test case...")
        start_time = time.time()
        Database.clean_up_filters(False)
        Database.clean_up_routes(False)
        Database.clean_up_groups(False)
        Database.clean_up_platoons(False)
        Database.clean_up_incentives(False)

        # DataBag.add("tc.vehicle_set_id", self.vehicle_set.set_id)
        # DataBag.add("tc.vehicle_set_type", self.vehicle_set.set_name)
        # DataBag.add("tc.saving_factor", self.saving_factor)

        # Trace discovery doesnt really need this since its just one algorithm.
        # for algorithm in self.algorithms:
        #    algorithm.create(self.vehicle_set.get_set_id())
        prototype = TraceDiscovery("bolt://localhost:7687", "neo4j", "12345678")
        prototype.test_discover_platoons(self.vehicle_set.get_set_id())

        # vehicle_paths = Database.get_vehicles_shortest_path_by_set_id(self.vehicle_set.get_set_id()) # 2024, doesnt seem relevant

        """ Shortest Path Platooning Routing without ILP  """
        # shortest_path_platooning_distance_wo_ilp = Analytics.calculate_platooning_shortest_path_routes(self.saving_factor, vehicle_paths)
        #
        # print(" Analytics without ILP ".center(100, "="))
        # print(shortest_path_platooning_distance_wo_ilp)

        """ Shortest Path Platooning Routing with ILP  """
        # shortest_path_platooning_distance, platooning_routes = Analytics.calculate_platooning_shortest_path_routes_ilp(self.saving_factor, vehicle_paths)
        # print(" Analytics with ILP ".center(100, "="))

        # shortest_path_distance = 0 # 2024, doesnt seem relevant
        # for vehicle_path in vehicle_paths:# 2024, doesnt seem relevant
        #    shortest_path_distance = shortest_path_distance + vehicle_path[1] # 2024, doesnt seem relevant

        """ Number of vehicles in vehicle set can be changed by some algorithm e.g. partitioning """
        # number_of_vehicles = Database.get_number_of_vehicles(self.vehicle_set.get_set_id()) # 2024, doesnt seem relevant
        # DataBag.add("tc.vehicle_set_size", number_of_vehicles) # 2024, doesnt seem relevant
        # DataBag.add("tc.shortest_path_savings", shortest_path_platooning_distance_wo_ilp)

        # calculation_time = time.time() - start_time # 2024, doesnt seem relevant
        # DataBag.add("tc.calculation_time", calculation_time) # 2024, doesnt seem relevant
        # print(calculation_time, shortest_path_platooning_distance, shortest_path_distance, ((shortest_path_distance - shortest_path_platooning_distance) * 100) / shortest_path_distance )
        # print("get paths", store_time)
