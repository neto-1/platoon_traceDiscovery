spectralClustering <- function(incentivesR, groupCreatingParameters){
			numberOfGroups=0
			set.seed(1234)
			spTrue = TRUE
			############### initialization of graph 
			graph  <- graph.adjacency(incentivesR,weighted=TRUE)
			#droppingValue = groupCreatingParameters$droppingValue
			kGroups = groupCreatingParameters$kGroups
			LimitValue = groupCreatingParameters$LimitValue
			if (kGroups >= LimitValue) {
				print("Error, because you are using SP. Groups cant be more than vehicle")
				
			  kGroups = LimitValue/2
			}
			###############  Output List
			cliqueList<-list()
			############### spectral clustering algorithm
			temp= spectralM(incentivesR,kGroups)
			############### initialization of subgraphs
			tempInduced = inducedSubgraph(graph,temp,kGroups,spTrue)
			################### max clique for each subgraph
			for(x in tempInduced){cliqueList<-c(cliqueList,max_cliques(x))}
			###################
			WeightOfClique<-function(clique){
			  #clique<-Clique[[1]]
			  g<-induced.subgraph(graph,vids = clique$name)
			  #g<-induced.subgraph(graph,vids=Clique)
			  sum<-0
			  for(i in 1:ecount(g)){
			    sum<-sum+E(g)[i]$weight
			  }
			  return(sum)
			}
			###################
			numberOfGroups=length(cliqueList)
			################### To remove the alone cars, that can't platoon with others
			cliqueList=cliqueList[sapply(cliqueList,length)>1]
			############### sorting weight function
			sVector<-sapply(cliqueList,WeightOfClique)
			############### order vector
			sOrder<-order(sVector,decreasing=T)
			############### sorted list
			sortedList<-cliqueList[sOrder]
			################### Print the weight of the best group
			cat("Weight of the best group:", WeightOfClique(sortedList[[1]]),"Length of best group:",length(sortedList[[1]]),"\n")
			########### forming disjoint groups
			#sortedList=formingDisjointGroupsRm(sortedList,graph)
			################### cliqueList
			returnedValueGroupPool<-listToMatrix(cliqueList, graph)
			################### adding the weight vector to the end of the matrix 
			returnedValueGroupPool=rbind(returnedValueGroupPool,sVector[sOrder])
			################### number of rows
			lastRow<-nrow(returnedValueGroupPool)
			################### name weight last row
			rownames(returnedValueGroupPool)[lastRow]<-"Weights"
			###################
			returnedValueGroupPool = list(groupPool=returnedValueGroupPool,alphaCut=1, numberOfGroups=numberOfGroups)
			}