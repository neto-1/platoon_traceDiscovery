
queryVehicles <- function(graph, configData, setID=0) {
	
	# ########## query for the relevant data to create vehicles ##########
	# #### query for pattern and random vehicles
	# queryPattern = paste0("MATCH (v1s:",configData$location,")<-[:",configData$startLocation,"]-(n:",configData$vehicle,")-[:",configData$endLocation,"]->(v1e:",configData$location,")")
	# # query for Where statement
	# queryWhere = paste0(" WHERE ",configData$ID,"(n) > 0")
	# # query for return statement
	# queryReturn = paste0(" RETURN toFloat(v1s.",configData$longitude,") AS v1slon, toFloat(v1s.",configData$latitude,") AS v1slat, toFloat(v1e.",configData$longitude,") AS v1elon, toFloat(v1e.",configData$latitude,") AS v1elat,",configData$ID,"(v1s) AS v1sid, ",configData$ID,"(v1e) AS v1eid, ",configData$ID,"(n) AS IDn skip ",skip," LIMIT ", LimitValue)
	
	#### query for set
	# query for the set-node and the vehicles connected to it
	# if there is a id given the selected set will be loaded, else (if setID=0) the last created set will be choosen

	if (setID == 0) {
		queryNewSet = paste0('match (s:',configData$Set,') return MAX(s.id)')
		setID = cypher(graph,queryNewSet)[1,1]
		querySet = paste0('match (s:',configData$Set,')-[:',configData$vehicleSet,']-(n:',configData$vehicle,') where s.id = ',setID)
	} else {
		querySet = paste0('match (s:',configData$Set,')-[:',configData$vehicleSet,']-(n:',configData$vehicle,') where s.id = ',setID)
	}
	# query for the pattern
	queryPattern = paste0(' with n MATCH (v1s:',configData$location,')<-[:',configData$startLocation,']-(n:',configData$vehicle,')-[:',configData$endLocation,']->(v1e:',configData$location,')')
	# query for the return
	queryReturn = paste0(' RETURN toFloat(v1s.lon) AS v1slon, toFloat(v1s.lat) AS v1slat, toFloat(v1e.lon) AS v1elon, toFloat(v1e.lat) AS v1elat,id(v1s) AS v1sid, id(v1e) AS v1eid, id(n) AS IDn')
	### add the query up ###
	queryComplete = paste0(querySet,queryPattern,queryReturn)
	
	############ load the HDV ############
	vehicles <- cypher(graph, queryComplete) #Einspeisung der HDV

	return(vehicles)
}


#print("ready-queryVehicles")