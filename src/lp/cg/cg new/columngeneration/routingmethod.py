from algorithm.algorithm import Algorithm


class RoutingMethod(Algorithm):

    def create(self, savings: float, vehicle_set_id: int) -> None:
        raise NotImplementedError("interface")

    def stringify(self) -> str:
        raise NotImplementedError("Interface")
