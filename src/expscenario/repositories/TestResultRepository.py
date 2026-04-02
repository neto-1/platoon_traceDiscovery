from experimentum.Storage import AbstractRepository
from repositories.AlgorithmsRepository import AlgorithmsRepository

class TestResultRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'test_results'
    __relationships__ = {
        'algorithms': [AlgorithmsRepository]
    }

    def __init__(self, saving_factor, vehicle_set_type, vehicle_set_size, shortest_path_savings):
        """Set attributes."""
        self.saving_factor = saving_factor
        self.vehicle_set_type = vehicle_set_type
        self.vehicle_set_size = vehicle_set_size
        self.shortest_path_savings = shortest_path_savings