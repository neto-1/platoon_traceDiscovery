


formingNotDisjointGroups <- function(MATR, BreakForSomePercent=0.2, numberOfRepeats=1, intersectionRoom = 0.25) {

	###Parameter###
	##BreakForSomePercent: The percentage of intersection, which is to small  (standard: BreakForSomePercent = 0.2)
	
	# initial number of Groups in the Matrix of Group assign (matrixGruppen) (this parameter has always to be 1, other values make no sense)
	numberOfGroups =1
	stillFoundANewGroup = TRUE
	#intersectionRoom: this value indicates, how good the other connections have to be (standard: intersectionRoom = 0.25)

	# Matrix of assigning the HDV to a group (row = HDV, column = group)
	matrixGruppen <- array(0,dim=(c(length(MATR[,1]),1)),dimnames= list(names(MATR[,1]),c(1) ) )
	
	# ####### Initial befüllung der matrixGruppen ######
	# matrixGruppen[getMax(MATR)[2],1]=1		# the 2 vehicle with the most intersection will be put in group 1, so that the row and...
	# matrixGruppen[getMax(MATR)[1],1]=1		# ...column of the MATR will be the rows set to 1 for the matrixGruppen
	
	# MATR[getMax(MATR)[2],getMax(MATR)[1]] = BreakForSomePercent	#the former highest value will be set to BreakForSomePercent

	## add BreakForSomePercent in the diagonal of the matrix, so that (obviously) vehicle i can always drive with vehicle i, since its the same vehicle
	s=1
	while (s<length(MATR[,1])+1) {								# the diagonal of the matrix will be set to BreakForSomePercent
		MATR[s,s]=BreakForSomePercent
		s=s+1
	}
	
	## double the matrix, so that out of every value in MATR a 2-vehicle group can be calculated
	MATR2 = MATR

	#assign a new row for a "quality bit"
	matrixGruppen = rbind(matrixGruppen, c(0))
	
	#### if there are no incentives in the matrix MATR, then an extra group containing all vehicles will be added, the quality bit for this group is zero and indicates, that no platoon exists for this set
	# check if there are no relevant values in MATR
	if (length(which(MATR>BreakForSomePercent)) < 1 ) {
		# add the group which includes every vehicle
		matrixGruppen = cbind(matrixGruppen, c(1))
		# set the quality bit for that group to 0
		matrixGruppen[length(matrixGruppen[,1]),2] = 0
		# count the new group
		#numberOfGroups= numberOfGroups +1
	}
	
	#### create a group of 2 vehicles for every value in MATR (therefore added MATR2)
	# check if there are values in MATR to create groups
	if (max(MATR2) > BreakForSomePercent) {
		# loop over every value in MATR to create a 2-vehicle-group
		while (max(MATR2) > BreakForSomePercent ) {
			numberOfGroups=numberOfGroups +1					# adding new group
			matrixGruppen <- cbind(matrixGruppen, c(0))			# adding new group
			matrixGruppen[getMax(MATR2)[1],numberOfGroups] = 1	#assign vehicle i
			matrixGruppen[getMax(MATR2)[2],numberOfGroups] = 1	#assign vehicle j
			MATR2[getMax(MATR2)[2],getMax(MATR2)[1]] = BreakForSomePercent #reset the current maximum value, so the algorithm can go to the next value
			matrixGruppen[length(matrixGruppen[,1]),numberOfGroups] = sum(2^(which(matrixGruppen[,numberOfGroups]==1))) # add a quality bit to ensure that there are no dublicate groups
		}
	}
	
	###### prepare the prepared matrix of groups for the building of bigger groups or the output
	# correct the number of groups for the deleted imaginary group
	numberOfGroups = numberOfGroups-1
	## delete the first column of matrixGruppen (which is a c(0) vector)
	matrixGruppen = matrixGruppen[,2:length(matrixGruppen[1,])]

	
	###### try to add vehicles to the existing 2-vehicle-groups
	# check if there are enough relevant values in MATR (there have to be at least 3 values to form bigger groups than groups with 2 vehicles)
	if ( !(length(which(MATR>BreakForSomePercent)) < 3 ) ) {
		while(stillFoundANewGroup) {
			stillFoundANewGroup = FALSE
		# #numberOfRepeats indicates, how often every vehicle will be checked
		# for (repeating in 1:numberOfRepeats) {
			#iterate all vehicles
			for (k in 1:length(MATR[,1])) {
				
				#iterate all still existing groups
				for (l in 1:numberOfGroups) {
					
					# if the last group was reached, break here and check the next vehicle
					if (l > numberOfGroups) break
					
					# if the actual vehicle k is already in group l, go to the next group
					if (matrixGruppen[k,l] == 1) next
					
					#find all vehicles in the group
					vehInGroup = which(matrixGruppen[,l]==1)
					
					#iterate all vehicles in that group
					for (m in 1:length(vehInGroup)) {
						
						#if the actual vehicle k can not drive with any vehicle in the group, then break
						if (MATR[k,vehInGroup[m]] < BreakForSomePercent) break #break, if the vehicle cant drive with some vehicle of this group
						
						#if the last vehicle is checked, do the following
						if (m == length(vehInGroup)) {
						
							#add a new column, since we are creating a new group
							matrixGruppen = cbind(matrixGruppen, matrixGruppen[,l])
							numberOfGroups = numberOfGroups+1
							
							# add the vehicle in the new created group
							matrixGruppen[k,length(matrixGruppen[1,])]=1
							
							#calculate the QualityBit, which is unique
							QualityBit = sum(2^(which(matrixGruppen[,numberOfGroups]==1)))
							
							# if there is the same QualityBit already, then we will have to delete the group
							if( length(which(matrixGruppen[length(matrixGruppen[,1]),] == QualityBit )) > 0 ) {
								# delete the last group
								matrixGruppen = matrixGruppen[,1:(length(matrixGruppen[1,])-1) ]
								numberOfGroups = numberOfGroups-1
								# if there is no QualityBit like the one calculated above, then assign it to the group
							}	else {
								matrixGruppen[length(matrixGruppen[,1]),numberOfGroups] = QualityBit
								stillFoundANewGroup = TRUE
							}
						}
					}
				}
			}
		}
	}
	if (numberOfGroups == 1) {
		matrixGruppen = cbind(matrixGruppen, c(0.1))
	}
	returnedMatrixGruppenAndnumberOfGroups = list(matrixGruppen=matrixGruppen,numberOfGroups=numberOfGroups)
	return(returnedMatrixGruppenAndnumberOfGroups)
}



######this counts the size of the groups in matrixGruppen
###for (summenzaehler in 1:length(matrixGruppen[1,])) { print(sum(matrixGruppen[1:(length(matrixGruppen[,1])-1),summenzaehler])) }

#save.image("thisfunction.model")



#rm(list=ls())


#print("ready-formingNotDisjointGroups")