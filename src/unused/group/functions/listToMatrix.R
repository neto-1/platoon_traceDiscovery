listToMatrix<-function(cliqueList, g){
	#print("copy right at TU-Clausthal")
	######## for aribatry data without name, initiate name as its index  
	if(is.null(V(g)$name)){
									V(g)$name = c(1:length(V(g)))
							}else{
									V(g)$name= V(g)$name
									}
	
	######## intiate blank matrix
	mList<-matrix(0,nrow=vcount(g),ncol=length(cliqueList),dimnames=list(V(g)$name,1:length(cliqueList)))
	######## set variable to the first element in the matrix
	y<-1
	######## intiate iterator for the cliques 
	iterator <- ihasNext(cliqueList)
	######## iterate on each variable 
	while (hasNext(iterator)){
		
		ne <- nextElem(iterator)
	######## intiate iterator for each clique
		it<- ihasNext(ne)
	while(hasNext(it)){
	######## test each element in the clique
			e <- nextElem(it)	
	######## x variable for the rows of the matrix
	for(x in 1:nrow(mList)){

	######## y variable for the coloumn of the matrix
			mList[which(e$name == rownames(mList)),y]=1
			break
					}
				}
	####### moving for next clique on 
				y<-y+1
				}
	####### return the matrix
	return(mList)
}
