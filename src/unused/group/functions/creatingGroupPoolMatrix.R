


creatingGroupPoolMatrix <- function(incentivesR, groupCreatingParameters) {
	spTrue = FALSE

	identifyGroupsBy = groupCreatingParameters$identifyGroupsBy
	switch(identifyGroupsBy,

		sp={
	
			# this is spectral clustering for communities
			returnedValueGroupPool = spectralClustering(incentivesR,groupCreatingParameters)
			return(returnedValueGroupPool)
		
		},
		wtp={
		
			# this is walk trap for graph partitioning 
			returnedValueGroupPool = walktrap(incentivesR,groupCreatingParameters)
			#print(returnedValueGroupPool)
			return(returnedValueGroupPool)
			
		
		},
		cl={
		  
		# this is bronkerbosch degeneracy	
			returnedValueGroupPool = bronKerbosch(incentivesR,groupCreatingParameters)
			return(returnedValueGroupPool)
		},
		spp={
		# this is the spectral extra algorithm of kernlab. it creates groups with more iterations	
			returnedValueGroupPool = spectralExtraGroupCreating(incentivesR,groupCreatingParameters)
			return(returnedValueGroupPool)
		},
		
		# this is the greedy approach to create groups. it creates groups out of the best values in incentivesR and tries to create as many groups, as in kGroups assigned
		greedy={
			returnedValueGroupPool = greedyGroupCreating(incentivesR,groupCreatingParameters)
			return(returnedValueGroupPool)
		}
	)
}


#print("ready-creatingGroupPoolMatrix")