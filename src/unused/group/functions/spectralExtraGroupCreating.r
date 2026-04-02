spectralExtraGroupCreating <- function(incentivesR, groupCreatingParameters){

			
            ## setting seeds to retrieve the same algorithm results
							set.seed(1234)
			## initializate all parameters
			## number of group, which should be created (minimum)
			
							kGroups = groupCreatingParameters$kGroups
			## initialization of graph 
			
							graph  <- graph.adjacency(incentivesR,weighted=TRUE)
			##  Output List
			
							cliqueList<-list()

			## spectral clustering algorithm
			
							temp= specc(incentivesR,kGroups)
			## retrive  the clusters index
			
							x=temp@.Data
			
			## initialization of subgraphs
							inducedGraphList<-list()
							for(i in seq(1,kGroups,1)){
						
								Edges <- E(graph)[which(x==i)]		
						
						 
								inducedGraph <- induced.subgraph(graph,Edges)

								inducedGraphList[[i]] <- inducedGraph
							}	
						
							tempInduced =inducedGraphList
			
			
			## output
			for(x in tempInduced){cliqueList<-c(cliqueList,max_cliques(x))}
			
			
			## cliqueList
			
			returnedValueGroupPool=listToMatrix(cliqueList, graph)
			
			##
			
			returnedValueGroupPool=list(groupPool=returnedValueGroupPool,alphaCut=1)

            return(returnedValueGroupPool)

}
