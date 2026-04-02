library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)
library(httr)
library(jsonlite)
library(RPostgreSQL) 
library(igraph)

######################################## initially load the functions ########################################
functions = c("astr", "vehConvexHull","formingNotDisjointGroups","getMax","storeGroups")
ownPath = script.dir <- dirname(dirname(sys.frame(1)$ofile))

##load the functions in the vector "functions"
for (func in 1:length(functions)) {
  functionname = functions[func]
  
  ## convert the actual path and add the needed source path ######
  completeSource = paste0(ownPath,"/functions/",functionname, ".R")
  source(completeSource)
}
completeSource=paste0(ownPath,"/sd/EdgeValuation.R")
source(completeSource)

sourcename<-paste0(ownPath,"/sd/config.txt")
con <- file(sourcename,"r")
username <- readLines(con,n=1)
pw<-readLines(con,n=2)
close(con)

##### start time 
tic()
dbStartTime = as.numeric(Sys.time())
############Initialisierung############

user = "neo4j";
pass = "12345678";
auth = authenticate(user, pass, type = "basic");
url = "http://localhost:7474/db/data/";

graph = startGraph(url, username=user, password=pass)



#### DELETE GROUPS FOR NEXT ITERATION
cypher(graph,"MATCH (n:Group) DETACH DELETE n")

############Parameter############
# output
output = FALSE

#Weight of the Overlays of the intersections in the comparison
DividebyFactor = 2

#type of deviation function
deviation="Normalverteilung"

#the number of functions, for which values will be calculated
numberoffunctions = 1

numberOfRepeats=1

#sum of all shortest paths
sumOfSP = 0


#linear weight
lw = 1.5

#check if two vehicles can drive together
canDriveTogether<-1

#this determinates the amount of groups we wanna get, if the parameter of getAllGroups is set to FALSE
if(!exists("kGroups") ) {
	kGroups = 50
}
# How many vehicles will be in the query
if(!exists("LimitValue") ) {
	LimitValue = 10
}

if(!exists("testid")) {
	testid = -1
}
sigma<-30
VehID <- 0

#get all groups, then make this TRUE, else only about "kGroups" will be receieved
getAllGroups = FALSE

# this determinates how exacly alpha parameter will be assigned (the lower the exacter)
decreasOfAlpha = 0.001


###################=== Define Graph Edges ===###################
query="MATCH (n)-[r:NEIGHBOUR]->(m)  RETURN id(n) as from, id(m) as to, r.distance as weight, n.lat as fromlat,n.lon as fromlon, m.lat as tolat,m.lon as tolon"
edges=cypher(graph,query)
edges$label=edges$weight

dataString <- paste0("MATCH (v1s:loc)<-[:STARTATLOCATION]-(n:veh)-[:ENDATLOCATION]->(v1e:loc) RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat, id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn LIMIT ",LimitValue)

data <- cypher(graph, dataString)  #Einspeisung der HDV
#matrix for assigning the trucks into groups
matrixOfIntersectionQuality <- array(0, dim=c(length(data$v1slon),length(data$v1slon), numberoffunctions+1), dimnames = list(data$IDn,c(1:length(data$IDn)),1:(numberoffunctions+1)))
sumSPList<-matrix(0, nrow=length(data$IDn), ncol=1)

###################=== Define Graph Nodes ===###################
query="Match (n:loc) Return id(n) as id,n.lat as lat, n.lon as lon"
qnodes = cypher(graph,query)
nodes <- data.frame(id=unique(c(edges$from, edges$to)))
nodes$label <- nodes$id

## all nodes
nodelist <- cypher(graph, "MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id, n.type AS ntype ")

# create iGraph-graph from the edges
ig = graph_from_data_frame(edges, directed=F,vertices=nodes)

# set the attributes lat and lon for nodes
for ( i in 1:length(nodes[[1]]) ) {
  
  ig <- set.vertex.attribute(ig, "label", index=i, value=qnodes[i,1])
  ig <- set.vertex.attribute(ig, "lat", index=i, value=qnodes[i,2])
  ig <- set.vertex.attribute(ig, "lon", index=i, value=qnodes[i,3])
}

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
	  if (j > length(data$v1slon)) break
	  print(i)
	  print(j)
	  #Fahrzeug 2 Start-und Endpunkt
	  p13 <- c(data$v1slon[j], data$v1slat[j]);
	  p23 <- c(data$v1elon[j], data$v1elat[j]);
	  
	  
	  pa = p22 - p12;
	  pb = p23 - p13;

	  if(is.na(pa) || is.na(pb)) {	
	    break
	  }
	  
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
	  #############################
	  ### intersection compare
	  if(!is.null(pol1) && !is.null(pol2)) {
	    res = gIntersection(pol1, pol2)
	    if(!is.null(res)) {
	      subgraph<-induced.subgraph(ig,V(ig))
		  canDriveTogether<-EdgeValuation(subgraph,sid,eid,sid2,eid2,nodelist,res,sigma);
		  matrixOfIntersectionQuality[i,j,2] = canDriveTogether
	    }
		else{
			matrixOfIntersectionQuality[i,j,2]=0
	    }
	  }

	}
	
}

mTime=as.numeric(Sys.time())-mainTime
groupTime=as.numeric(Sys.time())

##### preparing the matrixOfIntersectionQuality for the computation of the groups
# find lowest value in matrixOfIntersectionQuality[,,2] without 0
newMatrix = matrixOfIntersectionQuality[,,2]
newMatrix[newMatrix == 0] <- 1
#this value is the lowest in matrixOfIntersectionQuality[,,2] without 0
cancelCondition = min(newMatrix)

#get all groups for getAllGroups = TRUE and only get kGroups for FALSE
if (getAllGroups) {
	gruppenPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,2],0.0000001,numberOfRepeats)
} else {
	##### create all groups 
	#get a starting value for alpha
	for (testValue in 1:20) {
		test01 = which(matrixOfIntersectionQuality[,,2] > (20-testValue)/20)
		if (length(test01) > 3) {
			alphaCut = (20-testValue)/20
			break
		}
	}
	
	#create initial GroupPool
	gruppenPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,2],alphaCut,numberOfRepeats)
	
	#determinate the exact value to get "kGroups"
	while (length(gruppenPool[1,]) < kGroups && cancelCondition < alphaCut) {
		
		alphaCut = alphaCut - (decreasOfAlpha)
		gruppenPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,2],alphaCut,numberOfRepeats)
		
	}
}	

storeGroups(gruppenPool, data,10,TRUE)
gTime=as.numeric(Sys.time())-groupTime

sumOfSP = 0
for (allVehInDataX in 1:length(data$IDn)) {
	vehID = data$IDn[allVehInDataX]
	sid = data$v1sid[allVehInDataX]
	eid = data$v1eid[allVehInDataX]
	if(exists(paste0("veh_",vehID,"_",sid,"_",eid))) {
		sumOfSP = sumOfSP + as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4])
	} else {
		sdvtep = assign(paste("veh",vehID,sid,eid,sep="_"),astr(sid,eid), env = .GlobalEnv);
		sumOfSP = sumOfSP + as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4])
	}
}

############################ SQL Logging  ##################################

cedges = cypher(graph,"MATCH ()-[r:NEIGHBOUR]->() RETURN count(r)")

query = paste("BEGIN;
INSERT INTO candidategroupssd (sigma,groupquantity,alpha,deviationType, inittime, sdtime, grouptime, formedgroups,
                             sumsp,testid) VALUES('",sigma,"','",kGroups,"','",alphaCut,"','",deviation,"','",dbTime,"','",mTime,"','",gTime,"','",length(gruppenPool[1,]),"','",sumOfSP,"','",testid,"');")

query = paste(query, "INSERT INTO groups (testid, vehicles) VALUES ")

for (g in 1:length(gruppenPool[1,])) {
	query = paste(query,"((SELECT testid FROM test ORDER BY testid DESC LIMIT 1) , '{")
	vehicles <- as.numeric(names(which(gruppenPool[,g]==1)))
	for(v in 1:length(vehicles)) {
		if(length(vehicles) != v) {
			query = paste(query, vehicles[v],",")
		} else {
			query = paste(query, vehicles[v])
		}
	}
	query = paste(query, "}')")
	
	if(length(gruppenPool[1,]) != g) {
		query = paste(query, ",")
	} else {
		query = paste(query, "; COMMIT;")
	}
}

log = TRUE


if(log) {
	drv <- dbDriver("PostgreSQL")
	con <- dbConnect(drv, dbname = "platoon",
					 host = "139.174.101.155", port = 5432,
					 user = username, password = pw)
  #print(query)
	df_postgres <- dbGetQuery(con, query)
	dbDisconnect(con)

	#print(df_postgres)
}