class Configuration:

    db_path = "/Users/dmitry/Documents/wd/data/database.experiments/"
    db_plugins_path = "/Users/dmitry/Documents/wd/data/database.experiments/plugins"
    db_config_path = "/Users/dmitry/Documents/wd/data/database.experiments/conf"
    db_user = "neo4j"
    db_password = "12345678"
    db_http_port = 7474
    db_bolt_port = 7687
    db_version = "3.3.0"

    exp_path = "/Users/dmitry/Documents/wd/platooning/src/exp2/config/"
    exp_file = "experiment.json"
    exp_full_path = exp_path + exp_file

    pg_name = "admin"
    pg_pass = "dbklm983$"
    pg_db_name = "platoon"
    pg_host = "139.174.101.107"
    logging = True

    incentive_package_path = "/Users/dmitry/Documents/wd/platooning/src/group/convex/"
    algorithm__incentives__path = "/Users/dmitry/Documents/wd/platooning/src/group/Incentives"
    algorithm__grouping__path = "/Users/dmitry/Documents/wd/phd/src/gp"

    def __init__(self):
        raise NotImplementedError("static")

