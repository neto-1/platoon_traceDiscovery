# interface for sub problems
from columngeneration.model.vehicle import Vehicle
from neo4jrestclient.client import GraphDatabase
from columngeneration.model.route import Route
from typing import Dict, Tuple, List


class SPInterface:

    def get_path(self, shadow_prizes: Dict[Tuple[int, int], float], vehicles: List[Vehicle], graph: GraphDatabase) -> bool:
        raise NotImplementedError("interface")
