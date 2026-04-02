formingDisjointGroupsRm <- function(sortedList,g){
	########### initiate group list of all vehicles, maybe here we need some name to add 
	vertices=V(g)
	########### initiate empty list, which return the disjoint groups
    q=list()
	########### set counter to loop over the whole list
	i=1
	########### forming disjoint groups condition
	condition=any(sortedList[[i]]) %in% vertices
	########### loop breaks with the condition, that there are no more vehicles in the initiated list 
	while(i <length(sortedList) && length(vertices)>0){
	###########  test the condition
														if( condition== TRUE ){
																				###### test each member of the sorted list and add it to the new list 			
																				q[[i]]=sortedList[[i]][which(sortedList[[i]] %in% vertices)]
																				###### set it as temporal remove it if it saved
																				remove=vertices[which(vertices %in% sortedList[[i]])]
																				print(remove)
																				###### remove the visited vertices
																				vertices=setdiff(vertices, remove)
																				###### increasing the variable of the loop of the sorted list 
																				i=i+1
																				print(i)
																																
																																
																			 } else {
																							 
																						break
																							 
																					}
								
								}												
																			    ######  remove the empty members of the new list 
																				q=q[sapply(q,length)>0]
																				
																			    ######  retrive the new list 						
																				return(q)
														}