from gurobipy import *
from typing import List, Dict, Tuple


class LPModel:
    def __init__(self, model: Model):
        self._model = model
        self._relaxed_model = None
        self._variables = None
        self._constraints = None

    def get_model(self) -> Model:
        return self._model

    def store_relax(self, model: Model) -> None:
        self._relaxed_model = model
        print(model)

    def get_relaxed(self) -> Model:
        return self._relaxed_model

    def store_variables(self, variables: List[Dict]) -> None:
        self._variables = variables

    def store_constraints(self, constraints: List[Dict]) -> None:
        self._constraints = constraints

    def get_variables(self):
        return self._variables

    def get_constraints(self):
        return self._constraints

    def get_shadow_prizes(self):
        for list in self._constraints:
            print("start list ")
            print("whole list: " + str(list))
            for veh_id, edge in list.items():
                print(veh_id)
                print(edge)
                # print(constraint)
                pass
            print("end list")
