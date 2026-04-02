
spectralM<-function(M,kGroups=6){
	set.seed(1234)			
	droppingValue=round(0.75*(kGroups))
	####### diagonal matrix
	G = diag(rowSums(M))
	######## Laplacian
	Laplacian = G-M
	######## eigenVectors
	EigenLaplacian = eigen(Laplacian)
	######## Values
	eValues = EigenLaplacian$values
	######## dropping values
	dropedVector = order(eValues)[1:droppingValue+1]
	######## first vector
	v = EigenLaplacian$vectors[,dropedVector]
	######## K-means
	kmeanResult = kmeans(v, kGroups)$cluster
	result = list(index=kmeanResult,vectors=v, eValues=eValues)
	########
	return(result)


}