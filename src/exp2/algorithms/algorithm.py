class Algorithm(object):
    def __init__(self):
        self.vehicle_set_id = None
        self.saving_factor = None
        self.algorithm_name = type(self).__name__

    # TODO 2024 Implement create for the trace discovery algorithm
    def create(self, vehicle_set_id: int, saving_factor: float = 0) -> None:
        self.vehicle_set_id = vehicle_set_id
