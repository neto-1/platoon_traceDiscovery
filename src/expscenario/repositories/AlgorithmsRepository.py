from experimentum.Storage import AbstractRepository
from repositories.IncentivesRepository import IncentivesRepository
from repositories.GroupingRepository import GroupingRepository
from repositories.RoutingRepository import RoutingRepository
from repositories.DisjointnessRepository import DisjointnessRepository
from repositories.PartitioningRepository import PartitioningRepository
import datetime

class AlgorithmsRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'algorithms'
    __relationships__ = {
        'incentives': [IncentivesRepository],
        'grouping': [GroupingRepository],
        'routing': [RoutingRepository],
        'disjointness': [DisjointnessRepository],
        'partitioning': [PartitioningRepository]

    }

    def __init__(self, method, calculation_time, store_time, time, parameters = None):
        """Set attributes."""
        self.method = method
        self.calculation_time = calculation_time
        self.store_time = store_time
        self.time = time
        self.parameters = parameters
        self.executed_at = datetime.datetime.now()