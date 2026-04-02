class CMD:

    road_label = "location"
    road_rel = "NEIGHBOUR"
    vehicle_set_label = "VehicleSet"
    vehicle_in_set_rel = "CONSISTS_OF"
    vehicle_label = "Vehicle"
    vehicle_start_rel = "START_AT"
    vehicle_end_rel = "END_AT"
    sp_rel_start = "SP_START"
    sp_rel_end = "SP_END"
    route_label = "RouteNodeTemp"
    incentive_label = "Incentive"
    incentive_has_rel = "HAS"
    group_label = "Group"
    in_group_rel = "IN"
    route_rel = "LOC"
    next_route_rel = "NEXT"

    location_label = "Location"
    location_rel = "LOCATION"
    location_at_rel = "LOCATED_AT"

    platoon_at_rel = "PLATOON_AT"
    platoon_route_label = "PlatoonRoute"
    platoon_route_node_label = "PlatoonRouteNode"
    platoon_via_label = "PlatoonVia"

    start_at_rel = "START_AT"
    end_at_rel = "END_AT"
    route_nodes_rel = "ROUTE_NODES"
    platoon_via_rel = "PLATOON_VIA"

    def __init__(self):
        raise NotImplementedError("static")
# class CMD:
#
#     road_label = "loc"
#     road_rel = "NEIGHBOUR"
#     vehicle_set_label = "VehicleSet"
#     vehicle_in_set_rel = "CONSISTS_OF"
#     vehicle_label = "Vehicle"
#     vehicle_start_rel = "START_AT"
#     vehicle_end_rel = "END_AT"
#     sp_rel_start = "SP_START"
#     sp_rel_end = "SP_END"
#     route_label = "RouteNodeTemp"
#     incentive_label = "Incentive"
#     incentive_has_rel = "HAS"
#     group_label = "Group"
#     in_group_rel = "IN"
#     route_rel = "LOC"
#     next_route_rel = "NEXT"
#
#     location_label = "Location"
#     location_rel = "LOCATION"
#     location_at_rel = "LOCATED_AT"
#
#     platoon_at_rel = "PLATOON_AT"
#     platoon_route_label = "PlatoonRoute"
#     platoon_route_node_label = "PlatoonRouteNode"
#     platoon_via_label = "PlatoonVia"
#
#     start_at_rel = "START_AT"
#     end_at_rel = "END_AT"
#     route_nodes_rel = "ROUTE_NODES"
#     platoon_via_rel = "PLATOON_VIA"
#
#     def __init__(self):
#         raise NotImplementedError("static")
