import networkx as nx
from gurobipy import *
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import time
import psycopg2
import platform
import json
import yaml
import copy
from typing import Tuple, Dict, List
import subprocess
from lib.Basics import Basics
from typing import Tuple, Dict, List


# class contains all common information like config data or general functions
class Database:

    # init the basics
    def __init__(self):
        raise NotImplementedError("Static Class")

    @staticmethod
    def test_db(waiting_time: float = 0) -> bool:
        #load config for username and password
        src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host = Basics.load_config()
        try:
            GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)
            message = True
        except:
            time.sleep(waiting_time)
            print("Starting Neo4j waiting " + str(waiting_time) + " sec: " + " : %s" % time.ctime())
            message = False
        return message

    @staticmethod
    # initiate database
    def launch_db(name: str = "saarland_simple", waiting_time: float = 5.0) -> GraphDatabase:
        # load required config data
        src, db_prefix, db_plugins, db_config, db_user, db_pass, experiments, pg_name, pg_pass, pg_db_name, pg_host = Basics.load_config()

        # run new docker container
        docker = "docker run -d --name neodb --publish=7474:7474 --publish=7687:7687 --volume=" + db_prefix \
                 + "" + name + ":/data/databases/graph.db --volume=" + db_plugins + ":/plugins --volume=" + \
                 db_config + ":/conf --env=NEO4J_AUTH=" + db_user + "/" + db_pass + " neo4j:3.3.0"
        subprocess.call(docker, shell=True)

        # print helpful output for error finding and bug fixing
        print(docker)

        # wait until database is loaded
        run = False
        while not run:
            # try to run the database
            run = Database.test_db(waiting_time)

        # after initializing the database give the object db back
        try:
            graph_db = GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)
        except:
            graph_db = "no_database"
        return graph_db

    # stops the database and removes the container
    @staticmethod
    def stop_remove_db() -> None:
        # stop docker container
        docker_stop = "docker stop neodb"
        subprocess.call(docker_stop, shell=True)

        # delete docker container
        docker_stop = "docker rm neodb"
        subprocess.call(docker_stop, shell=True)

    # relaunch the database to another network
    @staticmethod
    def relaunch_db(name: str = "saarland_simple", waiting_time: float = 5) -> GraphDatabase:

        # stop and remove the container
        Database.stop_remove_db()

        # launch the database
        graph = Database.launch_db(name, waiting_time)

        # return the database
        return graph

    @staticmethod
    def test_and_connect(database_name: str = "saarland_simple", waiting_time: float = 0):
        # check if the database is already running
        try:
            Database.test_db(waiting_time)
        # if it is not running: launch the database
        except:
            Database.relaunch_db(database_name, 5)

    # delete all incentives (PlatooningUtility)
    @staticmethod
    def delete_incentives(db_user: str ="admin", db_pass: str ="12345678") -> None:
        graph_db = GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)
        query = "MATCH (u:PlatooningUtility) detach delete u"
        graph_db.query(query)

    # delete all Groups
    @staticmethod
    def delete_incentives(db_user: str ="admin", db_pass: str ="12345678") -> None:
        graph_db = GraphDatabase("http://localhost:7474", username=db_user, password=db_pass)
        query = "MATCH (g:Group) detach delete g"
        graph_db.query(query)