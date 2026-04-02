def GetFirstNodeOfSP(db,vehicleNodeId):
    query = "MATCH (vehiclenode:Vehicle)-[r1:SP]->(firstnode:RouteNode) where ID(vehiclenode)="+str(vehicleNodeId)+" return ID(firstnode)"
    res=db.query(query)
    if len(res)==0:
        return -1
    else:
        return res[0][0]

def CheckExistSP(db,vehicleNodeId):
    query = "MATCH (vehiclenode:Vehicle)-[r1:SP]->(firstnode:RouteNode) where ID(vehiclenode)="+str(vehicleNodeId)+" return ID(firstnode)"
    res=db.query(query)
    if len(res)==0:
        return False
    else:
        return True

def ComputeSPofVehicleSet(db,vehicleSetId):
    query = "MATCH (vehiclesetnode:VehicleSet)-[r1:INSET]->(vehiclenode:Vehicle) where vehiclesetnode.id="+str(vehicleSetId)+" return ID(vehiclenode)"
    res=db.query(query)
    for val in res:
        ComputeSPofVehicle(db,val[0])

def ComputeSPofVehicle(db,vehicleNodeId,path_nodes):
    if CheckExistSP(db,vehicleNodeId) ==False:# SP is not exist so we can compute it safely
        routeNodeList=[]
        count=-1
        for val in path_nodes:
            if count==-1:
                query="MATCH (pathnode:loc),(vehiclenode:Vehicle) where ID(pathnode)="+str(val)+" and ID(vehiclenode)="+str(vehicleNodeId)+" " \
                      "CREATE (routenode:RouteNode{time:0, group: 0}) " \
                      "CREATE (routenode)-[pnode:PNODE]->(pathnode) " \
                      "CREATE (vehiclenode)-[sp:SP]->(routenode) " \
                       "RETURN ID(routenode)"
            else:
                routeNodeId=routeNodeList.__getitem__(count)
                query="MATCH (pathnode:loc),(preroutenode:RouteNode),(preroutenode:RouteNode)-[prepnode:PNODE]->(prepathnode:loc),(prepathnode)-[r:NEIGHBOUR]-(pathnode) " \
                      "where ID(pathnode)="+str(val)+" and ID(preroutenode)="+str(routeNodeId)+" " \
                      "CREATE (routenode:RouteNode{time:0, group: 0}) " \
                      "CREATE (routenode)-[pnode:PNODE]->(pathnode) " \
                      "CREATE (preroutenode)-[next:NEXT{cost:r.distance}]->(routenode) " \
                       "RETURN ID(routenode)"
            res = db.query(query)
            routeNodeList.append(res[0][0])
            count=count+1
        # print "Shortest path is computed. All nodes and relations based on Data Model are created successfully"
    else:
        print "The shortest path is already computed. We can not compute it again"


def DeleteAllSP(db):
    query="match (n1:RouteNode)-[s:NEXT]->(n2:RouteNode) delete s"
    db.query(query)
    query="match ()-[s:SP]->(n2:RouteNode) delete s"
    db.query(query)
    query="match (n1:RouteNode)-[r1:PNODE]->() delete r1,n1"
    db.query(query)
    print "All Shortest paths are deleted successfully"
