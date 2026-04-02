library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)
library(httr)
library(jsonlite)
library(RPostgreSQL) 
library(igraph)

######################################## initially load the functions ########################################
functions = c("astr", "vehConvexHull","formingNotDisjointGroups")
if(!exists("ownPath")) {
  ownPath = script.dir <- dirname(dirname(sys.frame(1)$ofile))
}
##load the functions in the vector "functions"
for (func in 1:length(functions)) {
  functionname = functions[func]
  
  ## convert the actual path and add the needed source path ######
  completeSource = paste0(ownPath,"/functions/",functionname, ".R")
  source(completeSource)
  print(completeSource)
}
completeSource=paste0(ownPath,"/sd/EdgeValuation_grid.R")
print(completeSource)
source(completeSource)

##### start time 
tic()
dbStartTime = as.numeric(Sys.time())
############Initialisierung############

user = "neo4j";
pass = "1234567890";
auth = authenticate(user, pass, type = "basic");
url = "http://localhost:7474/db/data/";

graph = startGraph(url, username=user, password=pass)

###################=== Define Graph Edges ===###################
#query="MATCH (n)-[r:NEIGHBOUR]->(m)  RETURN id(n) as from, id(m) as to, r.distance as weight, n.lat as fromlat,n.lon as fromlon, m.lat as tolat,m.lon as tolon"
query="MATCH (n)-[r:NEIGHBOUR]->(m)  RETURN id(n) as from, id(m) as to, r.distance as weight, n.lat as fromlat,n.lon as fromlon, m.lat as tolat,m.lon as tolon"
edges=cypher(graph,query)
edges$label=edges$weight

#data <- cypher(graph, "MATCH (v1s:loc)<-[:STARTATLOCATION]-(n:veh)-[:ENDATLOCATION]->(v1e:loc) WHERE id(n)>3500 RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat, id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn LIMIT 30") 
#data <- cypher(graph, "MATCH (v1s:location)<-[:startAtLocation]-(n:vehicle)-[:endAtLocation]->(v1e:location) RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat, id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn")

###################=== Define Graph Nodes ===###################
#query="Match (n:loc) WHERE NOT(n.type = '') Return id(n) as id,n.lat as lat, n.lon as lon"
query="Match (n:loc) Return id(n) as id,n.lat as lat, n.lon as lon"
qnodes = cypher(graph,query)
nodes <- data.frame(id=unique(c(edges$from, edges$to)))
nodes$label <- nodes$id

## all nodes
#nodelist <- cypher(graph, "MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id, n.type AS ntype ")
nodelist <- cypher(graph, "MATCH (n:loc) RETURN n.lat AS lat, n.lon AS lon, id(n) AS id")

# create iGraph-graph from the edges
ig = graph_from_data_frame(edges, directed=F,vertices=nodes)

# set the attributes lat and lon for nodes
for ( i in 1:length(nodes[[1]]) ) {
  ig <- set.vertex.attribute(ig, "label", index=i, value=qnodes[i,1])
  ig <- set.vertex.attribute(ig, "lat", index=i, value=qnodes[i,2])
  ig <- set.vertex.attribute(ig, "lon", index=i, value=qnodes[i,3])
}
par(pch=22, col="black",lwd=1)
plot(get.vertex.attribute(ig, "lon"),get.vertex.attribute(ig, "lat"))
for ( d in 1:nrow(edges) ) {
  lines(c(as.numeric(edges$fromlon[d]), as.numeric(edges$tolon[d])),  c(as.numeric(edges$fromlat[d]), as.numeric(edges$tolat[d])))
}

############Parameter############
# output
output = FALSE

#Weight of the Overlays of the intersections in the comparison
DividebyFactor = 2

#linear weight
lw = 1.5

#check if two vehicles can drive together
canDriveTogether<-1

LimitValue = 30
sigma=10
VehID <- 0

fn <- function(x) {
  sum ( sqrt( (p12[1] - x[1])^2 + (p12[2] - x[2])^2 ) + sqrt( (p13[1] - x[1])^2 + (p13[2] - x[2])^2 ) + sqrt( (p22[1] - x[3])^2 + (p22[2] - x[4])^2 ) + sqrt( (p23[1] - x[3])^2 + (p23[2] - x[4])^2 ) + sqrt( (x[1] -x[3])^2 + (x[2] - x[4])^2 ) * lw)
}


dbTime =  as.numeric(Sys.time()) - dbStartTime;
##########=== MAIN LOOP ===##########

mainTime = as.numeric(Sys.time())

for ( i in 1:length(data$v1slon) ) {	

	#Fahrzeug 1 Start-und Endpunkt
	p12 <- c(data$v1slon[i], data$v1slat[i]);
	p22 <- c(data$v1elon[i], data$v1elat[i]);
	
	if(is.na(p12[1]) || is.na(p22[1]) ) { 
	  break
	}
	for ( j in i+1:length(data$v1slon) ) {
	  
	  #Fahrzeug 2 Start-und Endpunkt
	  p13 <- c(data$v1slon[j], data$v1slat[j]);
	  p23 <- c(data$v1elon[j], data$v1elat[j]);
	  
	  pa = p22 - p12;
	  pb = p23 - p13;
	  
	  if(is.na(pa) || is.na(pb)) {	
	    break
	  }
	  
	  ###################### STEP 1 - 90 Degree Check ######################
	  
	  ###### degree between linear line of vehicle are more then 90
	  if((pa[1] * pb[1] + pa[2] * pb[2]) < 0) {
	    
	    next
	  }
	  
	  ###### NODES ID
	  ### 1st VEHICLE
	  sid = data$v1sid[i]
	  eid = data$v1eid[i]
	  vehID = data$IDn[i]
	  
	  ### 2nd VEHICLE
	  eid2 = data$v1eid[j]
	  sid2 = data$v1sid[j]
	  vehID2 = data$IDn[j]
	  

	  pol1 = vehConvexHull(sid, eid, p12, pa,vehID,10)
	  pol2 = vehConvexHull(sid2, eid2, p13, pb, vehID2,10)

	  # create union of vehicle 1 and 2
	  if(!is.null(pol1)&&!is.null(pol2))
	  {
		res = gIntersection(pol1, pol2)
	  }
	  else
	  {
	    res=NULL;
	  }
	  canDriveTogether<-EdgeValuation(ig,sid,eid,sid2,eid2,nodelist,res,sigma);
	  #############################
	  ### intersection compare
	  if(!is.null(pol1) && !is.null(pol2)) {
	    res = gIntersection(pol1, pol2)
	    if(!is.null(res)) {
	      
	      qualityValue=canDriveTogether
	    }
	  }
	}
}
mTime=as.numeric(Sys.time())-mainTime

groupTime=as.numeric(Sys.time())

gTime=as.numeric(Sys.time())-groupTime
