
storeVehicleHulls <- function(vehicles, uploadtoNeo = TRUE,configData) {
	
	#iterate through all vehicles considered
	for (vehicle in 1:length(vehicles[,1])) {

		# create the polygon
		pol1 = vehConvexHull(vehicles$v1sid[vehicle], vehicles$v1eid[vehicle], c(vehicles$v1slon[vehicle],vehicles$v1slat[vehicle]), c(vehicles$v1elon[vehicle],vehicles$v1elat[vehicle])-c(vehicles$v1slon[vehicle],vehicles$v1slat[vehicle]), vehicles$IDn[vehicle],configData)
		
		# if the polygon exists, do:
		if(!is.null(pol1) ) {
			#get the coordinates from the polygon "pol1"
			coordinateLat = as.numeric(array(pol1@polygons[[1]]@Polygons[[1]]@coords[,1]))
			coordinateLon = as.numeric(array(pol1@polygons[[1]]@Polygons[[1]]@coords[,2]))
			coordinates = 0
			coordinates = c(coordinateLat[1],coordinateLon[1])
			
			# save the values in coordinates
			for (coordsLineNr in 2:length(pol1@polygons[[1]]@Polygons[[1]]@coords[,1])) {
				coordinates = c(coordinates, coordinateLat[coordsLineNr],coordinateLon[coordsLineNr])
			}
		}
		##############################################################################################################################
		
		##################### create the relationships from vehicle to the polygon node #####################
		qry2 = paste0('MATCH (g:',configData$vehicle,') where id(g) = ',vehicles$IDn[vehicle], ' with g create (g)-[:',configData$vehicleHull,']->(p:',configData$Polygon,'{name: id(g), ',configData$Poly,': [',coordinates[1])
		
		for (dia in 2:length(coordinates)) {
			qry2 = paste0(qry2, ', ',coordinates[dia])
		}
		qry2 = paste0(qry2 ,', ',coordinates[1],', ',coordinates[2],']})')
		
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


#print("ready-storeGroups")