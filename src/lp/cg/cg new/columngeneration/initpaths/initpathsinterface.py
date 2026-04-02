from columngeneration.model.vehicle import Vehicle
from typing import List


class InitPathsInterface:

    def init_paths(self, vehicles: List[Vehicle]) -> int:
        raise NotImplementedError("Must Override")
