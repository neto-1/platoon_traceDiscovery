import subprocess
from neo4jrestclient.client import GraphDatabase
import yaml
import json
from typing import Tuple, Dict, List


class MedianIncentives:

    # get the median incentive values
    @staticmethod
    def get_incentives(savings: float, set_id: int, median_savings: float) -> Dict[Tuple[int, int], float]:
        """
        Get the incentives for geometric median approach of the vehicles
        :param savings: the amount of savings for platooning
        :param set_id: the id of the vehicle set
        :param median_savings: the amount of savings for the air distances
        :return: unordered list of incentive values as follows: [id_veh_1, id_veh_2, incentive_value]
        """

        # define the input for R
        cmd = 'Rscript ' + 'R_lib/Geometric_Median.r' + " " + str(savings) + " " + str(set_id) + " " + str(median_savings)

        # call R to calculate incentives of the given instance
        incentive_median = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        # wait for R to finish
        incentive_median.wait()
        # retrieve the list from the process "incentive_median"
        list_of_median_values = MedianIncentives._get_process_return_value(incentive_median)

        # format the output
        geometric_median_incentives = {}
        for incentive_pair in list_of_median_values:
            geometric_median_incentives[(incentive_pair[0], incentive_pair[1])] = incentive_pair[2]

        return geometric_median_incentives

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

