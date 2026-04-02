###################=== INITIALISATION ===####################

library(RNeo4j)
library(tictoc)
library(sp)
library(rgeos)
library(httr)
library(jsonlite)
library(igraph)
#library(RMySQL)
library(RPostgreSQL) 

### output the actual start time of the algorithm
print(Sys.time())

######################################## initially load the functions ########################################
functions = c("compareVehVector","astr", "vehConvexHull", "lengthOfPlatoonDist", "getMax", "modifiedGeometricApproach", "formingDisjointGroups", "intersection", "formingNotDisjointGroups", "storeGroups")
 
###### find the path of the actual file ######
if(!exists("ownPath")) {
	ownPath = script.dir <- dirname(dirname(sys.frame(1)$ofile))
	
}

if(!exists("testid")) {
	testid = -1
}

if(!exists("vehtype")) {
	vehtype = "veh"
}


##load the functions in the vector "functions"
for (func in 1:length(functions)) {
	functionname = functions[func]
	
	## convert the actual path and add the needed source path ######
	completeSource = paste0(ownPath,"/functions/",functionname, ".R")
	source(completeSource)
	#print(completeSource)
}
########################################################################################################################



##### start time 
tic() #initial time #34582
dbStartTime = as.numeric(Sys.time())


############################## passworts and username for the graph database of neo4J ##############################
user = "neo4j";
#pass = "preprocessing";
pass = "x";
pass = "12345678";
auth = authenticate(user, pass, type = "basic")
url = "http://localhost:7474/db/data/";
graph = startGraph(url, username=user, password=pass)
########################################################################################################################


#### DELETE GROUPS FOR NEXT ITERATION
cypher(graph,"MATCH (n:Group) DETACH DELETE n")


############################################################ == PARAMETERS == ############################################################
#this determinates the amount of groups we wanna get, if the parameter of getAllGroups is set to FALSE
if(!exists("kGroups") ) {
	kGroups = 500
}
#get all groups, then make this TRUE, else only about "kGroups" will be receieved
getAllGroups = FALSE
# this determinates how exacly alpha parameter will be assigned (the lower the exacter)
decreasOfAlpha = 0.001


# How many vehicles will be in the query
if(!exists("LimitValue") ) {
	LimitValue = 100
}

# the lowest ID of the vehicles (in combination with LimitValue the IDs between VehID and VehID+LimitValue will be queried)
VehId = 0

# the amount of steps for the next passing of vehicles (if the first is WHERE id(n) > 3000, the next will be WHERE id(n) > (3000 + steps))
steps = 0

# check every condition or break if one fails
checkSingle = FALSE

#the number of functions, for which values will be calculated
numberoffunctions = 3

#Weight of the Overlays of the intersections in the comparison
DividebyFactor = 2

# linear weight
lw = 1.5

#The percentage of intersection, which is to small (HAS TO BE AT LEAST >0) (UNNESSASARY BECAUSE OF getAllGroups and kGroups)
BreakForSomePercent = 0.45

#The number of Repeats for the formingNotDisjunctGroups function: how often all vehicles should be tried to be assigned into a another group (if this number is low, there will be only groups with low  numbers of members)
numberOfRepeats = 1

# initial number of Groups in the Matrix of Group assign (matrixGruppen) (this parameter has always to be 1, other values make no sense)
numberOfGroups =1

#this value indicates, how good the other connections have to be
intersectionRoom = 0.25

#dimnames(matrixOfIntersectionQuality) <- list(c((TruckID$idnx),(TruckID$idnx)))

# output
output = FALSE
#output = TRUE
dbTime =  as.numeric(Sys.time()) - dbStartTime;
toc() #34582




##### scale of the map
# load the nodes
map <- cypher(graph,"MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id")
# scale the map (the difference between max lon and min lon, max lat and min lat)
scalingOfMap = (max(as.numeric(map$lon)) - min(as.numeric(map$lon))) +(max(as.numeric(map$lat)) - min(as.numeric(map$lat)))



AbfrageString = paste0("MATCH (v1s:loc)<-[:STARTATLOCATION]-(n:veh)-[:ENDATLOCATION]->(v1e:loc) WHERE id(n) > ", VehId -steps + steps, " AND NOT(id(n)=3446) RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat,id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn LIMIT ", LimitValue)
# The string for the query

############ load the HDV ############
vehicles <- cypher(graph, AbfrageString)  #Einspeisung der HDV
#WHERE toFloat(id(n)) = 3000 OR toFloat(id(n)) = 3001 OR toFloat(id(n)) = 3005 OR toFloat(id(n)) = 3006 OR toFloat(id(n)) = 3007 OR toFloat(id(n)) = 3008 OR toFloat(id(n)) = 3009 OR toFloat(id(n)) = 3010 OR toFloat(id(n)) = 3011 OR toFloat(id(n)) = 3012 OR toFloat(id(n)) = 3013 OR toFloat(id(n)) = 3014 OR toFloat(id(n)) = 3015 OR toFloat(id(n)) = 3016 OR toFloat(id(n)) = 3017 OR toFloat(id(n)) = 3019 OR toFloat(id(n)) = 3021 OR toFloat(id(n)) = 3022 OR toFloat(id(n)) = 3023 OR toFloat(id(n)) = 3024 OR toFloat(id(n)) = 3026 OR toFloat(id(n)) = 3027 OR toFloat(id(n)) = 3028 OR toFloat(id(n)) = 3029 OR toFloat(id(n)) = 3030 OR toFloat(id(n)) = 3031 OR toFloat(id(n)) = 3032 OR toFloat(id(n)) = 3033 OR toFloat(id(n)) = 3034
# WHERE id(n) > 3500
#WHERE id(n) > 3900 AND 
####### NOT(id(n)=3446) this vehicle has the same start and ending node!!!!!!!!


## save the shortest path in the extra column
vehicles3 = vehicles
vehicles3 = cbind(vehicles3,c(0))

#matrix for assigning the trucks into groups
matrixOfIntersectionQuality <- array(0, dim=c(length(vehicles$v1slon),length(vehicles$v1slon), numberoffunctions+1), dimnames = list(vehicles$IDn,c(1:length(vehicles$IDn)),1:(numberoffunctions+1)))


# Matrix of assigning the HDV to a group (row = HDV, column = group)
#matrixGruppen <- array(0,dim=(c(length(vehicles$v1slon),numberOfGroups)))


###############################################=== MAIN LOOP ===###############################################
tic() # time needed to iterate the vehicle combinations #34564568
mainTime = as.numeric(Sys.time())



##### iterate all vehicle combinations: save the values in matrixOfIntersectionQuality[,,x] for x = the number of the function and x+1 is the aggregated value

for ( j in 1:(length(vehicles$v1slon)-1) ) { #1:length(vehicles$v1slon) ) {
	
	for ( i in j+1:length(vehicles$v1slon) ) {  #29:length(vehicles$v1slon) ) {
		if (i > length(vehicles$v1slon)) break
		
		########################## ===== STEPWISE ALGORITHM ===== ##########################
		###################### STEP 1 - 90 Degree Check ######################
		
		compareVehVectorx = compareVehVector(vehicles,j,i)
		if( compareVehVectorx < 0 ) {
			if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
			next
		} else {
			matrixOfIntersectionQuality[j,i,1] = compareVehVectorx 
		}
		
		###################### STEP 2 - Extended Fermat Weber Problem ######################
		modifiedGeometricApproachx = modifiedGeometricApproach(vehicles,j,i,lw)
		if(modifiedGeometricApproachx[2] <= modifiedGeometricApproachx[1] ) {
			if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
			next
		} else {
			matrixOfIntersectionQuality[j,i,2] = ( modifiedGeometricApproachx[2] * lw) / (modifiedGeometricApproachx[1] *2)
		}
		
		
		###################### STEP 3 - Intersection ######################
		Intersectionx = intersection(vehicles,j,i,DividebyFactor,scalingOfMap)
		if( Intersectionx[length(Intersectionx)] <= 0 || is.null(intersection(vehicles,j,i,DividebyFactor,scalingOfMap) ) ) {
			if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
			next
		} else {
			matrixOfIntersectionQuality[j,i,3] = Intersectionx[length(Intersectionx)]
		}
		
		#matrixOfIntersectionQuality[j,i,4] = (matrixOfIntersectionQuality[j,i,3] + matrixOfIntersectionQuality[j,i,1] + matrixOfIntersectionQuality[j,i,2]) /numberoffunctions #assign the two HDV for driving together
		matrixOfIntersectionQuality[j,i,4] = matrixOfIntersectionQuality[j,i,3] * matrixOfIntersectionQuality[j,i,1] * matrixOfIntersectionQuality[j,i,2]  #assign the two HDV for driving together

		if (i == length(vehicles$v1slon) || j == length(vehicles$v1slon)) break
		
		########################## ===== END - STEPWISE ALGORITHM ===== ##########################
		
	}
}

############################################### End of the Main Loop (comparison of 2 HDV) ###############################################


mTime = as.numeric(Sys.time()) - mainTime
toc() #34564568


##### preparing the matrixOfIntersectionQuality for the computation of the groups
# findl lowest value in matrixOfIntersectionQuality[,,4] without 0
newMatrix = matrixOfIntersectionQuality[,,4]
newMatrix[newMatrix == 0] <- 1
#this value is the lowest in matrixOfIntersectionQuality[,,4] without 0
cancelCondition = min(newMatrix)


############################## Assign the vehicles into groups ##############################
####### time which is needed to assign the vehicles into groups 
tic() #4584329
gTime = as.numeric(Sys.time())


#### assining the vehicles in disjunct groups
#GroupVector <- formingDisjointGroups(matrixOfIntersectionQuality[,,4],BreakForSomePercent,intersectionRoom)

#get all groups for getAllGroups = TRUE and only get kGroups for FALSE
if (getAllGroups) {
	GroupPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,4],0.0000001,numberOfRepeats)
} else {
	##### create all groups 
	#get a starting value for alpha
	for (testValue in 1:20) {
		test01 = which(matrixOfIntersectionQuality[,,4] > (20-testValue)/20)
		if (length(test01) > 3) {
			alphaCut = (20-testValue)/20
			break
		}
	}
	
	#create initial GroupPool
	GroupPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,4],alphaCut,numberOfRepeats)
	
	#determinate the exact value to get "kGroups"
	while (length(GroupPool[1,]) < kGroups && cancelCondition < alphaCut) {
		
		alphaCut = alphaCut - (decreasOfAlpha)
		GroupPool <- formingNotDisjointGroups(matrixOfIntersectionQuality[,,4],alphaCut,numberOfRepeats)
		
		#sumOfGroups = which(matrixOfIntersectionQuality[,,4] > alphaCut)
	}
}	

##add the group vector to the input data
### vehicles = normal output
### vehicles2: ooutput with time stamp
#vehicles2 = cbind(vehicles,GroupVector)
vehicles2 = vehicles

geTime = as.numeric(Sys.time()) - gTime
toc() #4584329
######################################################################################################################################################

upTime = as.numeric(Sys.time())
tic()
storeGroups(GroupPool, vehicles2,10,TRUE)

toc()
upTime = as.numeric(Sys.time()) - upTime

timeData <- c(dbTime,mTime,geTime,upTime)


sumOfSP = 0
for (allVehInvehicles in 1:length(vehicles$IDn)) {
	vehID = vehicles$IDn[allVehInvehicles]
	sid = vehicles$v1sid[allVehInvehicles]
	eid = vehicles$v1eid[allVehInvehicles]
	if(exists(paste0("veh_",vehID,"_",sid,"_",eid))) {
		sumOfSP = sumOfSP + as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4])
	} else {
		sdvtep = assign(paste("veh",vehID,sid,eid,sep="_"),astr(sid,eid), env = .GlobalEnv);
		sumOfSP = sumOfSP + as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4])
	}
}


############################ MySQL Logging  ##################################
cedges = cypher(graph,"MATCH ()-[r:NEIGHBOUR]->() RETURN count(r)")
testid
query = paste("BEGIN;

INSERT INTO candidategroups (alpha, groupquantity, initializationt, pairwiseincentivest, initialgroupst,
                             persistgroupst, sumsp, formedgroups, testid)
VALUES('",alphaCut,"','",kGroups,"','",dbTime,"','",mTime,"','",geTime,"','",upTime,"','",sumOfSP,"','",length(GroupPool[1,]),"', ",testid,");")

query = paste(query, "INSERT INTO groups (testid, vehicles) VALUES ")

for (g in 1:length(GroupPool[1,])) {
	query = paste(query,"((SELECT testid FROM test ORDER BY testid DESC LIMIT 1) , '{")
	vehicles <- as.numeric(names(which(GroupPool[,g]==1)))
	for(v in 1:length(vehicles)) {
		if(length(vehicles) != v) {
			query = paste(query, vehicles[v],",")
		} else {
			query = paste(query, vehicles[v])
		}
	}
	query = paste(query, "}')")
	
	if(length(GroupPool[1,]) != g) {
		query = paste(query, ",")
	} else {
		query = paste(query, "; COMMIT;")
	}
}

#print(query)
pw <- {
  "admin123"
}


if(testid > -1) {
	drv <- dbDriver("PostgreSQL")
	con <- dbConnect(drv, dbname = "platoon",
					 host = "139.174.101.155", port = 5432,
					 user = "admin", password = pw)

	df_postgres <- dbGetQuery(con, query)
	dbDisconnect(con)

	print(df_postgres)
}





#con = dbConnect(MySQL(), user='admin', password='admin123', dbname='platoon', host='139.174.101.155', port=3306)
#query <- paste("INSERT INTO candidategroups (edges, vehicles, alpha, groupQuantity, formedGroups, sumSP, initializationT, pairwiseIncentivesT, initialGroupsT, persistGroupsT ) VALUES('",cedges, "','", LimitValue,"','",alphaCut,"','",kGroups,"','",length(GroupPool[1,]),"','",sumOfSP,"','",dbTime,"','",mTime,"','",geTime,"','",upTime,"')")


#dbSendQuery(con,query)	
#dbDisconnect(con)



####################################################### OUTPUT GRAPH #######################################################
if(output) {
	
	##for the simple.graph
	#map <- cypher(graph,"MATCH (n:loc) WHERE NOT(n.type = '') RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
	
	##for the germany veh.graph
	map <- cypher(graph,"MATCH (n:loc) RETURN n.location, n.lat AS lat, n.lon AS lon, id(n) AS id LIMIT 3000")
	####### Query only triangle and crosses  WHERE NOT(n.type = '')
	
	
	### only every 100th relation will be outputed due to overflow of data when 1.5M nodes are applied
	#rels <- cypher(graph,"MATCH (n)-[r:NEIGHBOUR]->(m) WHERE id(r)%100 = 0 RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")
	
	### rels for the "normal" 3000 nodes graph
	rels <- cypher(graph,"MATCH (n)-[r:NEIGHBOUR]->(m) RETURN n.lon, m.lon, n.lat, m.lat, id(r) as rid, id(n) as nid, id(m) as mid")
	#TruckID <- cypher(graph, "MATCH (n:veh) RETURN id(n) AS idnx LIMIT 50")

	plot(map$lon,map$lat)
	par(pch=22, col="black", lwd=1.5)
	for ( d in 1:length(rels$m.lon) ) {
		lines(c(as.numeric(rels$n.lon[d]), as.numeric(rels$m.lon[d])),  c(as.numeric(rels$n.lat[d]), as.numeric(rels$m.lat[d])))
	}

	par(pch=22, col="red", lwd=1.8)
	points(vehicles$v1slon,vehicles$v1slat)
	text(as.numeric(vehicles$v1slon)+0.1,as.numeric(vehicles$v1slat)+0.1, vehicles$IDn,cex = .8)


	par(pch=21, col="blue", lwd=1.8)
	points(vehicles$v1elon, vehicles$v1elat)
	text(as.numeric(vehicles$v1elon)+0.1,as.numeric(vehicles$v1elat)+0.1, vehicles$IDn,cex = .8)


	par(pch=21, col="grey", lwd=0.8)
	#par(pch=21, col="orange", lwd=1.8)
	curc = 0
	piec = rainbow(vehicles$GroupVector[length(vehicles[,1])])

	for ( d in 1:length(vehicles[[1]]) ) {
		if(curc != vehicles[[8]][d]) {
			
			curc = vehicles[[8]][d]
			par(pch=21, col=piec[curc], lwd=1.8)
		}	
		
		lines(c(as.numeric(vehicles$v1slon[d]), as.numeric(vehicles$v1elon[d])),  c(as.numeric(vehicles$v1slat[d]), as.numeric(vehicles$v1elat[d])))
	}

	par(pch=21, col="grey", lwd=0.8)
	for ( d in 1:length(vehicles$s.lon) ) {
		lines(c(as.numeric(vehicles$s.lon[d]), as.numeric(vehicles$e.lon[d])),  c(as.numeric(vehicles$s.lat[d]), as.numeric(vehicles$e.lat[d])))
	}
}
#####################################################################################################################################################################



