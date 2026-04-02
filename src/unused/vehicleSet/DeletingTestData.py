from neo4jrestclient.client import GraphDatabase

def deleteAllTestData():
    query="match (n1:VehicleSet)-[r1:INSET]->(n2:Vehicle)-[r2:START|END]->(n3:loc) delete r2,r1,n2,n1"
    db.query(query)
    print "Test Data is deleted"


def DeleteTestDataById(id):
    # match (n1:VehicleSet{id:2})-[r1:INSET]->(n2:Vehicle)-[r2:START|END]->(n3:loc) return n1,r1,n2,r2,n3
    query="match (n1:VehicleSet{id:"+str(id)+"})-[r1:INSET]->(n2:Vehicle)-[r2:START|END]->(n3:loc) delete r2,r1,n2,n1"
    db.query(query)
    print "Test Data is deleted"


def DeleteTestDataByDistribution(dist): # normal / lognormal / random / gamma / region
    query="match (n1:VehicleSet{distribution:'"+dist+"'})-[r1:INSET]->(n2:Vehicle)-[r2:START|END]->(n3:loc) delete r2,r1,n2,n1"
    db.query(query)
    print "Test Data is deleted"

dbuser = "neo4j"
dbpass = "12345678"
db = GraphDatabase("http://localhost:7474", username=dbuser, password=dbpass)
#DeleteTestDataByDistribution("normal") # normal / lognormal / random / gamma / region
#DeleteTestDataById(1)
deleteAllTestData()
