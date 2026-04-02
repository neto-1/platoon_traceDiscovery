# interface for masterproblems
from typing import Dict, List
from columngeneration.model.vehicle import Vehicle
from columngeneration.model.route import Route


class MPInterface:

    def solve_master(self, vehicles: List[Vehicle], graph):
        raise NotImplementedError("interface")
