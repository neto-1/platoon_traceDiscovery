
storeGroups <- function(GroupPool, vehicles, uploadtoNeo = TRUE,configData) {


	#iterate through all groups
	#for (allGroups in 1:length(GroupPool[1,])) {
	for (allGroups in 1:ncol(GroupPool)) {
		
		# this line has to be changed later!!!!!!!!!!!!!!!!!!!!!!!XXXXXXXXX!!!!!!!!!!!
		# if there is only one group to upoad, the matrix "GroupPool" is seen as a vector and has only one dimension
		# in formingNotDisjointGroups a dummy group is inserted with the value of 0.1 in each row, so that "GroupPool" is still a matrix with 2 dimensions
		if ( length(which(GroupPool[,allGroups] == 0.1)) > 0) next
		
		##################### create a vector which contains the polygon information #####################
		# find the row of the vehicles in GroupPool
		
		vehNr = which(GroupPool[,allGroups] == 1)

		#### create the first two polygons to merge them later
		# create first polygon
		
		
		pol1 = vehConvexHull(vehicles$v1sid[vehNr[1]], vehicles$v1eid[vehNr[1]], c(vehicles$v1slon[vehNr[1]],vehicles$v1slat[vehNr[1]]), c(vehicles$v1elon[vehNr[1]],vehicles$v1elat[vehNr[1]])-c(vehicles$v1slon[vehNr[1]],vehicles$v1slat[vehNr[1]]), vehicles$IDn[vehNr[1]],configData)
		if (length(vehNr) > 1) {
		
			pol2 = vehConvexHull(vehicles$v1sid[vehNr[2]], vehicles$v1eid[vehNr[2]], c(vehicles$v1slon[vehNr[2]],vehicles$v1slat[vehNr[2]]), c(vehicles$v1elon[vehNr[2]],vehicles$v1elat[vehNr[2]])-c(vehicles$v1slon[vehNr[2]],vehicles$v1slat[vehNr[2]]), vehicles$IDn[vehNr[2]],configData)
		}
		else {
			pol2 = pol1
		}
		
		# create union of vehicle 1 and 2
		if(!(is.null(pol1) || is.null(pol2))) {
			pol1 = gUnion(pol1, pol2)
			
		}
		
		# if there are more than two vehicles do the following
		if(length(vehNr) > 2) {
			for (allVeh in 3:length(vehNr)) {
				#create convexhull for vehicle 3 to X
				pol2 = vehConvexHull(vehicles$v1sid[vehNr[allVeh]], vehicles$v1eid[vehNr[allVeh]], c(vehicles$v1slon[vehNr[allVeh]],vehicles$v1slat[vehNr[allVeh]]), c(vehicles$v1elon[vehNr[allVeh]],vehicles$v1elat[vehNr[allVeh]])-c(vehicles$v1slon[vehNr[allVeh]],vehicles$v1slat[vehNr[allVeh]]), vehicles$IDn[vehNr[allVeh]], configData)
				#if the convex hull exists add it to the existing union
				if(!(is.null(pol1) || is.null(pol2))) pol1 = gUnion(pol1, pol2)
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
		## coord = coordinates
		##############################################################################################################################
		
		
		
		
		##################### create the relationships from group to all vehicles #####################
		# create a group and also create a node for its Polygon, the Polygon contains the coordinates of the convex hull
		qry2 = paste0('CREATE (g:',configData$Group,'{weight: 0}) with g create (g)-[:',configData$groupHull,']->(p:',configData$Polygon,'{name: id(g), ',configData$Poly,': [',coordinates[1])
		
		# add the coordinates to the string
		for (dia in 2:length(coordinates)) {
			qry2 = paste0(qry2, ', ',coordinates[dia])
		}
		qry2 = paste0(qry2 ,', ',coordinates[1],', ',coordinates[2],']}) WITH g MATCH (n:',configData$vehicle,') WHERE id(n)=')
		
		
		# match the vehicles in that group, iterate to add all vehicle of the group
		for ( di in 1:length(vehNr) ) {
			lindex = vehicles$IDn[vehNr[di]]
			if(di <= 1) {
				qry2 = paste0(qry2, lindex)
			} else {
				qry2 = paste0(qry2, ' OR id(n)=' ,lindex)
			}
		}

		# the final qrerry for neo4j, this is the part, where a relation from g (with Property = Poly, where the polygon is stored) to the vehicles n is created 
		qry2 = paste0(qry2, ' CREATE (g)-[:',configData$vehicleGroup,']->(n)')
		
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