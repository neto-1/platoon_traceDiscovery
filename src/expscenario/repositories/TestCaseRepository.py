from experimentum.Storage import AbstractRepository
from repositories.PerformanceRepository import PerformanceRepository
from repositories.TestResultRepository import TestResultRepository

class TestCaseRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'testcases'
    __relationships__ = {
        'performances': [PerformanceRepository],
        'test_result': [TestResultRepository]
    }

    def __init__(self, avg_road_point_degree, number_of_edges, number_of_road_points, iteration, experiment_id=None):
        """Set attributes."""
        self.iteration = iteration
        self.experiment_id = experiment_id
        self.avg_road_point_degree = avg_road_point_degree
        self.number_of_edges = number_of_edges
        self.number_of_road_points = number_of_road_points
