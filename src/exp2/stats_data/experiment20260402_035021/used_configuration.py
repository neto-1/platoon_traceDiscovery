from pathlib import Path

class Configuration:
    Project_root = Path(__file__).resolve().parents[3]
    db_path = Project_root/"data"/"database.spatial"
    # db_path = "C:/Users/ThinkPad-T470/Documents/Platoon/database.spatial/"
    db_plugins_path = db_path / "plugins"
    # db_plugins_path = "D:/DatenRepository/database.spatial/plugins/"
    db_config_path = db_path / "conf"
    # db_config_path = "D:/DatenRepository/database.spatial/conf/"
    db_user = "neo4j"
    db_password = "12345678"
    db_http_port = 7474
    db_bolt_port = 7687
    db_heap_initial_size = "2G"
    db_heap_max_size = "2G"
    db_version = "3.5.2-enterprise"

    # db_road_networks = [("grid_10x10", 50 * 1000, 1500 * 1000)]
    # db_road_networks = [("grid_20x20", 50*1000, 1500*1000)]
    # db_road_networks = [("grid_30x30", 500*1000, 1500*1000)]
    # db_road_networks = [("berlin", 5*1000, 1500*1000)]
    # db_road_networks = [("bayern", 50*1000, 1500*1000)]
    # db_road_networks = [("sweden", 50*1000, 300*1000)]
    # db_road_networks = [("germany", 50*1000, 300*1000)]
    # db_road_networks = [("germany", 10 * 1000, 20 * 1000)]  # for creating instances with min overlap
    db_road_networks = [("colorado", 50 * 1000, 1500 * 1000)]
    # db_road_networks = [("newyork", 50*1000, 1500*1000)]

    """ Chunk sizes for write batches """
    incentive_chunk_size = 500
    incentive_with_polygon_chunk_size = 100

    # C:/Users/ThinkPad-T470/Desktop/src/src

    exp_path = Project_root / "src" / "exp2" / "config"
    exp_file = "experiment1.json"
    working_directory = Project_root / "src" / "exp2"
    exp_full_path = exp_path / exp_file

    """ Gurobi configurations """
    grb_output_flag = False  # Gurobi solver produces output while solving
    grb_node_file_start = 0.1  # Write MIP nodes to disk (measured in GBytes)
    grb_threads = 1  # Number of threads, The default value of 0 is an automatic setting. It will generally use all of the cores in the machine, but it may choose to use fewer.
    grb_node_file_start_mg = grb_node_file_start
    grb_node_file_start_sg = 0.1

    grb_threads_mg = grb_threads
    grb_threads_sg = 1
    grb_log_iterations = False
    grb_log_seconds = 5

    log_cg = True

    shuffle_test_cases = False

    pg_name = "admin"
    pg_pass = "dbklm983$"
    pg_db_name = "platoon"
    pg_host = "139.174.101.107"
    logging = True

    # incentive_package_path = "/Users/gerrit/Documents/platooning/src/group/convex/"
    # algorithm__incentives__path = "/Users/gerrit/Documents/platooning/src/group/Incentives"
    # algorithm__grouping__path = "/Users/gerrit/Documents/phd/src/gp"

    def __init__(self):
        raise NotImplementedError("static")

