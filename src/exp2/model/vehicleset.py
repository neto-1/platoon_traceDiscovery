from model.database import Database


class VehicleSet:
    def __init__(self, set_id: int, set_type: str, set_name: str = "undef"):
        self.set_id = set_id
        self.set_type = set_type
        self.set_name = set_name

    def get_set_id(self) -> int:
        return self.set_id

    def clean_up(self) -> None:
        Database.clean_up_groups_by_vehicle_set(self.set_id)
