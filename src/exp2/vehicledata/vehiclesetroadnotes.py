from typing import Tuple, List

from model.vehicleset import VehicleSet
from vehicledata.database import Database
from vehicledata.vehiclesetcreator import VehicleSetCreator


class LocationBasedVehicleSetCreator(VehicleSetCreator):
    def __init__(self, vehicle_location_ids: List[Tuple[int, int]], set_type: str, vehicles_info: str):
        self.vehicle_location_ids = vehicle_location_ids
        self.set_type = set_type
        self.vehicles_info = vehicles_info

    def create(self) -> VehicleSet:
        vehicle_set_id = Database.create_vehicle_set_by_location_ids_trace(self.vehicle_location_ids)
        # todo temp
        # Database.number_of_vehicles(vehicle_set_id)
        vehicle_set = VehicleSet(vehicle_set_id, self.set_type, self.vehicles_info)
        return vehicle_set
