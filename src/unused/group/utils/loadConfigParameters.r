	

loadConfigParameters <- function(configData) {
	
	
	############################################################ == LOAD PARAMETERS == ############################################################
	#workingDirectory = assign("workingDirectory",configData$workingDirectory ,env = .GlobalEnv) 
	workingDirectory = configData$workingDirectory
	
	if(!exists("kGroups") ) {
		#kGroups = assign("kGroups",configData$kGroups ,env = .GlobalEnv) 
		kGroups = configData$kGroups
	}
	
	#getAllGroups = assign("getAllGroups",configData$getAllGroups, env = .GlobalEnv)
	getAllGroups = configData$getAllGroups
	
	#decreasOfAlpha = assign("decreasOfAlpha",configData$decreasOfAlpha ,env = .GlobalEnv) 
	decreasOfAlpha = configData$decreasOfAlpha
	
	if(!exists("LimitValue") ) {
		#LimitValue = assign("LimitValue",configData$LimitValue ,env = .GlobalEnv) 
		LimitValue = configData$LimitValue
	}
	
	#VehId = assign("VehId",configData$VehId ,env = .GlobalEnv) 
	VehId = configData$VehId
	
	#steps = assign("steps",configData$steps ,env = .GlobalEnv) 
	steps = configData$steps
	if(!exists("steps") ) {
		#steps = assign("steps",configData$steps ,env = .GlobalEnv) 
		steps = configData$steps
	}
	
	#checkSingle = assign("checkSingle",configData$checkSingle ,env = .GlobalEnv) 
	checkSingle = configData$checkSingle
	
	#numberoffunctions = assign("numberoffunctions",configData$numberoffunctions,env = .GlobalEnv )
	numberoffunctions = configData$numberoffunctions
	
	#DividebyFactor = assign("DividebyFactor",configData$DividebyFactor ,env = .GlobalEnv) 
	DividebyFactor = configData$DividebyFactor

	#lw = assign("lw",configData$lw ,env = .GlobalEnv) 
	lw = configData$lw

	#BreakForSomePercent = assign("BreakForSomePercent",configData$BreakForSomePercent ,env = .GlobalEnv) 
	BreakForSomePercent = configData$BreakForSomePercent

	#numberOfRepeats = assign("numberOfRepeats",configData$numberOfRepeats ,env = .GlobalEnv) 
	numberOfRepeats = configData$numberOfRepeats

	#numberOfGroups = assign("numberOfGroups",configData$numberOfGroups ,env = .GlobalEnv)
	numberOfGroups = configData$numberOfGroups

	#intersectionRoom = assign("intersectionRoom",configData$intersectionRoom ,env = .GlobalEnv) 
	intersectionRoom = configData$intersectionRoom

	#output = assign("output",configData$output ,env = .GlobalEnv) 
	output = configData$output
	############################################################ == PARAMETERS END == ############################################################


	############################################################ == LOAD Graph names == ############################################################
	#Group = assign("Group",configData$Group ,env = .GlobalEnv)
	Group = configData$Group	

	#location = assign("location",configData$location ,env = .GlobalEnv) 
	location = configData$location

	#vehicle = assign("vehicle",configData$vehicle ,env = .GlobalEnv) 
	vehicle = configData$vehicle

	#roads = assign("roads",configData$roads ,env = .GlobalEnv) 
	roads = configData$roads
	
	#endLocation = assign("endLocation",configData$endLocation ,env = .GlobalEnv) 
	endLocation = configData$endLocation

	#startLocation = assign("startLocation",configData$startLocation ,env = .GlobalEnv) 
	startLocation = configData$startLocation

	#vehicleGroup = assign("vehicleGroup",configData$vehicleGroup ,env = .GlobalEnv) 
	vehicleGroup = configData$vehicleGroup
	
	#Poly = assign("Poly",configData$Poly ,env = .GlobalEnv) 
	Poly = configData$Poly

	#shortestP = assign("shortestP",configData$shortestPath ,env = .GlobalEnv) 
	shortestPath = configData$shortestPath
	
	#distance = assign("distance",configData$distance ,env = .GlobalEnv) 
	distance = configData$distance

	#ID = assign("ID",configData$ID ,env = .GlobalEnv) 
	ID = configData$ID

	#latitude = assign("latitude",configData$latitude ,env = .GlobalEnv) 
	latitude = configData$latitude

	#longitude = assign("longitude",configData$longitude ,env = .GlobalEnv) 
	longitude = configData$longitude
	############################################################ == Graph names END == ############################################################
	
	comepleteListOfParameters = list(workingDirectory=workingDirectory,kGroups=kGroups,getAllGroups=getAllGroups,decreasOfAlpha=decreasOfAlpha,LimitValue=LimitValue,VehId=VehId,steps=steps,checkSingle=checkSingle,numberoffunctions=numberoffunctions,DividebyFactor=DividebyFactor,lw=lw,BreakForSomePercent=BreakForSomePercent,numberOfRepeats=numberOfRepeats,numberOfGroups=numberOfGroups,intersectionRoom=intersectionRoom,output=output,Group=Group,location=location,vehicle=vehicle,roads=roads,endLocation=endLocation,startLocation=startLocation,vehicleGroup=vehicleGroup,Poly=Poly,shortestPath=shortestPath,distance=distance,ID=ID,latitude=latitude,longitude=longitude)
	return(comepleteListOfParameters)
}
	