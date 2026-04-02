
intersection <- function(vehicles, j, i, configData) {
	###################### STEP 3 - Intersection ######################
	coordsAndOverlap = 0
	p12 <- c(vehicles$v1slon[j], vehicles$v1slat[j]);
	p22 <- c(vehicles$v1elon[j], vehicles$v1elat[j]);
	#p12 = start of veh 1
	#p22 = end of veh 1
	
	p13 <- c(vehicles$v1slon[i], vehicles$v1slat[i]);
	p23 <- c(vehicles$v1elon[i], vehicles$v1elat[i]);
	#p13 = start of veh 2
	#p23 = end of veh 2
	
	sid = vehicles$v1sid[j]
	#start and end id of the two nodes
	eid = vehicles$v1eid[j]
	
	sid2 = vehicles$v1sid[i]
	eid2 = vehicles$v1eid[i]
	#start and end id of the two nodes
	
	#vehicle ID
	veh1ID = vehicles$IDn[j]
	veh2ID = vehicles$IDn[i]
	
	pa = p22 - p12
	pb = p13 - p23
	### convex envelope
	pol1 = vehConvexHull(sid, eid, p12, pa, veh1ID,configData)
	pol2 = vehConvexHull(sid2, eid2, p13, pb, veh2ID,configData)
	if (is.null(pol1) || is.null(pol2) ) coordsAndOverlap = 0
	
	### intersection compare
	if(!is.null(pol1) && !is.null(pol2)) {

		res = gIntersection(pol1, pol2)			#res: polygon of the intersection
		if(!is.null(res)) {
						
			#polyg = pol@Polygons
			OverlapWith1 = res@polygons[[1]]@area / pol1@polygons[[1]]@area  #calculate the percentage of overlay
			OverlapWith2 = res@polygons[[1]]@area / pol2@polygons[[1]]@area
			
			#first output "Overlap" (the mean Overlap of the Intersection to the repectively polygons of the two vehicles)
			Overlap = (OverlapWith1 + OverlapWith2) / configData$DividebyFactor		# average overlay
			
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



#print("ready-Intersection")


#rm(list=ls())
