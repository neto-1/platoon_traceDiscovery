import ShortestPathDBOperation
# queries to create the nodes in the database

def RunQueries(db,startNodesId,endNodesId,distances,paths_nodes,numOfVehicles,distribution):
    # query to create the node with label VehicleSet
    # 1- Get the maximum Id of the nodes with VehicleSet label
    # 2- Create the Node
    query = "MATCH (n:VehicleSet) RETURN MAX(n.id)"
    result = db.query(query)
    setId = 0
    if result[0][0] is None:
        setId = 1
    else:
        setId = result[0][0] + 1
    query = "CREATE (n:VehicleSet{id: "+str(setId)+", size: "+str(numOfVehicles)+", distribution: '"+distribution+"'}) RETURN Id(n)"
    result = db.query(query)
    vehicleSetNode=result[0][0]

    # foreach generated vehicle:
    # 1- create node with label Vehicle
    # 2- create a relation to start node with label START, a relation to end node with label END
    # 3- create a relation from VehicleSet Node and Vehicle node with label INSET
    while len(startNodesId) != 0:
        startNodeId=startNodesId.pop(0)
        endNodeId= endNodesId.pop(0)
        distance=distances.pop(0)
        path_nodes=paths_nodes.pop(0)
        query = "MATCH (startnode:loc), (endnode:loc), (setnode:VehicleSet) " \
                "WHERE Id(startnode)="+ str(startNodeId)+" and Id(endnode)="+str(endNodeId)+" and Id(setnode)="+str(vehicleSetNode)+" " \
                "CREATE (vehnode:Vehicle{earliest_departure:0, latest_arrival:0, shortestpath_cost:"+ str(distance)+"}) " \
                "CREATE (vehnode)-[r1:START]->(startnode) " \
                "CREATE (vehnode)-[r2:END]->(endnode) " \
                "CREATE (setnode)-[r3:INSET]->(vehnode) " \
                "RETURN id(vehnode)"
        res=db.query(query)
        vehicle_id=res[0][0]
        ShortestPathDBOperation.ComputeSPofVehicle(db,vehicle_id,path_nodes)
    # print "Nodes and Relations are created correctly"


def GetNormalDistributionsParameters(longestPath,scaleValue):
    scaledLongestPath=longestPath*scaleValue
    mu=scaledLongestPath/2
    sigma=scaledLongestPath/6
    return mu,sigma
