import sys

# sys.path.append('/Users/aghiadhaloul/repos/graphdbs/platooning/src/exp2')  # To prever import errors
from stat_functions.add_info import add_info
from stat_functions.platoon_stats import add_platoon_stat
from algorithms.algorithm import Algorithm
# from algorithms.database import Database
from algorithms.trace_discovery.database import Database
# from datetime import time
import time
import datetime
# from datetime import datetime
import logging

# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"


class TraceDiscovery(Algorithm):
    # One can directly run this (without the automation framwork). Only a vehicle set id is nneded. Refer to main at the bottom.
    def __init__(self, uri, user, password):
        super(TraceDiscovery, self).__init__()
        self.algorithm_name = "TraceDiscovery"
        self.db_instance = Database(uri, user, password)

    def create(self, vehicle_set_id: int) -> None:
        # Outdated, go to test_discover_platoons
        super(TraceDiscovery, self).create(vehicle_set_id)

        logger.info(f"{green_text}Start trace discovery routes with {self.algorithm_name}.{reset_text}")

        start_time = time.time()
        retrieve_data_from_store_time = time.time() - start_time

        start_time = time.time()
        vehicle_set_ids = [137364, 138086]  # 2, 4 vehicles
        for vehicle_set_id in vehicle_set_ids:
            platoons = Database.discover_platoons(vehicle_set_id)

        calculation_time = time.time() - start_time

        start_time = time.time()
        self.store_platoon_traces(platoons)
        store_time = time.time() - start_time

        # Load data from DB and store data to DB time
        store_time = store_time + retrieve_data_from_store_time

        logger.info(
            f"{green_text}Platoon trace was calculated in {calculation_time} seconds with {self.algorithm_name} and stored in {store_time}.{reset_text}")

    def test_discover_platoons(self, exp2_vehicle_set_id):
        vehicle_sets = {
            "vehicle_set_bay_2_tiny_platoon": 173758,
            "vehicle_set_bay_3_tiny_platoon": 0,
            "vehicle_set_bay_4_tiny_platoon": 0,
            "vehicle_set_bay_5_tiny_platoon": 0,
            "bay_2_platoon_possible": 132504,
            "bay_3_platoon_possible": 134467,
            "bay_30": 126624,
            "swe_10": 1168278  # has origin and destination
        }
        # trace = self.db_instance.discover_platoons_python(135595) # 2 vehicles
        if exp2_vehicle_set_id is None:
            raise Exception("exp2_vehicle_set_id to be processed by the trace discovery prototype is None")
            vehicle_set = vehicle_sets["bay_30"]
        else:
            vehicle_set = exp2_vehicle_set_id

        start_timer_trace = time.time()  # Capture start time
        # NOTE: The heavy lifting is done here
        traces_set, traces_details = self.db_instance.discover_platoons_python(vehicle_set)
        # print("Trace set from algo***:", traces_set)
        # print("Trace_details from algo++++:",traces_details)
        end_timer_trace = time.time()  # Capture end time
        duration = end_timer_trace - start_timer_trace  # Calculate duration
        # add_info("platoon_duration1", str(duration), "platoon_stats.csv")
        # print(f">>>>>>>>>>>>>>>>>>>> >>>>>>>>>>>>>>>>>>> discover_platoons_python duration: {duration}")  # Print duration

        # print(f"Found {len(traces_set)} trace(s) for vehicle_set ({vehicle_set}) = ", traces_set)
        logger.info(
            f"{green_text}Generated {len(traces_set)} platoon trace(s) for :VehicleSet (<id>={vehicle_set}): {traces_set}{reset_text}")
        # for key, value in traces_details.items():  # Use .items() to get both keys and values
        print(f"{orange_text}Trace(s) details:{reset_text}")
        for key, value in sorted(traces_details.items(), key=lambda item: len(item[1]), reverse=True):
            add_info("platoon_id", key, "platoon_stats.csv")
            add_info("number_of_events", len(value), "platoon_stats.csv")
            add_info("vehicle_set", vehicle_set, "platoon_stats.csv")
            add_info("test_case_duration_time", duration, "platoon_stats.csv")
            print(f"\t{orange_text}Trace {key} has {len(value)} events.{reset_text}")

        # The visualization command
        traces_str = " ".join(str(trace_id) for trace_id in traces_set)  # Join traces into a string

        visualization_command = f"python3 visualizer.py --vehicle_set_id {vehicle_set} --platoon_ids {traces_str}"

        # Print the visualization command to the user
        print(
            f"{green_text}\nVISUALIZATION HINT:{reset_text} To visualize the generated platoon traces for this test case, run the following command:")
        print(
            f"(First, please cd into the correct directory. It should be /exp2/algorithms/trace_discovery/map_visualization/)")
        print(f"{orange_text}{visualization_command}{reset_text}\n")

        return

# uncomment these lines if you are executing this file algorithm.py directly as a script
# trace_discovery = TraceDiscovery("bolt://localhost:7687", "neo4j", "12345678")
# trace_discovery.test_discover_platoons(1168278)
