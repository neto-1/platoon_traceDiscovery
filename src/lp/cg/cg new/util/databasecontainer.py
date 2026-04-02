import subprocess
from util.configuration import Configuration
from neo4j.v1 import GraphDatabase
import time


class DatabaseContainer:
    """
    provides methods to launch and stop docker container with neo4j database management system
    """
    def __init__(self):
        raise NotImplementedError("static")

    db_container_name = None
    driver = None

    @staticmethod
    def launch(db_name: str,  db_user: str = Configuration.db_user, db_password: str = Configuration.db_password,
               db_http_port: int = Configuration.db_http_port, db_bolt_port: int = Configuration.db_bolt_port,
               db_version: str = Configuration.db_version, db_path: str = Configuration.db_path,
               db_plugins_path: str = Configuration.db_plugins_path,
               db_config_path: str = Configuration.db_config_path, db_output_flag: bool = True) -> None:
        """
        launches neo4j docker container;
        :param db_name: database name
        :param db_user: database user
        :param db_password: database password
        :param db_http_port: database http port; default: 7474
        :param db_bolt_port: database bolt port; default: 7687
        :param db_version: version of database management system; the plug-in version and database instance version
        must be considered
        :param db_path: database path links the folder containing the database instance
        :param db_plugins_path: path to the folder with the plug-ins; some plug-ins have to be registered in config file
        :param db_config_path: path to the folder with the config file
        :param db_output_flag: if activated, docker log and exception message will shown
        :return:
        """

        if DatabaseContainer.db_container_name is not None:
            raise ValueError

        DatabaseContainer.db_container_name = "neo_" + db_name

        run_docker_command = "docker run -d --name " + DatabaseContainer.db_container_name + \
                             " --publish=" + str(db_http_port) + ":7474 " \
                             "--publish=" + str(db_bolt_port) + ":7687 " \
                             "--volume=" + db_path + db_name + ":/data/databases/graph.db " \
                             "--volume=" + db_plugins_path + ":/plugins " \
                             "--volume=" + db_config_path + ":/conf " \
                             "--env=NEO4J_AUTH=" + db_user + "/" + db_password + " neo4j:" + db_version
        if db_output_flag:
            print(run_docker_command)
        subprocess.Popen(run_docker_command, shell=True)

        is_not_running = True
        print("Starting Neo4j ")
        starting_time = time.time()
        while is_not_running:
            try:
                DatabaseContainer.driver = GraphDatabase.driver("bolt://localhost:" + str(db_bolt_port),
                                                                auth=(db_user, db_password))
                is_not_running = False
            except Exception as exp:
                time.sleep(5)
                print(",.", end='\r')
                print(".")
                if db_output_flag:
                    print(exp)
                    subprocess.Popen("docker logs " + DatabaseContainer.db_container_name, shell=True)

        print("Neo4j started in", time.time() - starting_time, "seconds.")

    @staticmethod
    def stop() -> None:
        """
        stops and removes current running neo4j docker container
        :return:
        """

        # force remove docker container
        docker_stop = "docker rm --force " + DatabaseContainer.db_container_name
        subprocess.Popen(docker_stop, shell=True)

        DatabaseContainer.db_container_name = None
        DatabaseContainer.driver = None
