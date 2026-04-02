walktrap <- function(incentivesR, groupCreatingParameters){
	## Parameter
			kGroups = groupCreatingParameters$kGroups
			numberOfGroups=0
			set.seed(1234)
			############### initialization of graph 
			graph  <- graph.adjacency(incentivesR,weighted=TRUE)
			###############  Output List
			cliqueList<-list()
			############## sp
			spTrue=FALSE
			############### walk trap algorithm
			temp= cluster_walktrap(graph)
			############### kgroup
			clusterLength = length(temp)
			############### initialization of subgraphs
			tempInduced = inducedSubgraph(graph,temp,clusterLength,spTrue)
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
			################### return number of groups
			if (kGroups > length(sortedList)){
			sortedList=sortedList
			}else{
			sortedList=sortedList[c(1:kGroups)]
			}
		  ########### forming disjoint groups
			#sortedList=formingDisjointGroupsRm(sortedList,graph)
			################### cliqueList
			returnedValueGroupPool<-listToMatrix(sortedList, graph)
			################### adding the weight vector to the end of the matrix 
			returnedValueGroupPool=rbind(returnedValueGroupPool,sVector[sOrder])
			################### number of rows
			lastRow<-nrow(returnedValueGroupPool)
			################### name weight last row
			rownames(returnedValueGroupPool)[lastRow]<-"Weights"
			###################
			returnedValueGroupPool = list(groupPool=returnedValueGroupPool,alphaCut=1, numberOfGroups=numberOfGroups)
			}