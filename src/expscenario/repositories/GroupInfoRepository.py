from experimentum.Storage import AbstractRepository

class GroupInfoRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'group_info'
    # __relationships__ = {
    # }

    def __init__(self, group_id_neo, incentives_avg, angle_incentives_avg, median_incentives_avg, hull_incentives_avg, group_edges, group_nodes,
                 number_of_vehicles, group_polygon_coords, group_polygon_area, group_polygon_non_convex_coords, group_polygon_non_convex_area, selected):
        """Set attributes."""
        self.group_id_neo = group_id_neo
        self.incentives_avg = incentives_avg
        self.angle_incentives_avg = angle_incentives_avg
        self.median_incentives_avg = median_incentives_avg
        self.hull_incentives_avg = hull_incentives_avg
        self.group_edges = group_edges
        self.group_nodes = group_nodes
        self.number_of_vehicles = number_of_vehicles
        self.group_polygon_coords = group_polygon_coords
        self.group_polygon_area = group_polygon_area
        self.group_polygon_non_convex_coords = group_polygon_non_convex_coords
        self.group_polygon_non_convex_area = group_polygon_non_convex_area
        self.selected = selected