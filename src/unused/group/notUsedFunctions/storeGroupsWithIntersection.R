
storeGroups <- function(GroupPool, dataX, uploadtoNeo = TRUE) {
	
	#iterate through all groups
	for (allGroups in 1:length(GroupPool[1,])) {
		
		##################### create a vector which contains the polygon information #####################
		# find the row of the vehicles in GroupPool
		vehNr = which(GroupPool[,allGroups] == 1)
		
		# create the first two polygons
		pol1 = vehConvexHull(dataX$v1sid[vehNr[1]], dataX$v1eid[vehNr[1]], c(dataX$v1slon[vehNr[1]],dataX$v1slat[vehNr[1]]), c(dataX$v1elon[vehNr[1]],dataX$v1elat[vehNr[1]])-c(dataX$v1slon[vehNr[1]],dataX$v1slat[vehNr[1]]), dataX$IDn[vehNr[1]])
		pol2 = vehConvexHull(dataX$v1sid[vehNr[2]], dataX$v1eid[vehNr[2]], c(dataX$v1slon[vehNr[2]],dataX$v1slat[vehNr[2]]), c(dataX$v1elon[vehNr[2]],dataX$v1elat[vehNr[2]])-c(dataX$v1slon[vehNr[2]],dataX$v1slat[vehNr[2]]), dataX$IDn[vehNr[2]])
		# create union of vehicle 1 and 2
		if(!(is.null(pol1) || is.null(pol2))) {
			pol1 = gUnion(pol1, pol2)
			res = gIntersection(pol1, pol2)
		}
		
		# if there are more than two vehicles do the following
		if(length(vehNr) > 2) {
			for (allVeh in 3:length(vehNr)) {
				#create convexhull for vehicle 3 to X
				pol2 = vehConvexHull(dataX$v1sid[vehNr[allVeh]], dataX$v1eid[vehNr[allVeh]], c(dataX$v1slon[vehNr[allVeh]],dataX$v1slat[vehNr[allVeh]]), c(dataX$v1elon[vehNr[allVeh]],dataX$v1elat[vehNr[allVeh]])-c(dataX$v1slon[vehNr[allVeh]],dataX$v1slat[vehNr[allVeh]]), dataX$IDn[vehNr[allVeh]])
				#if the convex hull exists add it to the existing union
				if(!(is.null(pol1) || is.null(pol2))) {
					pol1 = gUnion(pol1, pol2)
					res = gIntersection(pol1, pol2)
				}
			}
		}
		
		if(!is.null(pol1) ) {
			
			#get the coordinates from the polygon "pol1" which contains the union of all vehicles in group Nr. "allGroups"
			coordinateLat = as.numeric(array(pol1@polygons[[1]]@Polygons[[1]]@coords[,1]))
			coordinateLon = as.numeric(array(pol1@polygons[[1]]@Polygons[[1]]@coords[,2]))
			coordinates = 0
			coordinates = c(coordinateLat[1],coordinateLon[1])
			
			for (coordsLineNr in 2:length(pol1@polygons[[1]]@Polygons[[1]]@coords[,1])) {
				coordinates = c(coordinates, coordinateLat[coordsLineNr],coordinateLon[coordsLineNr])
			}
		}
		
		if(!is.null(res)) {
			coordinateLatIntersec = as.numeric(array(res@polygons[[1]]@Polygons[[1]]@coords[,1]))
			coordinateLonIntersec = as.numeric(array(res@polygons[[1]]@Polygons[[1]]@coords[,2]))
			coordinatesIntersec = 0
			coordinatesIntersec = c(coordinateLatIntersec[1],coordinateLonIntersec[1])
			
			#create the second output (the coordinatesIntersec of the intersection-polygon)
			for (coordsLineNr in 2:length(res@polygons[[1]]@Polygons[[1]]@coords[,1])) {
				coordinatesIntersec = c(coordinatesIntersec, coordinateLatIntersec[coordsLineNr],coordinateLonIntersec[coordsLineNr])
			}
		}
		
		
		## coord = coordinates
		##############################################################################################################################
		
		
		##################### create the relationships from group to all vehicles #####################
		# create a group and match the vehicles which are in group Nr "allGroups"
		#add the property coordinates to "Poly"
		qry2 = paste0('CREATE (g:Group{Poly: [',coordinates[1])
		
		#add the union polygon 
		for (dia in 2:length(coordinates)) {
			qry2 = paste0(qry2, ', ',coordinates[dia])
		}
		
		# add the intersection polygon
		qry2 = paste0(qry2 ,', ',coordinates[1],', ',coordinates[2],'], PolyIntersec: [',coordinatesIntersec[1])
				for (dib in 2:length(coordinatesIntersec)) {
			qry2 = paste0(qry2, ', ',coordinatesIntersec[dib])
		}
		qry2 = paste0(qry2 ,', ',coordinatesIntersec[1],', ',coordinatesIntersec[2],']}) WITH g MATCH (n:veh) WHERE id(n)=')
		
		
		
		
		
		
		
		
		#iterate to add all vehicle of the group
		for ( di in 1:length(vehNr) ) {
			lindex = dataX$IDn[vehNr[di]]
			if(di <= 1) {
				qry2 = paste0(qry2, lindex)
			} else {
				qry2 = paste0(qry2, ' OR id(n)=' ,lindex)
			}
		}
		
		# the final qrerry for neo4j, this is the part, where a relation from g (with Property = Poly, where the polygon is stored) to the vehicles n is created 
		qry2 = paste0(qry2, ' CREATE (g)-[:vehgroup]->(n)')
		
		
		# the if is for testing cases, so that it will not be uploaded every time
		if(uploadtoNeo) {
			cypher(graph, qry2)
		} else {
			print("nothing is uploaded, because uploadtoNeo is set to FALSE")
		}
		
		
		
		
		
		##############################################################################################################################
		
		
	}
	return(NULL)
}



######this counts the size of the groups in matrixGruppen
###for (summenzaehler in 1:length(matrixGruppen[1,])) { print(sum(matrixGruppen[1:(length(matrixGruppen[,1])-1),summenzaehler])) }

##save.image("thisfunction.model")



#rm(list=ls())


#print("ready-storeGroups")