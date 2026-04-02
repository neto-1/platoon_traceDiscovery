

createIndividualGroupMatrices <- function(vehicles,iterateGroups){

	
	#give out the indizes of the group (the rows of vehicles of the same group)
	groupIndize = which(vehicles[,8]==iterateGroups)
	
	#this line gives the initial value to groupx...it could maybe be erased
	groupx = vehicles[groupIndize[1],]
	
	#create a group for every number(also when the entrys are "NA"), otherwise the for-goingThroughGroups loop will not work for not existing groups
	#assign(paste("GroupNr",iterateGroups,sep="_"),groupx, env = .GlobalEnv)
	#identify the members of the groups out of the input (iterate over all members of the input data)
	if(length(groupIndize) > 1) {
		#we only get (and want) groups with a size of 2 or more!
		for (memberOfGroup in 2:length(groupIndize)) {
			#add the next member to the auxiliary variable groupx
			groupx = rbind(groupx,vehicles[groupIndize[memberOfGroup],])
			
			# if the group is full and all members are added, we declare a matrix: GroupNr_x with x as the number of the group
			if (length(groupIndize) == memberOfGroup) {
				Ausgabe = assign(paste("GroupNr",iterateGroups,sep="_"),groupx, env = .GlobalEnv) #this produces a global variable...it is unnessassary, execpt the code is in a for-loop and is not an external function
			}
		}
	}
	
	return(Ausgabe)
}

#print("ready-createIndividualGroupMatrices")


#rm(list=ls())
