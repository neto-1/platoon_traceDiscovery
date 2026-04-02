from experimentum.Experiments import Experiment

from util.databasecontainer import DatabaseContainer
from model.testsuite import TestSuite
from model.database import Database
from util.databag import DataBag
import pprint
import json
from batch.run import main

class PlatooningExperiment(Experiment):

    """Sample Experiment which just adds random numbers to a list."""

    def reset(self):
        """Reset data structured and values used in each test run."""
        # self.my_list = []
        # self.range = range(0, 1235)
        pass

    def run(self):
        return main()
