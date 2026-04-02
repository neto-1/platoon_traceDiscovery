spectralClustering<-function(Matrix,randomgraph,maxNumberOfCommunities=2,type="sp"){
	temp<-c()
	inducedGraphList<-list()
	switch(type,
		sp={temp <- multiWay(Matrix, maxComm=maxNumberOfCommunities)},
		so={temp <- spectralOptimization(Matrix, refine = TRUE)},
		s1={temp <- spectral1(Matrix, numRandom=0, maxComm=(length(M[1,])-1))},
		s2={temp <- spectral2(Matrix, numRandom=0, maxComm=(length(M[1,])-1))})

	for(i in seq(1,maxNumberOfCommunities,1)){
		Edges <- E(randomgraph)[which(temp$'community structure'==i)]
		inducedGraph <- induced.subgraph(randomgraph,Edges)
		#dev.new()
		#plot(inducedGraph,edge.label=E(inducedGraph))
		inducedGraphList[[paste0("inducedGraph", i)]] <- inducedGraph
	}
	return(inducedGraphList)
}








