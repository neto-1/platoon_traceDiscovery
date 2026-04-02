inducedSubgraph<-function(randomgraph,resultOfSpectral,k, spTrue){

	inducedGraphList<-list()

	 for(i in seq(1,k,1)){
		if (spTrue == TRUE) {
			################ spectrasl clustering
			Edges <- E(randomgraph)[which(resultOfSpectral$index==i)]		
		} else {
			################ partitioniong 
			Edges <- E(randomgraph)[which(membership(resultOfSpectral)==i)]
		}
		
		 
		inducedGraph <- induced.subgraph(randomgraph,Edges)

		inducedGraphList[[i]] <- inducedGraph
	}
	
	
	
	
	return(inducedGraphList)
 
}