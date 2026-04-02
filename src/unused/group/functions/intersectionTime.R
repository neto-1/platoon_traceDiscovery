
intersectionTime <- function(vehicles, j, i, configData,typeOfHull) {
	###################### STEP 3 - Intersection ######################
	coordsAndOverlap = 0
	#p12 = start of veh 1
	#p22 = end of veh 1
	
	#create a vector for the lower path
	p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j], vehicles$startEarly[j]);
	p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j], vehicles$endEarly[j]);
	#print(p12)
	# create a vector for the upper path
	p12late <- c(vehicles$v1slon[j], vehicles$v1slat[j], vehicles$startLate[j]);
	p22late <- c(vehicles$v1elon[j], vehicles$v1elat[j], vehicles$endLate[j]);
	#print(p12late)
	#create lower and upper vector for veh 2
	p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i], vehicles$startEarly[i]);
	p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i], vehicles$endEarly[i]);
	p13late <- c(vehicles$v1slon[i], vehicles$v1slat[i], vehicles$startLate[i]);
	p23late <- c(vehicles$v1elon[i], vehicles$v1elat[i], vehicles$endLate[i]);
	
	#p13 = start of veh 2
	#p23 = end of veh 2
	
	#start and end id of the two nodes
	sid = vehicles$v1sid[j]
	eid = vehicles$v1eid[j]
	#print(sid)
	#print(eid)
	sid2 = vehicles$v1sid[i]
	eid2 = vehicles$v1eid[i]
	#start and end id of the two nodes
	
	#vehicle ID
	veh1ID = vehicles$IDn[j]
	veh2ID = vehicles$IDn[i]
	#print(veh1ID)
	paLow = p22 - p12
	pbLow = p23 - p13
	#print(paLow)
	paLate = p22late - p12late
	pbLate = p23late - p13late
	#print(paLate)
	# create the over-all vector, starting at earliest time and ending in latest time
	pa = p22late - p12
	pb = p23late - p13
	
	### convex envelope
	switch(typeOfHull,
		# normal convexHull, with air distance and shortest Path
		convexHull={
			pol1 = vehConvexHullTime(sid, eid, p12, p12late, pa, paLow, paLate, veh1ID, configData)
			pol2 = vehConvexHullTime(sid2, eid2, p13, p13late, pb, paLow, pbLate, veh2ID, configData)	
		},
		# convex Hull is an elipse
		elipse={
			pol1 = elipseHull(vehicles, j, ShortestPath, configData)
			pol2 = elipseHull(vehicles, i, ShortestPath, configData)
			
			# delete the last column where every value is 0
			pol1 = pol1[,1:2]
			pol2 = pol2[,1:2]
		}
	)

	
	commonPoints = rbind(pol1,pol2)
	
	commonPoints = commonPoints[,1:2]
	# for (i in 1:length(commonPoints[,1])){
		# for (j in 1:length(commonPoints[1,])) {
			# commonPoints[i,j] = round(commonPoints[i,j], digits = 2)
		# }
	# }

	
	#print(commonPoints)
	commonHull = convhulln(commonPoints, options="FA")
	
	pol1Hull = convhulln(pol1, options="FA")
	pol2Hull = convhulln(pol2, options="FA")
	#print(pol1Hull)
	#print(pol2Hull)
	returnValue = c(pol1Hull$vol, pol1Hull$area, pol2Hull$vol, pol2Hull$area, commonHull$vol, commonHull$area)
	return(returnValue)
}



#print("ready-Intersection")


#rm(list=ls())



