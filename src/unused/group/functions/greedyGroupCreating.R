
greedyGroupCreating <- function(incentivesR, groupCreatingParameters) {

	####initializate all parameters
	# number of group, which should be created (minimum)
	kGroups = groupCreatingParameters$kGroups
	# the steps in which alphaCut will be decreased (higher steps: more performance but the number of groups can be much more than kGroups, smaller steps: lower performance, but the number of Groups will be more near kGroups)
	decreasOfAlpha = groupCreatingParameters$decreasOfAlpha
	# when alphaCut is decreased to this value, the iteration will be canceled and the algorithm stops
	cancelCondition = groupCreatingParameters$cancelCondition

	if (kGroups < 1) {
		
		if (max(incentivesR) > 0) {
			incentivesR= incentivesR * (1/max(incentivesR))
		}
		alphaCut <- kGroups
		groupPool <- formingNotDisjointGroups(incentivesR,alphaCut)[[1]]
		numberOfGroups <- formingNotDisjointGroups(incentivesR,alphaCut)[[2]]
		returnedValueGroupPool = list(groupPool=groupPool,alphaCut=alphaCut, numberOfGroups=numberOfGroups)
		
	} else {
		
		####get a starting value for alpha: there needs to be some values in incentivesR, so that the function doesnt crash!
		# alphaCut represents the parameter "breakforsomepercent" and cuts out all values which are smaller than it, so that only the top values will be taken into account
		# if there arent enough values set alphaCut to a low number near 0
		if (length(which(incentivesR > 0)) <2) {
			alphaCut = 0.00001
		} else {
			# norm the incentive matrix R so that alphaCut can be calculated more easily
			incentivesR= incentivesR * (1/max(incentivesR))
			
			for (testValue in 1:20) { #the testing for an initial value is chosen freely, here it is 20 steps
				numberOfEntrys = which(incentivesR > (20-testValue)/20)
				# as soon as there are more than 3 values the loop can break and the function "formingNotDisjointGroups" can be used
				
				if (length(numberOfEntrys) > 1) {
					alphaCut = (20-testValue)/20
					break
				}
			}
		}
		
		#create initial groupPool, the function "formingNotDisjointGroups" executes with default settings except for the matrix and the alphaCut
		groupPool <- formingNotDisjointGroups(incentivesR,alphaCut)
		numberOfGroups = groupPool[[2]]
		groupPool = groupPool[[1]]

		###### determine the needed number of groups
		## if there are no incentives, a group of all vehicles will be returned
		# check if there is more than one group
		if (numberOfGroups > 1) {
			#this while loop determinate the exact value of alphaCut to get kGroups but calculates all possible groups for all values, which are bigger than alphaCut in the matrix of incentivesR
			while (length(groupPool[1,]) < kGroups && cancelCondition < alphaCut && alphaCut > decreasOfAlpha) {
				# decrease alphaCut
				alphaCut = alphaCut - (decreasOfAlpha)
				
				# calculate all possible groups
				groupPool <- formingNotDisjointGroups(incentivesR,alphaCut)[[1]]
				numberOfGroups <- formingNotDisjointGroups(incentivesR,alphaCut)[[2]]
			}
		}
		
		## add actual alphaCut for the output
		returnedValueGroupPool = list(groupPool=groupPool,alphaCut=alphaCut, numberOfGroups=numberOfGroups)
	}
	
	return(returnedValueGroupPool)
}
	




######this counts the size of the groups in groupPool
###for (summenzaehler in 1:length(groupPool[1,])) { print(sum(groupPool[1:(length(groupPool[,1])-1),summenzaehler])) }


#print("ready-creatingGroupPoolMatrix")