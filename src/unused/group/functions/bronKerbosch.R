 bronKerbosch <- function(incentivesR, groupCreatingParameters){ 
  ## Parameter
			kGroups = groupCreatingParameters$kGroups
			numberOfGroups=0
			set.seed(1234)
			cliqueMin = groupCreatingParameters$cliqueMin
			############### initialization of graph 
			graph  <- graph.adjacency(incentivesR,weighted=TRUE)
			############### weight of clique
			WeightOfClique<-function(Clique){
			#clique1<-Clique[[1]]
			g<-induced.subgraph(graph,vids=Clique)
			sum<-0
			for(i in 1:ecount(g)){
				sum<-sum+E(g)[i]$weight
				}
			return(sum)
			}
			###############  Output List
			cliqueList<-list()
			############### max clique
			cliqueList<-max_cliques(graph)
			numberOfGroups=length(cliqueList)
			################### To remove the alone cars, that can't platoon with others
			cliqueList=cliqueList[sapply(cliqueList,length)>1]
			############### sorting vector
			sVector<-sapply(cliqueList,WeightOfClique)
			############### order vector
			sOrder<-order(sVector,decreasing=T)
			############### sorted list
			sortedList<-cliqueList[sOrder]
			################### Print the weight of the best group
			cat("Weight of the best group:", WeightOfClique(sortedList[[1]]),"Length of best group:",length(sortedList[[1]]),"\n")
			############### return number of groups, if the number of groups is bigger than the list, the algorithm would return the produced number of groups
			# check if there are more groups than we needed
			if (kGroups > length(sortedList)){
			#return the produced list
			sortedList=sortedList
			}else{
			#just give the required number (kgroups) 
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