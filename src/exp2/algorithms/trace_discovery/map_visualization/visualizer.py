# Import necessary libraries
import argparse
import datetime
import logging
import os
import random

import folium
import numpy as np
from folium.plugins import Search
from neo4j import GraphDatabase

# TODO: Split visualizer.py into smaller files.

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"


# Parse terminal arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a map with vehicle routes and platoon events.")

    parser.add_argument(
        "--vehicle_set_id",
        type=int,
        help="ID of the vehicle set to use for route fetching."
    )

    parser.add_argument(
        "--platoon_ids",
        type=int,
        nargs='*',  # This allows multiple platoon IDs to be passed
        help="List of platoon IDs to visualize (separated by spaces)."
    )

    args = parser.parse_args()
    return args


class RoadMapExporter:
    """
    A class that exports road map data from a graph database.

    Args:
        uri (str): The URI of the graph database.
        user (str): The username for authentication.
        password (str): The password for authentication.
    """

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Closes the connection to the graph database.
        """
        self.driver.close()

    def fetch_vehicle_route_points(self, vehicle_set_ids):
        """
        Fetches route points for a specific vehicle set.

        Args:
            vehicle_set_ids (list): A list of vehicle set IDs.

        Returns:
            dict: A dictionary containing the route points for each vehicle in the set.
                The keys are the vehicle IDs and the values are dictionaries with the following keys:
                - "route_points": A list of dictionaries representing the route points, each containing
                  the latitude, longitude, and OSM ID.
                - "origin_point": A dictionary representing the origin point, containing the latitude,
                  longitude, and OSM ID.
                - "destination_point": A dictionary representing the destination point, containing the
                  latitude, longitude, and OSM ID.
        """
        with self.driver.session() as session:
            # Query to fetch route points for a specific vehicle
            route_query = """
            MATCH (vs:VehicleSet)-[:CONSISTS_OF]->(v:Vehicle)-[:IS_ROUTED_BY]->(rn:RouteNode)
            WHERE id(vs)=$vehicle_set_id
            MATCH (rn)-[:IS_AT]->(rd:RoadPoint)
            OPTIONAL MATCH (v)-[:ORIGIN]->(o:RoadPoint)
            OPTIONAL MATCH (v)-[:DESTINATION]->(d:RoadPoint)
            RETURN id(v) AS vehicle_id, 
                collect({lat: rd.lat, lon: rd.lon, osm_id: rd.osm_id}) AS route_points,
                collect(distinct {lat: o.lat, lon: o.lon, osm_id: o.osm_id})[0] AS origin_point,
                collect(distinct {lat: d.lat, lon: d.lon, osm_id: d.osm_id})[0] AS destination_point
            """

            result = session.run(route_query, vehicle_set_id=vehicle_set_ids)
            route_points_by_vehicle = {}
            for record in result:
                route_points_by_vehicle[record["vehicle_id"]] = {
                    "route_points": record["route_points"],
                    "origin_point": record["origin_point"],
                    "destination_point": record["destination_point"]
                }
            return route_points_by_vehicle

    def fetch_road_segments_and_nodes(self):
        """
        Fetches road segments and nodes from the graph database.

        Returns:
            tuple: A tuple containing two lists:
                - The first list contains dictionaries representing the road segments, each containing
                  the start and end node information, road segment ID, and distance in meters.
                - The second list contains dictionaries representing the unique nodes, each containing
                  the node ID, OSM ID, latitude, longitude, and labels.
        """
        with self.driver.session() as session:
            # Fetch road segments and nodes with labels
            segment_query = """
            MATCH (n)-[r:ROAD_SEGMENT]->(m)
            RETURN n.osm_id AS start_osm_id, ID(n) AS start_node_id, n.lon AS start_lon, n.lat AS start_lat, 
                labels(n) AS start_labels, m.osm_id AS end_osm_id, ID(m) AS end_node_id, m.lon AS end_lon, 
                m.lat AS end_lat, labels(m) AS end_labels, ID(r) AS road_segment_id, r.distance_meter AS distance_meter
            """
            segment_result = session.run(segment_query)
            segments = []
            nodes = {}

            for record in segment_result:
                # Create segments with start and end node information
                segments.append({
                    "start": {
                        "node_id": record["start_node_id"],
                        "osm_id": record["start_osm_id"],
                        "lon": record["start_lon"],
                        "lat": record["start_lat"],
                        "labels": record["start_labels"]
                    },
                    "end": {
                        "node_id": record["end_node_id"],
                        "osm_id": record["end_osm_id"],
                        "lon": record["end_lon"],
                        "lat": record["end_lat"],
                        "labels": record["end_labels"]
                    },
                    "road_segment_id": record["road_segment_id"],
                    "distance_meter": record["distance_meter"]
                })

                # Collect unique nodes and their labels
                start_osm_id = record["start_osm_id"]
                end_osm_id = record["end_osm_id"]
                if start_osm_id not in nodes:
                    nodes[start_osm_id] = {
                        "node_id": record["start_node_id"],
                        "osm_id": start_osm_id,
                        "lon": record["start_lon"],
                        "lat": record["start_lat"],
                        "labels": record["start_labels"]
                    }
                if end_osm_id not in nodes:
                    nodes[end_osm_id] = {
                        "node_id": record["end_node_id"],
                        "osm_id": end_osm_id,
                        "lon": record["end_lon"],
                        "lat": record["end_lat"],
                        "labels": record["end_labels"]
                    }

            # Return both segments and a list of unique nodes with labels
            return segments, list(nodes.values())

    def fetch_platoon_events_by_ids(self, platoon_ids):
        """
        Fetches platoon events by their IDs.

        Args:
            platoon_ids (list): A list of platoon IDs.

        Returns:
            dict: A dictionary containing the platoon events for each platoon.
                The keys are the platoon IDs and the values are dictionaries with the following keys:
                - The relationship type as the key, and a list of dictionaries representing the event points
                  as the value. Each event point dictionary contains the latitude and longitude.
        """
        events_by_platoon = {}
        with self.driver.session() as session:
            for platoon_id in platoon_ids:
                platoon_event_query = """
                MATCH (p:Platoon)-[r]->(pe:PlatoonEvent)-[:HAPPENS_AT]->(rn:RouteNode)-[:IS_AT]->(rp:RoadPoint)
                WHERE id(p) = $platoon_id
                RETURN type(r) AS relationship_type, collect({lat: rp.lat, lon: rp.lon}) AS event_points
                """
                result = session.run(platoon_event_query, platoon_id=platoon_id)
                events_by_type = {}
                for record in result:
                    event_type = record["relationship_type"]
                    if event_type not in events_by_type:
                        events_by_type[event_type] = set()
                    # Convert event points to tuples and add to set for uniqueness
                    events_by_type[event_type].update((ep['lat'], ep['lon']) for ep in record["event_points"])
                # Convert sets back to list of dicts for the final structure
                events_by_platoon[platoon_id] = {etype: [{'lat': lat, 'lon': lon} for lat, lon in points] for
                                                 etype, points in events_by_type.items()}
        return events_by_platoon


def plot_road_segments(map_obj, segments):
    color_dg = '#424242',  # Dark Gray for good visibility
    for segment in segments:
        start = [segment["start"]["lat"], segment["start"]["lon"]]
        end = [segment["end"]["lat"], segment["end"]["lon"]]
        polyline = folium.PolyLine([start, end], color=color_dg, weight=2, opacity=0.8)  # , fill_opacity=0.3)
        popup_text = f"Segment from OSM ID: {segment['start']['osm_id']} (Neo4j Node ID: {segment['start']['node_id']}) to OSM ID: {segment['end']['osm_id']} (Neo4j Node ID: {segment['end']['node_id']})<br>Neo4j Road Segment ID: {segment['road_segment_id']}<br>Distance (m): {segment['distance_meter']} meters"
        polyline.add_child(folium.Popup(popup_text))
        map_obj.add_child(polyline)


def identify_shared_nodes(vehicle_route_points):
    node_appearances = {}
    for vehicle_id, points in vehicle_route_points.items():
        for point in points:
            osm_id = point['osm_id']
            node_appearances[osm_id] = node_appearances.get(osm_id, 0) + 1
    shared_nodes = {osm_id for osm_id, count in node_appearances.items() if count > 1}
    print("len(shared_nodes): ", len(shared_nodes))
    return shared_nodes


def plot_nodes(map_obj, nodes, shared_nodes):
    """
    Plot nodes on a map object.

    Args:
        map_obj (folium.Map): The map object to plot the nodes on.
        nodes (list): A list of node objects.
        shared_nodes (list): A list of shared node IDs (appearing in multiple vehicles routes. Was used before platoon data was available to view expected platoons)

    Returns:
        None
    """
    color_teal = '#00796B',  # Teal for a bit of color

    for node in nodes:
        osm_id = node['osm_id']
        node_tooltip_text = f"(Neo4j Node ID: {node['node_id']})<br>OSM ID: {node['osm_id']}<br>Type: {', '.join(node['labels'])}"
        node_popup_text = f"(Neo4j Node ID: {node['node_id']})<br>OSM ID: {node['osm_id']}<br>Latitude: {node['lat']}<br>Longitude: {node['lon']}"
        if osm_id in shared_nodes:
            print("shared node osm_id: ", osm_id)
            # Shared nodes visualization
            marker = folium.CircleMarker(
                location=[node["lat"], node["lon"]],
                radius=5,
                color='yellow',
                fill=True,
                fill_color='yellow',
                opacity=2,
                fill_opacity=2,
                tooltip=node_tooltip_text
            ).add_to(map_obj)
        else:
            # Unique nodes visualization
            marker = folium.CircleMarker(
                location=[node["lat"], node["lon"]],
                radius=1,
                color=color_teal,
                fill=True,
                fill_color=color_teal,
                opacity=0.05,
                fill_opacity=0.05,
                tooltip=node_tooltip_text
            ).add_to(map_obj)

        # Add a popup that can be clicked to show more info
        marker.add_child(folium.Popup(node_popup_text))
        marker.add_to(map_obj)


def randomize_location(lat, lon, meters=1):
    """
    Randomizes the location by approximately 'meters'.
    This is done since multiple vehicle routes and platoon events happening at the same location and are difficult to distinguish.
    """
    # meters = 1
    delta_lat = random.uniform(-1, 1) * (meters / 111000)  # Random value between -1 and 1 meter
    delta_lon = random.uniform(-1, 1) * (meters / (111000 * np.cos(lat * (np.pi / 180))))
    return lat + delta_lat, lon + delta_lon


def plot_vehicle_routes(map_obj, vehicle_route_points):
    """
    Plot the routes of vehicles on a map.

    Args:
        map_obj (folium.Map): The folium map object to plot the routes on.
        vehicle_route_points (dict): A dictionary containing the route information for each vehicle.
            The keys are the vehicle IDs, and the values are dictionaries with the following keys:
            - 'route_points': A list of route points, where each point is a dictionary with 'lat' and 'lon' keys.
            - 'origin_point': The origin point of the route, as a dictionary with 'lat' and 'lon' keys.
            - 'destination_point': The destination point of the route, as a dictionary with 'lat' and 'lon' keys.

    Returns:
        None
    """
    # Predefined complementary vehicle colors (in HEX)
    vehicle_colors = [
        '#1f77b4',  # Muted blue
        '#ff7f0e',  # Muted orange
        '#2ca02c',  # Muted green
        '#d62728',  # Muted red
        '#9467bd',  # Muted purple
        '#8c564b',  # Muted brown
        '#e377c2',  # Muted pink
        '#7f7f7f',  # Muted gray
        '#bcbd22',  # Lime green
        '#17becf'  # Light teal
    ]
    for idx, (vehicle_id, route_info) in enumerate(vehicle_route_points.items()):
        hex_color = vehicle_colors[idx % len(vehicle_colors)]
        points = route_info["route_points"]
        origin = route_info["origin_point"]
        destination = route_info["destination_point"]

        # Plot each route point only if it's not the origin or destination
        for point in points:
            lat_, lon_ = randomize_location(point["lat"], point["lon"], 5)
            if (origin is None or (point["lat"], point["lon"]) != (origin["lat"], origin["lon"])) and \
                    (destination is None or (point["lat"], point["lon"]) != (destination["lat"], destination["lon"])):
                folium.CircleMarker(
                    location=[lat_, lon_],
                    radius=10,
                    color=hex_color,
                    fill=True,
                    fill_color=hex_color,
                ).add_to(map_obj)

        # Plot origin point
        if origin:
            randomized_origin_lat, randomized_origin_lon = randomize_location(origin["lat"], origin["lon"], 10)
            folium.RegularPolygonMarker(
                location=[randomized_origin_lat, randomized_origin_lon],
                number_of_sides=8,
                radius=15,
                color=hex_color,
                fill_color=hex_color,
                fill_opacity=0.5,  # Fully opaque
                weight=3,  # Thicker border
                fill=True
            ).add_to(map_obj)

        # Plot destination point
        if destination:
            randomized_destination_lat, randomized_destination_lon = randomize_location(destination["lat"],
                                                                                        destination["lon"], 10)
            folium.RegularPolygonMarker(
                location=[randomized_destination_lat, randomized_destination_lon],
                number_of_sides=4,
                radius=15,
                color=hex_color,
                fill_color=hex_color,
                fill_opacity=0.5,  # Fully opaque
                weight=3,  # Thicker border
                fill=True
            ).add_to(map_obj)
    # -------------


def plot_platoon_events(map_obj, platoon_events):
    """
    Plot platoon events on a map.

    Args:
        map_obj (folium.Map): The folium map object to plot on.
        platoon_events (dict): A dictionary containing platoon events data. The keys are platoon IDs and the values are
                               dictionaries containing event types and corresponding points.

    Returns:
        None
    """
    # Define icons for different event types
    # More under https://getbootstrap.com/docs/3.3/components/
    event_icons = {
        "CREATE": "screenshot",
        "VIA": "road",
        "ADD": "plus-sign",
        "REMOVE": "minus-sign",
        "DISSOLVE": "flag",
    }

    # Predefined set of folium supported icon colors
    folium_icon_colors = [
        'lightred', 'darkred', 'orange',
        'beige', 'lightgreen', 'green', 'darkgreen',
        'lightblue', 'cadetblue', 'darkblue',
        'purple', 'darkpurple',
        'pink', 'gray', 'lightgray', 'black', 'red'
    ]
    num_platoons = len(platoon_events)
    if num_platoons > len(folium_icon_colors):
        print("Warning: More platoons than available distinct icon colors. Colors will repeat.")
    color_idx = 0

    for platoon_id, events in platoon_events.items():
        icon_color = folium_icon_colors[color_idx % len(folium_icon_colors)]
        color_idx += 1

        for event_type, points in events.items():
            icon_name = event_icons.get(event_type, "question-sign")

            for point in points:
                lat_, lon_ = randomize_location(point["lat"], point["lon"], 3)
                folium.Marker(
                    location=[lat_, lon_],
                    icon=folium.Icon(color=icon_color, icon=icon_name),
                    popup=f"Platoon {platoon_id}: {event_type} event"
                ).add_to(map_obj)


def make_nodes_searchable(map_obj, nodes):
    """
    Adds searchable nodes to the given map object.
    Warning: make the output extremely sloww. Only use for locating a mysterious road point.

    Args:
        map_obj (folium.Map): The map object to add the searchable nodes to.
        nodes (list): A list of nodes.

    Returns:
        None
    """
    nodes_geojson = nodes_to_geojson(nodes)
    geojson_layer = folium.GeoJson(
        nodes_geojson,
        name="Nodes",
        style_function=lambda x: {'fillColor': '#ffffff', 'color': '#ffffff', 'fillOpacity': 0, 'weight': 0},
        show=False  # Set to False so it doesn't show the layer on map load
    )
    map_obj.add_child(geojson_layer)

    search_control = Search(
        layer=geojson_layer,
        geom_type='Point',
        placeholder="Search for OSM ID",
        collapsed=False,
        search_label='osm_id'
    )
    map_obj.add_child(search_control)


def nodes_to_geojson(nodes):
    """
    Converts a list of nodes to a GeoJSON FeatureCollection.

    Args:
        nodes (list): A list of nodes, where each node is a dictionary containing the following keys:
            - osm_id (int): The OSM ID of the node.
            - lat (float): The latitude of the node.
            - lon (float): The longitude of the node.

    Returns:
        Ugly GeoJson that is needed in make_nodes_searchable to index the map.
    """
    features = []
    for node in nodes:
        feature = {
            "type": "Feature",
            "properties": {
                "osm_id": node['osm_id'],
                "popup": f"OSM ID: {node['osm_id']}<br>Latitude: {node['lat']}<br>Longitude: {node['lon']}"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [node['lon'], node['lat']]
            }
        }
        features.append(feature)
    return {"type": "FeatureCollection", "features": features}


def calculate_average_lat_lon(platoon_events):
    """
    Calculate the average latitude and longitude from platoon events.
    I think I used it at some point to let the map center around the platoon events, but was an unnecessary level of complexity.

    Parameters:
    - platoon_events (dict): A dictionary where keys are event types and values are lists of points (each point is a dict with 'lat' and 'lon').

    Returns:
    - (float, float): A tuple containing the average latitude and longitude.
    """
    total_lat = 0
    total_lon = 0
    count = 0

    for event_type, points in platoon_events.items():
        for point in points:
            total_lat += point['lat']
            total_lon += point['lon']
            count += 1

    if count == 0:
        return None, None  # Avoid division by zero if there are no points

    average_lat = total_lat / count
    average_lon = total_lon / count

    return average_lat, average_lon


def create_map(segments, nodes, map_center, vehicle_route_points, file_name, platoon_events, searchable_nodes=False):
    """
    Create a map visualization with road segments, nodes, vehicle route points, platoon events, and searchable nodes.

    Args:
        segments (list): List of road segments to plot on the map.
        nodes (list): List of nodes to plot on the map.
        map_center (tuple): Tuple containing the latitude and longitude coordinates of the map center.
        vehicle_route_points (list): List of vehicle route points to plot on the map.
        file_name (str): Name of the file to save the map as.
        platoon_events (list): List of platoon events to plot on the map.
        searchable_nodes (bool, optional): Flag indicating whether to make nodes searchable on the map. Defaults to False. Enabling it creates a searchable map, no routes and platoons.

    Returns:
        None
    """
    logger.info(f"Creating map centered at {map_center}.")
    # Create the map

    # map_obj = folium.Map(location=map_location, zoom_start=13) # Use this instead of CartoDB for good old openstreetmaps style
    map_obj = folium.Map(location=[map_center[0], map_center[1]], tiles='CartoDB positron',
                         zoom_start=8)  # this looks better in screenshots

    # Plot road segments
    logger.info("Plotting road segments.")
    plot_road_segments(map_obj, segments)

    # Plot nodes
    logger.info("Plotting nodes.")
    plot_nodes(map_obj, nodes, shared_nodes={})

    # Plot vehicle routes, if available
    if vehicle_route_points is not None:
        logger.info("Plotting vehicle routes.")
        plot_vehicle_routes(map_obj, vehicle_route_points)
        # uncomment the next two lines and comment the third to view the shared nodes.
        # shared_nodes = identify_shared_nodes(vehicle_route_points)
        # plot_nodes(map_obj, nodes, shared_nodes)

    if platoon_events is not None:
        logger.info(f"Plotting {len(platoon_events)} platoon events.")
        plot_platoon_events(map_obj, platoon_events)
    else:
        logger.warning("No platoon events provided.")

    # Make nodes searchable if the flag is set
    if searchable_nodes:
        logger.info("Adding searchable nodes to the map.")
        make_nodes_searchable(map_obj, nodes)

    # Save the map to an HTML file
    map_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    map_obj.save(map_file_path)
    print(" Ready to view ".center(100, "="))
    logger.info(f"{green_text}Map has been created and saved as \n{map_file_path}{reset_text}"
                f"{orange_text}\nHINT: copy the local path above into your browser.{reset_text}")
    print("".center(100, "="))


def check_vehicle_set_exists(vehicle_set_id: int) -> bool:
    """
    Checks if a vehicle set with the given ID exists in the database.
    
    Args:
        vehicle_set_id (int): The ID of the vehicle set.
    
    Returns:
        bool: True if the vehicle set exists, False otherwise.
    """
    with exporter.driver.session() as session:
        result = session.run("MATCH (vs:VehicleSet) WHERE id(vs)=$vehicle_set_id RETURN vs",
                             vehicle_set_id=vehicle_set_id)
        vehicle_set = result.single()
        if vehicle_set:
            # logger.info(f"Vehicle Set with ID {vehicle_set_id} exists.")
            return True
        else:
            logger.error(f"{red_text}Vehicle Set with ID {vehicle_set_id} does not exist.{reset_text}")
            return False


def check_platoon_traces_exist(platoon_ids: set) -> bool:
    """
    Checks if all platoon traces with the given IDs exist in the database.
    
    Args:
        platoon_ids (set): A set of platoon IDs.
    
    Returns:
        bool: True if all platoon traces exist, False otherwise.
    """
    missing_traces = []
    with exporter.driver.session() as session:
        for platoon_id in platoon_ids:
            result = session.run("MATCH (p:Platoon) WHERE id(p)=$platoon_id RETURN p", platoon_id=platoon_id)
            platoon = result.single()
            if not platoon:
                missing_traces.append(platoon_id)

    if missing_traces:
        logger.error(f"{red_text}The following platoon traces do not exist: {missing_traces} {reset_text}")
        return False
    # logger.info(f"All platoon traces with IDs {platoon_ids} exist.")
    return True


if __name__ == "__main__":
    # Parse the command-line arguments
    args = parse_args()

    # Database connection details
    # TODO instead of the following, use the connection in databasecontainer.py from exp2
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "12345678"

    exporter = RoadMapExporter(uri, user, password)

    # Default vehicle set and platoon IDs
    # NOTE: You may update these two variables isntead of sending command line arguments
    default_vehicle_set = -1
    default_platoon_ids = {-2, -3, -4}

    # Use terminal parameters if provided, otherwise use defaults
    vehicle_set = args.vehicle_set_id if args.vehicle_set_id else default_vehicle_set
    platoon_ids = set(args.platoon_ids) if args.platoon_ids else default_platoon_ids

    invalid_vehicle_Set = False
    invalid_platoon_traces = False
    # Check if vehicle set and platoon traces exist before proceeding
    if not check_vehicle_set_exists(vehicle_set):
        invalid_vehicle_Set = True
        # logger.error(f"{red_text}Vehicle set with ID {vehicle_set} does not exist. Exiting.{reset_text}")

    if not check_platoon_traces_exist(platoon_ids):
        invalid_platoon_traces = True
        # logger.error(f"{red_text}One or more platoon traces do not exist. Exiting.{reset_text}")

    if invalid_vehicle_Set or invalid_platoon_traces:
        logger.error(
            f"{red_text}Could not generate the map due to missing or invalid vehicle route points or platoon events.{reset_text}")
        exit(1)

    # Fetch road segments and nodes
    logger.info("Fetching road segments and nodes.")
    road_segments, nodes = exporter.fetch_road_segments_and_nodes()

    # Fetch vehicle route points if the vehicle set is valid
    vehicle_route_points = None
    try:
        vehicle_route_points = exporter.fetch_vehicle_route_points(vehicle_set)
        logger.info(f"Fetched vehicle routes for Vehicle Set (ID={vehicle_set}).")
    except Exception as e:
        logger.error(f"Failed to fetch vehicle routes for Vehicle Set (ID={vehicle_set}): {e}")

    # Fetch platoon events if platoon IDs are provided
    platoon_events = None
    try:
        platoon_events = exporter.fetch_platoon_events_by_ids(platoon_ids)
        logger.info(f"Fetched platoon events for {len(platoon_ids)} platoons.")
    except Exception as e:
        logger.error(f"Failed to fetch platoon events for IDs {platoon_ids}: {e}")

    # Close the exporter connection
    exporter.close()

    logger.info("Generating map.")
    map_center_location = [48.6384555, 11.5582801]

    file_name = f'vehicle_set_{vehicle_set}_platoon_count_{len(platoon_ids)}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.html'

    create_map(segments=road_segments,
               nodes=nodes,
               map_center=map_center_location,
               vehicle_route_points=vehicle_route_points,
               file_name=file_name,
               platoon_events=platoon_events,
               searchable_nodes=False)

    logger.info("Data export process completed successfully.")
