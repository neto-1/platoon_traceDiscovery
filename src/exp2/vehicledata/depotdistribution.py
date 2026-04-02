from model.vehicleset import VehicleSet
from vehicledata.database import Database
from vehicledata.vehiclesetcreator import VehicleSetCreator


class DepotVehicleDistributor(VehicleSetCreator):
    def __init__(self, number_of_vehicles: int, set_type: str, min_platooning_distance: int,
                 max_platooning_distance: int):
        self.number_of_vehicles = number_of_vehicles
        self.set_type = set_type
        self.min_platooning_distance = min_platooning_distance
        self.max_platooning_distance = max_platooning_distance

    def create(self) -> VehicleSet:
        vehicle_set_id = Database.create_depot_vehicle_set(self.number_of_vehicles, self.min_platooning_distance,
                                                           self.max_platooning_distance)
        vehicle_set = VehicleSet(vehicle_set_id, self.set_type, "gen_depot_" + str(self.number_of_vehicles))

        # if Configuration.print_vehicles:
        #     Database.generate_vehicles(vehicle_set_id)

        return vehicle_set
