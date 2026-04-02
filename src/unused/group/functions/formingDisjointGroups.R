


formingDisjointGroups <- function(incentivesR, BreakForSomePercent=0.2, intersectionRoom = 0.25) {

	###Parameter###
	##BreakForSomePercent: The percentage of intersection, which is to small  (standard: BreakForSomePercent = 0.2)
	

	# initial number of Groups in the Matrix of Group assign (matrixGruppen) (this parameter has always to be 1, other values make no sense)
	numberOfGroups =1

	#intersectionRoom: this value indicates, how good the other connections have to be (standard: intersectionRoom = 0.25)

	# Matrix of assigning the HDV to a group (row = HDV, column = group)
	matrixGruppen <- array(0,dim=(c(length(incentivesR[,1]),numberOfGroups)))

	zaehler = 1
	
	####### Initial befüllung der matrixGruppen ######
	matrixGruppen[getMax(incentivesR)[2],1]=1		# the 2 vehicle with the most intersection will be put in group 1, so that the row and...
	matrixGruppen[getMax(incentivesR)[1],1]=1		# ...column of the incentivesR will be the rows set to 1 for the matrixGruppen
	
	incentivesR[getMax(incentivesR)[2],getMax(incentivesR)[1]] = BreakForSomePercent	#the former highest value will be set to BreakForSomePercent


	s=1
	while (s<length(incentivesR[,1])+1) {								# the diagonal of the matrix will be set to BreakForSomePercent
		incentivesR[s,s]=BreakForSomePercent
		s=s+1
	}	
	
	while (max(incentivesR) > BreakForSomePercent) {
		
		
		NotInAGroup = TRUE		#variable indicating, if one of the vehicles is already in a group
		for (u in 1:1) {
		 #this loop is only for help, because of the break parameter....HIER GIBTS BESTIMMT WAS BESSERES!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			#test if i is already in a group
			print("jajsdfjlsadkjfk")
			if (sum(matrixGruppen[getMax(incentivesR)[1],]) > 0) {
				
				NotInAGroup = FALSE	#for this has to be FALSE, so that the algorithm doesn't go in the other loop later
				#test if vehicle j is also already in a group
				if (sum(matrixGruppen[getMax(incentivesR)[2],]) > 0) {
					break
				}

				#print(getMax(t(matrixGruppen[getMax(incentivesR)[1],]))[1]) #das hier gibt die gruppe aus, in der fahrzeug i (matrixGruppen[getMax(incentivesR)[1]) bereits ist
				# this is the group, in which vehicle i is already assigned
				l = getMax(t(matrixGruppen[getMax(incentivesR)[1],]))[1]
				
				#iterate over all vehicles to find the members of l
				for (k in 1:length(incentivesR[,1])) {

					if (matrixGruppen[k,l] == 1) {	#find every member of the group l
						
						
						#löschen ab hier
							# if(zaehler > 72) {
								# print(paste(getMax(incentivesR)[2], l, "hier ist es"))
								# print(incentivesR[getMax(incentivesR)[2],k] + incentivesR[k,getMax(incentivesR)[2]])
								# print( max(max(incentivesR)-intersectionRoom , 0   ))
							# }
						#löschen bis hier
						
						

						if (incentivesR[getMax(incentivesR)[2],k] + incentivesR[k,getMax(incentivesR)[2]] <= max(max(incentivesR)-intersectionRoom, 0 )) {	#können die beiden per intersection zusammen fahren?	
						# this condition proves if the two vehicles can drive together
						# "incentivesR[getMax(incentivesR)[2],k]" is the amount of incentive to drive together
						# the amount of incentive to drive together has to be at least the actuell max value substraced by the value of intersectionRoom
						# the value which has to be satisfied is the difference between the max value of the incentivesR and the intersectionRoom or 0
						
						
							break #EIGENTLICH nicht nur break sondern nächste Gruppe überprüfen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
						}
					}
					# after every member is checked vehicle j can also be assigned to group l
					if (length(incentivesR[,1]) == k) {		
						matrixGruppen[getMax(incentivesR)[2],l] = 1
					}
				}
			}

			#test if j is already in a group
			if (sum(matrixGruppen[getMax(incentivesR)[2],]) > 0) {
				NotInAGroup = FALSE
				#test if vehicle i is also already in a group (KANN VIELLEICH WEGGELASSEN WERDEN, DA ES SCHON OBEN ÜBERPRÜFT WURDE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
				if (sum(matrixGruppen[getMax(incentivesR)[1],]) > 0) {
					break
				}

				#print(getMax(t(matrixGruppen[getMax(incentivesR)[2],]))[1]) #das hier gibt die gruppe aus, in der fahrzeug i (matrixGruppen[getMax(incentivesR)[1]) bereits ist
				
				# this is the group, in which vehicle j is already assigned
				l = getMax(t(matrixGruppen[getMax(incentivesR)[2],]))[1]
				#iterate over all vehicles to find the members of l
				for (k in 1:length(incentivesR[,1])) {

					if (matrixGruppen[k,l] == 1) {	#find every member of the group l
						
						if (incentivesR[getMax(incentivesR)[1],k] + incentivesR[k,getMax(incentivesR)[1]] <=  max(max(incentivesR)-intersectionRoom, 0 ) ) {	#können die beiden per intersection zusammen fahren?
							 #EIGENTLICH nicht nur break sondern nächste Gruppe überprüfen!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!	
							break
						}
					}	
					# after every member is checked vehicle j can also be assigned to group l
					if (length(incentivesR[,1]) == k) {				
						matrixGruppen[getMax(incentivesR)[1],l] = 1 
					}
				}
			}	
		}
		
		if (NotInAGroup) {#this only runs, if both vehicles have no group
			
			for (l in 1:numberOfGroups) {#iterate all existing groups
				
				for (k in 1:length(incentivesR[,1])) {#iterate all vehicles to find the HDV, which are driving in group l

					if (matrixGruppen[k,l] == 1) {	#all vehicles, which are in this group have the indicator 1
						#test, if vehicle i can drive with the members of group l, break if they cannot drive together
						if (incentivesR[getMax(incentivesR)[1],k] + incentivesR[k,getMax(incentivesR)[1]] <= max(incentivesR)-intersectionRoom ) {	#können die beiden per intersection zusammen fahren?
							break #EIGENTLICH nicht nur break sondern nächste Gruppe überprüfen
						}
						#test, if vehicle j can drive with the member of group l, break if they cannot drive together
						if (incentivesR[getMax(incentivesR)[2],k] + incentivesR[k,getMax(incentivesR)[2]] <= max(incentivesR)-intersectionRoom ) {	#können die beiden per intersection zusammen fahren?
							break #EIGENTLICH nicht nur break sondern nächste Gruppe überprüfen
						}
					}	
					# assign vehicle i and j in group l, after every member of group l is checked
					if (length(incentivesR[,1]) == k) {				
						matrixGruppen[getMax(incentivesR)[1],l] = 1			#wenn alles ok, werden die fahrzeuge i und j in gruppe l eingetragen
						matrixGruppen[getMax(incentivesR)[2],l] = 1
					}
				}
				# ABbruch, falls schon in eine Gruppe eingeplant, sonst doppeleinplanung in mehrere Gruppen, in denen i und j fahren könnten!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				if(matrixGruppen[getMax(incentivesR)[1],l] == 1) {
					break
				}
				
				# nächste 3 zeilen brauch man nicht mehr, wenn die 3 zeilen hier drüber klappen
				if (sum(matrixGruppen[getMax(incentivesR)[1]]) > 0 || sum(matrixGruppen[getMax(incentivesR)[2]]) > 0 ) {
					break
				}
				
				
				#If every group is tested and the vehicles are still in no group: add them together in a new opened group l+1
				if (l == numberOfGroups && sum(matrixGruppen[getMax(incentivesR)[1],]) == 0 && sum(matrixGruppen[getMax(incentivesR)[2],]) == 0 ) {   #if the last group is checked and there is no allocation for HDV k, add a new group
					numberOfGroups=numberOfGroups +1					# adding new group
					matrixGruppen <- cbind(matrixGruppen, c(0))			# adding new group
					matrixGruppen[getMax(incentivesR)[1],l+1] = 1						# add the vehicle k to the new group l+1
					matrixGruppen[getMax(incentivesR)[2],l+1] = 1
					break											# go to next vehicle
				}
			}
		}
		
		incentivesR[getMax(incentivesR)[2],getMax(incentivesR)[1]] = incentivesR[getMax(incentivesR)[2],getMax(incentivesR)[1]] - 0.2				# löschen des alten maximum wertes
		
	}
	
	groups <- matrix(0,nrow= length(incentivesR[,1]))
	
	for (x in 1:numberOfGroups) {#iterate all existing groups
				
		for (y in 1:length(incentivesR[,1])) {#iterate all vehicles to find the HDV, which are driving in group l

			if (matrixGruppen[y,x] == 1) {	#all vehicles, which are in this group have the indicator 1
										# adding new group
					groups[y,1]=x
			}
		}
	}
	
	return(groups)
}







#save.image("thisfunction.model")



#rm(list=ls())


#print("ready-formingDisjointGroups")