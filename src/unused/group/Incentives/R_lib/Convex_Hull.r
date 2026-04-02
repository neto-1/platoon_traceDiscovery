suppressWarnings(suppressMessages(library(jsonlite)))
suppressWarnings(suppressMessages(library(rgeos)))
# input parameters
args = commandArgs(trailingOnly=TRUE)
savingfactor = as.numeric(args[1])
set_id = as.numeric(args[2])
hull = args[3]
get_polygons = args[4]
# hull="convexHull"
# set_id=8674
# savingfactor=0.1
# some needed librarys (neo4j and json)
library(RNeo4j)
library(jsonlite)
library(sp)
library(rgeos)

# function to get the vehicles
queryVehicles <- function(graph, set_id=0) {
	
	# query for the pattern
	queryPattern = paste0('match (s:VehicleSet)-[:CONSISTS_OF]-(n:Vehicle) where s.id = ',set_id,' with n MATCH (v1s:loc)<-[:STARTS_AT]-(n:Vehicle)-[:ENDS_AT]->(v1e:loc)')
	# query for the return
	queryReturn = paste0(' RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat,id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn')
	### add the query up ###
	queryComplete = paste0(queryPattern,queryReturn)
	
	############ load the HDV ############
	vehicles <- cypher(graph, queryComplete) #Einspeisung der HDV

	return(vehicles)
}

# the intersection process
intersection <- function(pol1, pol2) {

	# if one hull is empty or not existend, the overlap is zero
	if (is.null(pol1) || is.null(pol2)) coordsAndOverlap = 0
	
	### intersection compare
	if(!is.null(pol1) && !is.null(pol2)) {

		res = gIntersection(pol1, pol2)			#res: polygon of the intersection
		if(!is.null(res)) {
						
			#polyg = pol@Polygons
			OverlapWith1 = res@polygons[[1]]@area / pol1@polygons[[1]]@area  #calculate the percentage of overlay
			OverlapWith2 = res@polygons[[1]]@area / pol2@polygons[[1]]@area
			
			
			#first output "Overlap" (the mean Overlap of the Intersection to the repectively polygons of the two vehicles)
			Overlap = (OverlapWith1 + OverlapWith2) / 2		# average overlay
			
			#matrixOfIntersectionQuality[j,i] = Overlap  #assign the two HDV for driving together
			
			
			#get the coordinates from the polygon "res" which contains the union of all vehicles in group Nr. "allGroups"
			coordinateLat = as.numeric(array(res@polygons[[1]]@Polygons[[1]]@coords[,1]))
			coordinateLon = as.numeric(array(res@polygons[[1]]@Polygons[[1]]@coords[,2]))
			coordinates = 0
			coordinates = c(coordinateLat[1],coordinateLon[1])
			
			#create the second output (the coordinates of the intersection-polygon)
			for (coordsLineNr in 2:length(res@polygons[[1]]@Polygons[[1]]@coords[,1])) {
				coordinates = c(coordinates, coordinateLat[coordsLineNr],coordinateLon[coordsLineNr])
			}

			coordsAndOverlap = c(coordinates, Overlap)
		}
	}
	return(coordsAndOverlap)
}

# the calculation of a vehicle hull
vehConvexHull <-function(sid, eid, sp, pa, vehID, savingfactor= 0.1) {
	
	# check if the air line of the vehicle is not 0
	if((pa[1]^2 + pa[2]^2) != 0) {
		
		# !!!!!!!! parameters !!!!!!!!
		repeats = 1 # this parameter determines, how many nodes of the shortest path get a "neighbour" for the convex hull (1=every node, 2=every second,...)
		beeline_points = 1/(1-savingfactor)-1 # this parameter determines, how far the points behind and before the starting and the ending points are placed
		wideness = 1/(1-savingfactor)-1 # this parameter determines, how wide the convex hull is constructed
		
		# query to get the route nodes
		query = paste0("MATCH (v:Vehicle)-[:STARTS_AT]-(n:loc)-[:PNODE]-(r:RouteNode)-[:SP_START]-(v:Vehicle) where id(v) = ",vehID, " with r match (r)-[:NEXT*]-(p:RouteNode) with p match (p)-[:PNODE]-(m:loc) return id(m) as mID, m.lon as lon, m.lat as lat")
		# get the route nodes through the cypher query 
		sdvtep = cypher(graph, query)
		# get the length of the shortest path of the vehicle
		dsum = as.numeric(cypher(graph, paste0("match (v:Vehicle) where id(v) = ", vehID, " return v.shortestpath_cost")))
		# the number of nodes in the shortest path
		dist = (length(sdvtep[,1]) - 1)
		
		assign("shortestPath",dsum,envir = .GlobalEnv)
		assign("nodeid", sdvtep[,1] , envir = .GlobalEnv)  #die liste des kürzesten weges der IDs der knoten wird hier gebraucht...
		
		# create the first point, by adding a distance to the starting point in the opposide direction of the bee line
		convexP1 = sp + pa * (-beeline_points)
		
		# the second point is the point on the opposide side of the air distance vector of the vehicle (behind the destination point)
		convexP2 = sp + pa + pa * beeline_points
		
		# rotate the vector pa 90 degree and get s, to make the convex hull wider
		s <- c(pa[2] * -1, pa[1])
		
		# subSetA includes additional convex points: the points in line of the bee line, which have to be added seperadely
		subSetA <-c(convexP1)
		subSetB <-c()
		
		# iterate through the nodes of the shortest path
		if(!is.null(sdvtep)) {
			for ( d in 1:length(sdvtep[,2]) ) {
				# consider only the nodes dependent from repeats, but also everytime the first and the last
				if((d %% repeats == 0 || d == length(sdvtep[,2]) || d == 1)  ) {
				
					# get the coordinates of the respectively node
					rplon = as.numeric(as.character(sdvtep[d,2]))
					rplat = as.numeric(as.character(sdvtep[d,3]))
					
					# add a point to the one side and the other side of the node
					var1 = c(rplon, rplat) + s * wideness
					var2 = c(rplon, rplat) - s * wideness
				
					# fill the subsets
					subSetA <- c(subSetA, var1)
					subSetB <- c(subSetB, var2)
				}
			}
			# add the other convex point to subSetA (which is also in line with the bee line)
			subSetA <- c(subSetA, convexP2); 

			# Resort subSetB, so that the points made up from subSetA and subSetB are in the right order, when added together
			resortedSubSetB <-c()
			lB = length(subSetB)
			for ( itr in 1:lB ) {
				i = lB - itr + 1
				if( i %% 2 == 0) {
					resortedSubSetB <- c(resortedSubSetB, c(subSetB[i-1], subSetB[i]))
				}
			}
			# add the subsets together
			subSet <- c(subSetA, resortedSubSetB)
			# create two lists for the latitude and longitute values
			subSetLon <- c()
			subSetLat <- c()
			for ( itr in 1:length(subSet) ) {
				if( itr %% 2 != 0) {
					lon = (subSet[itr])
					lat = (subSet[itr + 1])
					subSetLon <- c(subSetLon, lon)
					subSetLat <- c(subSetLat, lat)
				}
			}
			
			# close polygon (first and last point has to be the same)
			subSetLon <- c(subSetLon, subSet[1])
			subSetLat <- c(subSetLat, subSet[2])
			
			pol = SpatialPolygons(list( Polygons(list(Polygon(cbind(subSetLon,subSetLat))), ID="x2")))
			
			resCon = gConvexHull(pol, byid=FALSE, id = NULL)
			polCon = resCon@polygons[[1]]
			polygCon = polCon@Polygons
			
			return(resCon);
		}
	}
	
	print("store the vehicle hulls (in 2D so far)")
	return(NULL)
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
		if (i<=j) next
		
		p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j]);
		p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j]);
		#p12 = start of veh 1
		#p22 = end of veh 1
		
		p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i]);
		p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i]);
		
		pa = p22 - p12
		pb = p13 - p23
		# calculate the hulls of the vehicles
		pol1 = vehConvexHull(vehicles$v1sid[j], vehicles$v1eid[j], c(vehicles$v1slon[j], vehicles$v1slat[j]), pa, vehicles$IDn[j], savingfactor)
		pol2 = vehConvexHull(vehicles$v1sid[i], vehicles$v1eid[i], c(vehicles$v1slon[i], vehicles$v1slat[i]), pb, vehicles$IDn[i], savingfactor)
		
		
		# compare the polygons pol1 and pol2: the return value is a list of lat and lon values, which result in a polygon; the LAST VALUE is the incentive value!!!
		geometric_values = intersection(pol1, pol2)
		
		
		# just write the incentive, if it is big enough; every row: [id_vehicle_1, id_vehicle_2, incentive_value]
		if (geometric_values[length(geometric_values)] > 0) {
			incentivesR = rbind(incentivesR, c(vehicles$IDn[i], vehicles$IDn[j], as.numeric(round(geometric_values[length(geometric_values)],4))))
		}
	}
}

# just need the lines, where something is written
incentivesR = incentivesR[3:length(incentivesR[,1]),]

# return value
print(toJSON(incentivesR))
