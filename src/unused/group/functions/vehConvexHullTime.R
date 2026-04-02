# ToDo describe imput parameters
# ToDo only start id and end id necessary
# ToDo rename parameters
vehConvexHullTime <-function(sid, eid, sp, spLate, pa, paLow, paLate, vehID,configData) {
	if((pa[1]^2 + pa[2]^2) != 0) {
		
		# !!!!!!!! parameters !!!!!!!!
		savingfactor=0.1
		repeats = 1 # this parameter determines, how many nodes of the shortest path get a "neighbour" for the convex hull (1=every node, 2=every second,...)
		beeline_points = 1/(1-savingfactor) - 1 # this parameter determines, how far the points behind and before the starting and the ending points are placed
		wideness = 1/(1-savingfactor) - 1 # this parameter determines, how wide the convex hull is constructed
		
		#print(paste0("veh_",vehID,"_",sid,"_",eid))
		#if shortest path doesn't exist: compute it
		if(exists(paste0("veh_",vehID,"_",sid,"_",eid))) {
			sdvtep = get0(paste0("veh_",vehID,"_",sid,"_",eid))
	
		} else {
			sdvtep = assign(paste("veh",vehID,sid,eid,sep="_"),astr(sid,eid), env = .GlobalEnv);
			
			if(!is.null(sdvtep)) {
				createSP = paste0("MATCH (n:",configData$vehicle,") WHERE ",configData$ID,"(n) = ",vehID," SET n.",configData$shortestPath," =",as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4]))
				#createSP = paste0("MATCH (n:veh) WHERE id(n) = ",vehID," SET n.SP =",as.numeric(get0(paste0("veh_",vehID,"_",sid,"_",eid))[1,4]))
				
				cypher(graph, createSP)
			}
		}
		
		
		# get the path length and the steps
		dsum = as.numeric(sdvtep[1,4]);
		
		# make a global variable for the node IDs and the shortest path
		assign("shortestPath",dsum,envir = .GlobalEnv)
		assign("nodeid", sdvtep[,1] , envir = .GlobalEnv)  #die liste des kürzesten weges der IDs der knoten wird hier gebraucht...
		
		
		# 180 degree of pa vector
		cpv1 = c(pa[1],pa[2]) * -1
		
		# convex point 1 before starting point in direction of negative bee line
		convexP1 = c(cpv1 * beeline_points + c(sp[1],sp[2]),sp[3])
		
		
		# convex point 2 (behind the destination node in direction of bee line
		convexP2 = c(c(sp[1],sp[2]) + c(pa[1],pa[2]) + cpv1 * beeline_points * -1,pa[3]+sp[3])
		#points(convexP2[1], convexP2[2])
		
		# 90 degree of pa vector for the wideness of the hull 
		s <- c(pa[2] * -1, pa[1]);
		
		
		### create Subsets for the 4 lines for the convex hull (left of the path, right of the path, over the path and under the path) 
		subSetAtime <-c(convexP1)
		subSetBtime <-c()
		subSetEaliestTime <-c()
		subSetLatestTime <-c()
		
		
		if(!is.null(sdvtep)) {
			for ( d in 1:length(sdvtep[,2]) ) {

				if((d %% repeats == 0 || d == length(sdvtep[,2]) || d == 1)  ) {
					rplon = as.numeric(as.character(sdvtep[d,2]));
					rplat = as.numeric(as.character(sdvtep[d,3]));

					
					# time parameter for the convex hull. it starts from the earliest time to the last time using pa[3]
					normalTime = (d/length(sdvtep[,2])) * pa[3]
					#time parameter for the earliest time using palow[3]
					lowTime = (d/length(sdvtep[,2])) * paLow[3]
					#time parameter for the latest time using palate[3]
					lateTime = (d/length(sdvtep[,2])) * paLate[3]
					
					#geografical coords
					var1 = c(rplon, rplat) + s * wideness
					var2 = c(rplon, rplat) - s * wideness
					
					# add time (the third dimension) to the points left and right of the path
					# var1time = c(rplon, rplat, sp[3] + normalTime)
					var1time = c(var1, sp[3] + normalTime)
					# var2time = c(rplon, rplat, sp[3] + normalTime)
					var2time = c(var2, sp[3] + normalTime)
		#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
					# fill subsets to the left and right of the path
					subSetAtime <- c(subSetAtime, var1time);
					subSetBtime <- c(subSetBtime, var2time);
					
					# time coords over and under the path
					expandingFactor = 0.5 #factor to expand the hull (must be in ]0,1])
					var3time = c(rplon, rplat,sp[3] + lowTime * expandingFactor)
					var4time = c(rplon, rplat,spLate[3] + lateTime * (2-expandingFactor))
					
					# fill subsets over and under the path
					subSetEaliestTime <- c(subSetEaliestTime, var3time);
					subSetLatestTime <- c(subSetLatestTime, var4time);
					
				}
			}
			
			
			###### create a matrix with all points of the 4 subsets (subSetAtime, subSetBtime, subSetEaliestTime, subSetLatestTime)
			# order the coords OVER the path
			subSetLatestTimeCoords = matrix(0,length(subSetLatestTime)/3,3)
			for (makeCoords in 1:(length(subSetLatestTime)/3)) {
				subSetLatestTimeCoords[makeCoords,1] = subSetLatestTime[makeCoords*3-2]
				subSetLatestTimeCoords[makeCoords,2] = subSetLatestTime[makeCoords*3-1]
				subSetLatestTimeCoords[makeCoords,3] = subSetLatestTime[makeCoords*3]
			}
			
			# order the coords UNDER the path
			subSetEaliestTimeCoords = matrix(0,length(subSetEaliestTime)/3,3)
			for (makeCoords in 1:(length(subSetEaliestTime)/3)) {
				subSetEaliestTimeCoords[makeCoords,1] = subSetEaliestTime[makeCoords*3-2]
				subSetEaliestTimeCoords[makeCoords,2] = subSetEaliestTime[makeCoords*3-1]
				subSetEaliestTimeCoords[makeCoords,3] = subSetEaliestTime[makeCoords*3]
			}
			
			# order the coords LEFT/RIGHT the path
			subSetAtimeCoords = matrix(0,length(subSetAtime)/3,3)
			for (makeCoords in 1:(length(subSetAtime)/3)) {
				subSetAtimeCoords[makeCoords,1] = subSetAtime[makeCoords*3-2]
				subSetAtimeCoords[makeCoords,2] = subSetAtime[makeCoords*3-1]
				subSetAtimeCoords[makeCoords,3] = subSetAtime[makeCoords*3]
			}
			
			# order the coords LEFT/RIGHT the path
			subSetBtimeCoords = matrix(0,length(subSetBtime)/3,3)
			for (makeCoords in 1:(length(subSetBtime)/3)) {
				subSetBtimeCoords[makeCoords,1] = subSetBtime[makeCoords*3-2]
				subSetBtimeCoords[makeCoords,2] = subSetBtime[makeCoords*3-1]
				subSetBtimeCoords[makeCoords,3] = subSetBtime[makeCoords*3]
			}
			
			# combine all 4 matrices, to give out all points for the convex hull
			allCoords = rbind(subSetLatestTimeCoords, subSetEaliestTimeCoords, subSetAtimeCoords, subSetBtimeCoords)

			return(allCoords);
		}
	}
}

elipseHull <- function(vehicles, j ,ShortestPath=1, configData) {

	startLat = vehicles$v1slat[j]
	startLon = vehicles$v1slon[j]
	endLat = vehicles$v1elat[j]
	endLon = vehicles$v1elon[j]
	# n is number of points per quadrant
	n <- 5
	qry = paste0("Match (n:Vehicle) where id(n) = ", vehicles$IDn[j]," return n.SP")
	
	sp_len = cypher(graph, qry)
	sp_len <- sp_len[[1]] / 98.21
	# (startLat,startLon) = Starting point coordinates
	# (EndLat,EndLon) = ending point coordinates
	
	p1 <- c(startLat, startLon)
	p2 <- c(endLat, endLon)

	
	# vector from p1 to p2
	v_p1_p2 <- p2 - p1

	# angle between [0, -1] and v_p1_p2
	cosang <- v_p1_p2 %*% c(0, -1)
	sinang <- length(-1*v_p1_p2[[1]])
	angle <- atan2(sinang, cosang)

	
	# vector from p1 to the center between p1 and p2 (equals the center of the ellipse)
	v_p1_center <- .5 * v_p1_p2
	# vector length
	v_p1_center_len <- sqrt(sum(v_p1_center^2))
	# center of the ellipse
	center <- p1 + v_p1_center
	# half the width of the ellipse (pythagoras)
	halfWidth <- sqrt(sp_len^2/4 + v_p1_center_len^2)
	# half the height equals the length of the ellipse
	halfHeight <- sp_len/2

	# points before rotation
	points <- list()
	# calculate points for the third quadrant
	
	i <- 1
	while (i <= n) {
		# magic!
		theta <- pi/2 * i / (n+1)
		fi <- pi - atan(tan(theta) * halfWidth/halfHeight)
		x <- center[[1]] + halfWidth * cos(fi)
		y <- center[[2]] + halfHeight * sin(fi)
		
		points[[i]] <- c(x, y)
		
		i = i +1
		
	}
	
	# mirror the points to the other quadrants
	i <- 1
	l <- length(points)
	
	while (i <= l) {
		
		point <- points[[i]]
		
		second_quadrant_point <- c(point[[1]], 2*center[[2]]-point[[2]])
		
		first_quadrant_point <- c(2*center[[1]]-point[[1]], 2*center[[2]]-point[[2]])
		fourth_quadrant_point <- c(2*center[[1]]-point[[1]], point[[2]])
		points[[length(points)+1]] <- second_quadrant_point
		points[[length(points)+1]] <- first_quadrant_point
		points[[length(points)+1]] <- fourth_quadrant_point
		i = i +1
	}
	
	# add points on the right, left, top and bottom
	points[[length(points)+1]] <- c(center[[1]]+halfWidth, center[[2]])
	points[[length(points)+1]] <- c(center[[1]]-halfWidth, center[[2]])
	points[[length(points)+1]] <- c(center[[1]], center[[2]]+halfHeight)
	points[[length(points)+1]] <- c(center[[1]], center[[2]]-halfHeight)

	# rotation matrix
	r <- matrix(
		c(cos(angle), -sin(angle), sin(angle), cos(angle)),
		nrow <- 2,
		ncol <- 2,
		byrow <- TRUE)
	# points after rotation
	rotatedPoints <- c()
	i <- 1
	while (i <= length(points)) {
		point <- points[[i]]
		# rotate points around center
		
		rotatedPoint <- (r %*% (point - center)) + center
		
		rotatedPoints[[length(rotatedPoints)+1]] <- rotatedPoint
		i = i +1
	}
	
	
	allCoords = matrix(0,nrow=length(rotatedPoints),ncol=3)
	for (i in 1:length(rotatedPoints)) {
		
		allCoords[i,1] = rotatedPoints[[i]][2]
		allCoords[i,2] = rotatedPoints[[i]][1]
		allCoords[i,3] = 0
		
	}
	
	# dummy matrix for "correct" output

	
	
	
	
	
	
	# returns a list of nodes with the format for n points: (matrix 3*n) where every row is a point (lat, lon, time)
	return(allCoords)
}
#print("ready-vehConvexHullTime")