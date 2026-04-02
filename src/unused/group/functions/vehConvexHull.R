
vehConvexHull <-function(sid, eid, sp, pa, vehID, configData) {
	
	# check if the air line of the vehicle is not 0
	if((pa[1]^2 + pa[2]^2) != 0) {
		
		# !!!!!!!! parameters !!!!!!!!
		savingfactor=0.1
		repeats = 1 # this parameter determines, how many nodes of the shortest path get a "neighbour" for the convex hull (1=every node, 2=every second,...)
		beeline_points = 1/(1-savingfactor)-1 # this parameter determines, how far the points behind and before the starting and the ending points are placed
		wideness = 1/(1-savingfactor)-1 # this parameter determines, how wide the convex hull is constructed
		
		# query to get the route nodes
		query = paste0("MATCH (v:",configData$vehicle,")-[:",configData$startLocation,"]-(n:",configData$location,")-[:PNODE]-(r:RouteNode)-[:",configData$shortestPath,"]-(v:",configData$vehicle,") where id(v) = ",vehID, " with r match (r)-[:NEXT*]-(p:RouteNode) with p match (p)-[:PNODE]-(m:",configData$location,") return id(m) as mID, m.lon as lon, m.lat as lat")
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


#print("ready-vehConvexHull")