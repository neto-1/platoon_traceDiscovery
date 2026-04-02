from typing import Dict, List

class BasicIncentiveMethod():

    def get_incentives(self, saving: float, vehicle_set_id: int) -> Dict[int, float]:
        raise NotImplementedError("Must Override")

    def get_parameters(self) -> List[str or int or float]:
        raise NotImplementedError("Must Override")
