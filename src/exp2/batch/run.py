import sys, os
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
EXP2_DIR = CURRENT_DIR.parent
if str(EXP2_DIR) not in sys.path:
    # sys.path.append(str(EXP2_DIR))  # To prevent import errors
    exp2_dir = str(EXP2_DIR)
    sys.path.insert(0, exp2_dir)

# sys.path.append('/Users/aghiadhaloul/repos/graphdbs/platooning/src/exp2')  # To prever import errors
from util.databasecontainer import DatabaseContainer
from model.testsuite import TestSuite
from util.databag import DataBag
from util.configuration import Configuration
import traceback
import time
import sys
import os
import logging
import datetime
from stat_functions.add_info import add_info
from stat_functions import stats_path
from vehicledata.database import Database
from model.database import Database   


# To activate the virtual environment in Windows PowerShell, use the following command:
# .venv\Scripts\activate 

# To set the PYTHONPATH in Windows PowerShell, use the following command:
# $env:PYTHONPATH = "C:\Users\ThinkPad-T470\Desktop\School_TU\Hiwi_position\platoon_traceD\src\exp2"


# Logging with formatting (to print out the error messages in red)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
red_text = "\033[91m"
reset_text = "\033[0m"


def main():
    start_experiment_time = datetime.datetime.now()
    print(" Initialization and Bootstrap ".center(100, "="))
    if not hasattr(Configuration, 'db_road_networks') or not Configuration.db_road_networks:
        error_message = (
            f"{red_text}\n{'*' * 60}\n"
            "Configuration error: 'db_road_networks' is missing or empty.\n"
            "POSSIBLE CAUSES: 'db_road_networks' in \"configuration.py\" was not set up correctly.\n"
            "Exiting...\n"
            f"{'*' * 60}{reset_text}\n"
        )
        logger.error(error_message)
        exit()

    for road_network in Configuration.db_road_networks:
        try:
            DatabaseContainer.launch(road_network[0], db_output_flag=True)
            # we call database.count_road_points & database.count_road_segments and insert the total RoadPoints nodes and RoadSegments edges in the testcase stats
            testcase_name_path = stats_path.stats_folder
            testcase_name = os.path.basename(testcase_name_path) if testcase_name_path else "N/A"
            add_info("testcase_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S"), "testcase_stats.csv")
            add_info("testcase_name", testcase_name, "testcase_stats.csv")
            number_of_road_points = Database.count_road_points()
            add_info("total_road_points", number_of_road_points, "testcase_stats.csv")
            number_of_road_segments = Database.count_road_segments()
            add_info("total_road_segments", number_of_road_segments, "testcase_stats.csv")
        except Exception as e:
            # Logging the full content of road_network[0] along with the error message
            error_message = (
                f"{red_text}\n\n{'*' * 60}\n"
                f"An error occurred while launching the DB container.\n"
                f"POSSIBLE CAUSES: You have not started the Docker daemon, the port is already in use, or you did not specify the target platform.\n"
                f"EXCEPTION DETAILS: {e}\n"
                f"{'*' * 60}{reset_text}\n"
            )

            # Logging the error message in red
            logger.error(error_message)
            exit()
            # print(f"* An error occurred while launching the DB Container: {e}")
        start_time = time.time()
        """ Clean up  Incentives, Platoons, Groups  """
        # NOTE: The cleaning up has been removed since it sometimes causes a crash (like when there is nothing to clean up).
        # TODO: clean_up should properly handle the case when there is nothing to clean up.
        # Database.clean_up()
        # DatabaseAlgo.clean_cached_shortest_paths()
        # Database.remove_unconnected_road_nodes()
        # ------------------------------------------------------------------------------------------
        # NOTE: The minimum and maximum platooning distances are not relevant to the platoon trace discovery problem.
        # They are added here to maintain the TestSuite structure. The values are defined in RoadNetworks in util/configuration.py.
        print("")
        print(" Vehicle Loading and Route Creation ".center(100, "="))
        test_suite = TestSuite.create_from_json(min_platooning_distance=road_network[1],
                                                max_platooning_distance=road_network[2])

        # NOTE: The timers and databag are not in use in the platoon trace discovery problem.
        preparation_time = time.time() - start_time
        DataBag.add("preparation_time", preparation_time)

        try:
            # Note: this is where the main execution of the test cases happens.
            test_suite.run()
        except Exception:
            print("Unexpected error:", sys.exc_info()[0])
            logging.error(traceback.format_exc())
        end_experiment_time = datetime.datetime.now()
        duration_experiment = (end_experiment_time - start_experiment_time).total_seconds()
        add_info("testcase_duration", duration_experiment, "testcase_stats.csv")

        return


if __name__ == "__main__":
    main()
