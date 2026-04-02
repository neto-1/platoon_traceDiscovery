from experimentum.Storage import AbstractRepository

class RoutingRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'routing'
    # __relationships__ = {
    # }

    def __init__(self, group_ids, number_of_vehicles, objective_value):
        """Set attributes."""
        self.group_ids = [group_ids] if not isinstance(group_ids, list) else group_ids
        self.number_of_vehicles = [number_of_vehicles] if not isinstance(number_of_vehicles, list) else number_of_vehicles
        self.objective_value = [objective_value] if not isinstance(objective_value, list) else objective_value
