
getMax <- function(MAT) {
	
	# get the row and the column of the maximal entry in matrix MAT
	if (length(which(MAT == max(MAT), arr.ind = TRUE))>2) {
		i = which(MAT == max(MAT), arr.ind = TRUE)[1,2]
		j = which(MAT == max(MAT), arr.ind = TRUE)[1,1]
	} else {
		i = which(MAT == max(MAT), arr.ind = TRUE)[2]
		j = which(MAT == max(MAT), arr.ind = TRUE)[1]
	}

	#print(j)
	
	# ### old method:
	# # first get the entry (in total, so entry in 5x5 matrix on row 2 and column 2 would be 7)
	# NumberOfEntry = which(MAT == max(MAT))

	# #get the row of the highest value
	# j = NumberOfEntry %% length(MAT[,1]) #gibt die j-te zeile aus
	# #get the column of the highest value
	# i = ceiling(NumberOfEntry / length(MAT[,1])) #gibt die i-te zeile aus
	
	#giveback <- c(i,j)

	return(c(i[1],j[1]))	
}


#print("ready-getMax")

#rm(list=ls())
