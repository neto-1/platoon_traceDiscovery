import collections
import subprocess
from neo4jrestclient.client import GraphDatabase
#import pycurl
#from StringIO import StringIO
import time
import yaml

import psycopg2
import platform

# Load configurations
with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
src = (cfg["src"])
dbprefix = (cfg["dbprefix"])
dbplugins = (cfg["dbplugins"])
dbconfig = (cfg["dbconfig"])
experiments = (cfg["experiments"])
pgname = (cfg["pgname"])
pgpass = (cfg["pgpass"])
pgdbname = (cfg["pgdbname"])
pghost = (cfg["pghost"])


def initdb():
    dbuser = "neo4j"
    dbpass = "12345678"

    db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)

    return db

def relabelnodes():
    query = "MATCH (n:vehicle) REMOVE n:vehicle SET n:veh"
    db = initdb()
    db.query(query)


def relabelrelationships():
    query = "MATCH (s)-[r:ends]->(e) " \
            "DELETE r " \
            "CREATE (s)-[:ENDATLOCATION]->(e)"
    db = initdb()
    db.query(query)


def launchdb(dbprefix, dbname, dbuser, dbpass, dbplugins, dbconfig, containername):
    docker = "docker run -d --name "+containername+" --publish=7474:7474 --publish=7687:7687 --volume="+dbprefix+""+dbname+":/data/databases/graph.db --volume="+dbplugins+":/plugins --volume="+dbconfig+":/conf --env=NEO4J_AUTH="+dbuser+"/"+dbpass+" neo4j"
    subprocess.call(docker, shell=True)

    print(docker)

    run = True
    while run:
        try:
            gb = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)
            run = False
        except:
            time.sleep(5)
            print("Starting Neo4j: "+ dbname +" : %s" % time.ctime())
            run = True
    return gb


def stopdb(containername) :
    dockerstop = "docker stop " + containername
    subprocess.call(dockerstop, shell=True)

    dockerstop = "docker rm " + containername
    subprocess.call(dockerstop, shell=True)

#relabelnodes()

#relabelrelationships()

stopdb("neodb")


launchdb(dbprefix,
       "saarland_simple", "neo4j", "12345678",
       dbplugins,
        dbconfig,"neodb")

# launchdb(dbprefix,
#        "GridNetwork", "neo4j", "1234567890",
#        dbplugins,
#         dbconfig,"neodb")

# launchdb("/Users/dmitry/Documents/wd/data/databases.spatial/",
#        "saarland_simple", "neo4j", "12345678",
#        "/Users/dmitry/Documents/wd/data/databases.spatial/plugins",
#        "/Users/dmitry/Documents/wd/data/databases.spatial/conf","neodb")

# launchdb("/Users/dmitry/Documents/wd/data/databases.taxi/",
#        "new_york_city_cleaning", "neo4j", "12345678",
#        "/Users/dmitry/Documents/wd/data/databases.spatial/plugins",
#        "/Users/dmitry/Documents/wd/data/databases.spatial/conf","neodb")

# launchdb("/Users/dmitry/Documents/wd/data/",
#         "grid_simple", "neo4j", "1234567890",
#         "/Users/dmitry/Documents/wd/data/databases.spatial/plugins",
#         "/Users/dmitry/Documents/wd/data/databases.spatial/conf","neodb")

# launchdb("/Users/dmitry/Documents/wd/data/databases.spatial/",
#         "germany_simple.graphdb", "neo4j", "12345678",
#         "/Users/dmitry/Documents/wd/data/databases.spatial/plugins",
#         "/Users/dmitry/Documents/wd/data/databases.spatial/conf","neodb")

# launchdb("C:\Users\cg-admin\Documents\Platooning\Data\databases.spatial\\",
#         "saarland_simple", "neo4j", "12345678",
#         "C:\Users\cg-admin\Documents\Platooning\Data\databases.spatial\plugins",
#         "C:\Users\cg-admin\Documents\Platooning\Data\databases.spatial\conf","neodb")
