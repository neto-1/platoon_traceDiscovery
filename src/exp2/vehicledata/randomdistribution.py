from model.vehicleset import VehicleSet
from vehicledata.database import Database
from vehicledata.vehiclesetcreator import VehicleSetCreator


class RandomVehicleSetCreator(VehicleSetCreator):
    def __init__(self, number_of_vehicles: int, set_type: str):
        self.number_of_vehicles = number_of_vehicles
        self.set_type = set_type

    def create(self) -> VehicleSet:
        # vehicle_set_id = Database.create_random_vehicle_set(self.number_of_vehicles)
        vehicle_set_id = Database.create_random_vehicle_set_trace(self.number_of_vehicles)
        vehicle_set = VehicleSet(vehicle_set_id, self.set_type, "gen_random_" + str(self.number_of_vehicles))

        # if Configuration.print_vehicles:
        #     Database.generate_vehicles(vehicle_set_id)

        return vehicle_set
