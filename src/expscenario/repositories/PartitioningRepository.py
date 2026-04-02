from experimentum.Storage import AbstractRepository

class PartitioningRepository(AbstractRepository.implementation):

    """Repository for the disjointness table data."""

    __table__ = 'partitioning'
    # __relationships__ = {
    # }

    def __init__(self, new_vehicles, incentives_time, grouping_time, number_of_partitioned_vehicles, number_of_new_created_vehicles):
        """Set attributes."""
        self.new_vehicles = new_vehicles
        self.incentives_time = incentives_time
        self.grouping_time = grouping_time
        self.number_of_partitioned_vehicles = number_of_partitioned_vehicles
        self.number_of_new_created_vehicles = number_of_new_created_vehicles
