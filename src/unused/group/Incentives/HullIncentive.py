import subprocess
from neo4jrestclient.client import GraphDatabase
import yaml
import json
from typing import Tuple, Dict, List
from basicincentivemethod import BasicIncentiveMethod


class HullIncentives(BasicIncentiveMethod):

    # get the median incentive values
    @staticmethod
    def get_incentives(savings:float=0.1, set_id: int=0, type_of_hull: str="convexHull", get_polygons: bool=True) -> Dict[Tuple[int, int], float]:
        """
        Get the incentives for the hull-comparisons of the vehicles (convexHull, eclipse)
        :param savings: the amount of savings applied
        :param set_id: the id of the vehicle set
        :param type_of_hull: the type of hull to be applied on every vehicle (e.g. convexHull, eclipse,...)
        :param get_polygons: indicating, if the output should include the polygons itself or not
        :return: unordered list of incentive values as follows: [id_veh_1, id_veh_2, incentive_value]
        """

        # define the input for the R procedure
        cmd = 'Rscript ' + 'R_lib/Convex_Hull.r' + " " + str(savings) + " " + str(set_id) + " " + str(type_of_hull) + " " + str(get_polygons)

        # call R to calculate incentives of the given instance
        incentive_median = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # wait for R to finish
        incentive_median.wait()

        # retrieve the list from the process "incentive_median"
        list_of_hull_values = HullIncentives._get_process_return_value(incentive_median)

        # format the output
        hull_incentives = {}
        for incentive_pair in list_of_hull_values:
            hull_incentives[(incentive_pair[0], incentive_pair[1])] = incentive_pair[2]

        return hull_incentives

    # function to receive and format output
    @staticmethod
    def _get_process_return_value(process, verbose=False):
        """
        Get the return value of process (i.e. the last print statement)
        :param process: The process returned from subprocess.popen
        :param verbose: Whether or not the output of the process should be printed
        """
        output = None

        # poll will return the exit code if the process is completed otherwise it returns null
        while process.poll() is None or process.poll() == 0:
            line = process.stdout.readline()

            if not line:
                break
            output = line  # last print statement
            if verbose:
                print(line.rstrip().decode('utf-8'))

        return json.loads(output)  # parse JSON




#### HOW TO USE!!!
# get the values for example with this line:
values = HullIncentives.get_incentives(0.1, 8674, "convexHull")

print(values)
