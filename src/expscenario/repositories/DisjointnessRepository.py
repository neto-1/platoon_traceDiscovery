from experimentum.Storage import AbstractRepository

class DisjointnessRepository(AbstractRepository.implementation):

    """Repository for the disjointness table data."""

    __table__ = 'disjointness'
    # __relationships__ = {
    # }

    def __init__(self, distance_savings, shortest_path_distances, savings, optimized_savings):
        """Set attributes."""
        self.distance_savings = distance_savings
        self.shortest_path_distances = shortest_path_distances
        self.savings = savings
        self.optimized_savings = optimized_savings
