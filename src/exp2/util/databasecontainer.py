import logging
import subprocess
import sys
import time
from neo4j import GraphDatabase
from util.configuration import Configuration
from stat_functions import stats_path
from stat_functions.experiment_folder import create_experiment_folder, create_testcase_folder   


# Setting up logging with formatting
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ANSI escape codes for colored output in terminal
green_text = "\033[92m"
orange_text = "\033[93m"
red_text = "\033[91m"
reset_text = "\033[0m"


class DatabaseContainer:
    """
    provides methods to launch and stop docker container with neo4j database management system
    """

    def __init__(self):
        raise NotImplementedError("static")

    db_container_name = None
    driver = None

    @staticmethod
    def check_docker_daemon() -> None:
        docker_daemon_check_cmd = "docker info > /dev/null 2>&1"
        docker_daemon_running = subprocess.call(docker_daemon_check_cmd, shell=True) == 0
        if not docker_daemon_running:
            logger.error(
                f"{red_text}Docker daemon is not running. Please ensure Docker is installed and running.{reset_text}")
            raise RuntimeError("Cannot connect to the Docker daemon. Is the docker daemon running?")
        # logger.info(f"{green_text}Docker daemon is running and ready.{reset_text}")

    @staticmethod
    def container_exists(container_name: str) -> str:
        container_exists_cmd = f"docker ps -aq -f name=^{container_name}$"
        container_id = subprocess.getoutput(container_exists_cmd)
        return container_id

    @staticmethod
    def start_or_restart_container(container_id: str, container_name: str) -> None:
        if container_id:
            # Check if it's running
            container_running_cmd = f"docker inspect -f '{{{{.State.Running}}}}' {container_id}"
            is_running = subprocess.getoutput(container_running_cmd) == 'true'
            if not is_running:
                logger.info(
                    f"{orange_text}The container \"{container_name}\" exists but is not running. Now starting it...{reset_text}")
                try:
                    subprocess.run(f"docker start {container_name}", shell=True, check=True)
                    logger.info(
                        f"{green_text}Container \"{container_name}\" successfully started. Now initializing the Neo4j database inside the container. This might take some time...{reset_text}")
                except subprocess.CalledProcessError as e:
                    logger.error(
                        f"{red_text}Failed to start the container \"{container_name}\". It may be due to port conflicts (e.g., port {Configuration.db_http_port} or {Configuration.db_bolt_port} is already in use).{reset_text}")
                    logger.error(f"{red_text}Docker error: {e}{reset_text}")
                    logger.info(
                        f"{orange_text}Please manually stop the conflicting container or assign different ports.{reset_text}")
                    raise RuntimeError(
                        f"Failed to start container \"{container_name}\" due to port conflict or other issues.")
            else:
                logger.info(f"{green_text}Container \"{container_name}\" is already running.{reset_text}")
        else:
            logger.error(f"{red_text}Container {container_name} does not exist.{reset_text}")
            raise RuntimeError(f"Container {container_name} does not exist.")

    @staticmethod
    def start_or_restart_container_dep(container_id: str, container_name: str) -> None:
        if container_id:
            # Check if it's running
            container_running_cmd = f"docker inspect -f '{{{{.State.Running}}}}' {container_id}"
            is_running = subprocess.getoutput(container_running_cmd) == 'true'
            if not is_running:
                logger.info(
                    f"{orange_text}The container \"{container_name}\" already exists but is not running. Now starting it...{reset_text}")
                subprocess.run(f"docker start {container_name}", shell=True, check=True)
                logger.info(
                    f"{green_text}Container \"{container_name}\" successfully started. Now initializing the Neo4j database inside the container. This might take some time...{reset_text}")
            else:
                logger.info(f"{green_text}Container \"{container_name}\" is already running.{reset_text}")
        else:
            logger.error(f"{red_text}Container {container_name} does not exist.{reset_text}")
            raise RuntimeError(f"Container {container_name} does not exist.")

    @staticmethod
    def launch_new_container(container_name: str, db_name: str, db_http_port: int, db_bolt_port: int,
                             db_user: str, db_password: str, db_version: str, db_path: str, db_plugins_path: str,
                             db_config_path: str, db_heap_initial_size: str, db_heap_max_size: str,
                             db_output_flag: bool) -> None:
        run_cmd = f"docker run -d --name {container_name} " \
                  f"--publish={db_http_port}:7474 " \
                  f"--publish={db_bolt_port}:7687 " \
                  f"--volume={db_path}{db_name}:/data/databases/graph.db " \
                  f"--volume={db_plugins_path}:/plugins " \
                  f"--volume={db_config_path}:/conf " \
                  f"--env=NEO4J_ACCEPT_LICENSE_AGREEMENT=yes " \
                  f"--env=NEO4J_dbms_memory_heap_initial__size={db_heap_initial_size} " \
                  f"--env=NEO4J_dbms_memory_heap_max__size={db_heap_max_size} " \
                  f"--env=NEO4J_AUTH={db_user}/{db_password} " \
                  f"--platform linux/x86_64 neo4j:{db_version}"

        if db_output_flag:
            logger.info(f"{orange_text}Launching a new Neo4j container named \"{container_name}{reset_text}\"")


        subprocess.run(run_cmd, shell=True, check=True)
        logger.info(
            f"{green_text}Container \"{container_name}\" was created and successfully started. Now initializing the Neo4j database inside the container. This might take some time...{reset_text}")

    @classmethod
    def wait_for_neo4j(cls, db_bolt_port: int, db_user: str, db_password: str, max_retries: int = 15,
                       db_output_flag: bool = True) -> None:
        """
        Wait for the Neo4j database to be fully ready by checking the Bolt port availability.
        """
        is_not_running = True
        start_time = time.time()
        retry_count = 0

        # Initial log for container
        # logger.info(f"The Docker container '{cls.db_container_name}' has started. Now initializing the Neo4j database inside the container. This might take some time...")

        while is_not_running and retry_count < max_retries:
            try:
                # Show progress message for database initialization
                if db_output_flag:
                    sys.stdout.write(
                        f"\r{orange_text}Neo4j database is starting up (attempt {retry_count + 1})...{reset_text}")
                    sys.stdout.flush()

                # Create driver object
                cls.driver = GraphDatabase.driver(f"bolt://localhost:{db_bolt_port}", auth=(db_user, db_password))

                # Try opening a session and running a test query to verify connection
                with cls.driver.session() as session:
                    session.run("RETURN 1")  # Lightweight test query to verify the connection

                # If the query runs successfully, Neo4j is ready
                is_not_running = False

            except Exception:
                retry_count += 1
                if retry_count < max_retries:
                    sleep_duration = min(2 ** retry_count, 30)  # Exponential backoff, max sleep 30 seconds
                    sys.stdout.write(
                        f"\r{orange_text}Neo4j database is still initializing (retry {retry_count}). Next check in {sleep_duration} seconds...{reset_text}\r")
                    sys.stdout.flush()
                    time.sleep(sleep_duration)
                else:
                    # Exhausted retries
                    sys.stdout.write(
                        f"\r{red_text}Neo4j database failed to initialize after {retry_count} attempts.{reset_text}\n")
                    sys.stdout.flush()
                    logger.error(f"Neo4j database failed to start after {retry_count} attempts.")
                    raise RuntimeError("Neo4j database failed to start after several attempts.")

        # Clear the line and log success
        sys.stdout.write("\r")  # Clear the line
        logger.info(
            f"{green_text}Neo4j database inside the container is now fully operational and ready to accept connections. Startup completed in {time.time() - start_time:.2f} seconds.{reset_text}")

        # Include a clickable URL for the user to access the Neo4j interface
        logger.info(f"{green_text}Access the Neo4j browser interface at: {reset_text}http://localhost:7474/browser/")

    @classmethod
    def launch(cls, db_name: str, db_user: str = Configuration.db_user, db_password: str = Configuration.db_password,
               db_http_port: int = Configuration.db_http_port, db_bolt_port: int = Configuration.db_bolt_port,
               db_version: str = Configuration.db_version, db_path: str = Configuration.db_path,
               db_plugins_path: str = Configuration.db_plugins_path,
               db_config_path: str = Configuration.db_config_path,
               db_heap_initial_size: str = Configuration.db_heap_initial_size,
               db_heap_max_size: str = Configuration.db_heap_max_size,
               db_output_flag: bool = True) -> None:
        """
        Launches or restarts a Neo4j Docker container.
        """
        # cls.check_docker_daemon()

        cls.db_container_name = f"neo_{db_name}"
        container_id = cls.container_exists(cls.db_container_name)

        if container_id:
            cls.start_or_restart_container(container_id, cls.db_container_name)
            # Update the stats_path.stats_folder to reflect the current experiment
            existing_experiment_folder = stats_path.experiment_folder
            # print(f"existing_experiment_folder ✔✔✔🐱🎁: {existing_experiment_folder}")
            testcase_folder = create_testcase_folder(existing_experiment_folder)
            stats_path.stats_folder = testcase_folder  # Set the global path

        else:
            # TODO improve logging wording. 
            logger.info(f"{orange_text}The container \"{cls.db_container_name}\" does not exist.{reset_text}")

            cls.launch_new_container(cls.db_container_name, db_name, db_http_port, db_bolt_port,
                                     db_user, db_password, db_version, db_path, db_plugins_path, db_config_path,
                                     db_heap_initial_size, db_heap_max_size, db_output_flag)

            # Update the stats_path.stats_folder to reflect the current experiment
            experiment_folder = create_experiment_folder()
            time.sleep(2)  # Wait for 2 seconds to ensure the experiment folder is created
            testcase_folder = create_testcase_folder(experiment_folder)
            stats_path.stats_folder = testcase_folder  # Set the global path
            stats_path.experiment_folder = experiment_folder  # Set the experiment path

        cls.wait_for_neo4j(db_bolt_port, db_user, db_password, db_output_flag=db_output_flag)
        # logger.info(f"{green_text}Neo4j container launch process completed for: {cls.db_container_name}.{reset_text}")

    @staticmethod
    def stop() -> None:
        docker_stop = "docker stop " + DatabaseContainer.db_container_name

    @staticmethod
    def remove() -> None:
        """
        stops and removes current running neo4j docker container
        :return:
        """

        # force remove docker container
        docker_stop = "docker rm --force " + DatabaseContainer.db_container_name
        subprocess.Popen(docker_stop, shell=True)

        DatabaseContainer.db_container_name = None
        DatabaseContainer.driver = None
