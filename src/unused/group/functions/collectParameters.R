
collectParameters <- function(configData, cancelCondition, kGroups, LimitValue, identifyGroupsBy="greedy") {
	
	dictionary = list(
		kGroups = kGroups,
		decreasOfAlpha = configData$decreasOfAlpha,
		cancelCondition = cancelCondition,
		droppingValue = configData$droppingValue,
		LimitValue = LimitValue,
		cliqueMin = configData$cliqueMin,
		identifyGroupsBy = identifyGroupsBy
	)
	
	
	return(dictionary)
}



#print("ready-Intersection")


#rm(list=ls())



