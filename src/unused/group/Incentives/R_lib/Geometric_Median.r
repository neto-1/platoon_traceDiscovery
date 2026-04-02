suppressWarnings(suppressMessages(library(jsonlite)))
# input parameters
args = commandArgs(trailingOnly=TRUE)
# input parameter from python
savings= as.numeric(args[1])
set_id = as.numeric(args[2])
savingFactorMedian = (as.numeric(args[3]))


# some needed librarys (neo4j and json)
library(RNeo4j)
library(jsonlite)

# function to get the vehicles
queryVehicles <- function(graph, set_id) {
	
	# query for the pattern
	queryPattern = paste0('match (s:VehicleSet)-[:CONSISTS_OF]->(n:Vehicle) where id(s) = ',set_id,' with n MATCH (v1s:loc)<-[:STARTS_AT]-(n:Vehicle)-[:ENDS_AT]->(v1e:loc)')
	# query for the return
	queryReturn = paste0(' RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat,id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn')
	### add the query up ###
	queryComplete = paste0(queryPattern,queryReturn)
	
	############ load the HDV ############
	vehicles <- cypher(graph, queryComplete) #Einspeisung der HDV

	return(vehicles)
}

# the calculation of geometric median and its incentive
modifiedGeometricApproach <- function(vehicles, j, i, lw=0.5) {

	##Parameter	
	p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j]); # start of veh 1
	p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j]); # end of veh 1
	
	p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i]) # start of veh 2
	p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i]) # end of veh 2
	
	# function describing the length of the platooning distance (2 ways from start to meeting; 2 ways from splitting to end; (1+savingFactorMedian) times 
	lengthOfPlatoonDist <- function(x) {
		sum ( sqrt( (p12[1] - x[1])^2 + (p12[2] - x[2])^2 ) + sqrt( (p13[1] - x[1])^2 + (p13[2] - x[2])^2 ) + sqrt( (p22[1] - x[3])^2 + (p22[2] - x[4])^2 ) + sqrt( (p23[1] - x[3])^2 + (p23[2] - x[4])^2 ) + sqrt( (x[1] -x[3])^2 + (x[2] - x[4])^2 ) * (2-lw))
	}
	
	###### compute extended fermar weber points with gradient approach
	g<-nlm(lengthOfPlatoonDist, x <- c(0,1,0,1), hessian=FALSE);
	###### results of gradient computation
	
	gresult <- g[2];
	g1p <- c(gresult[[1]][1],gresult[[1]][2]);
	g2p <- c(gresult[[1]][3],gresult[[1]][4]);
	
	###### compute linear distance of compared vehicles
	v1lin = p12 - p22
	v1lin = sqrt( v1lin[1]^2 + v1lin[2]^2);
	v2lin = p13 - p23;
	v2lin = sqrt( v2lin[1]^2 + v2lin[2]^2);
	singleLDis = v1lin + v2lin;
	
	###### compute linear platooned distance of compared vehicles
	s1lin = g1p - p12;
	s1lin = sqrt( s1lin[1]^2 + s1lin[2]^2);
	s2lin = g1p - p13;
	s2lin = sqrt( s2lin[1]^2 + s2lin[2]^2);
	glin = g1p - g2p;
	glin = sqrt( glin[1]^2 + glin[2]^2 )
	e1lin = g2p - p22;
	e1lin = sqrt( e1lin[1]^2 + e1lin[2]^2);
	e2lin = g2p - p23;
	e2lin = sqrt( e2lin[1]^2 + e2lin[2]^2);
	platoonedLDis = s1lin + s2lin + e1lin + e2lin + glin *(2-lw);

	#return the platooned distance and the distance of each vehicle
	return(c(platoonedLDis,singleLDis))
}

# the parameters for the database
pass = "12345678"
user = "neo4j"
url = "http://localhost:7474/db/data/"

# load the graph
graph = startGraph(url, username=user, password=pass)

# load the vehicles
vehicles <- queryVehicles(graph, set_id)

# create "empty" matrix to store the values
incentivesR <- array(0, dim=c(2,3))

# iterate through all vehicle combinations
for (i in 1:length(vehicles[,1])) { 
	for (j in 1:length(vehicles[,1])) {
		# just 1 comparison per pair
		if (i<=j) {
			next
		}
		
		# calculate the air distance and the platooning distance and return the 2 values
		geometric_values = modifiedGeometricApproach(vehicles, j, i, savingFactorMedian)
		
		# convert the median value to be between 0 and 1
		incentive_of_median = (( geometric_values[2] / geometric_values[1]) -1) * ((2/savingFactorMedian)-1)

		# just write the incentive if it is big enough, every row: [id_vehicle_1, id_vehicle_2, incentive_value]
		if (geometric_values[2] >= geometric_values[1]) {
			incentivesR = rbind(incentivesR, c(vehicles$IDn[i], vehicles$IDn[j], incentive_of_median))
			
		}
	}
}

# just need the lines, where something is written (the first to lines are empty through the creation process)
incentivesR = incentivesR[3:length(incentivesR[,1]),]

# return value
print(toJSON(incentivesR))
