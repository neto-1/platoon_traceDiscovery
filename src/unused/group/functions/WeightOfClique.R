weightOfClique<-function(Clique,graph){
################## choosing the first list memeber
 clique1<-Clique[[1]]
################# forming induced subgraph for the clique with relation between its name and the whole graph
			g<-induced.subgraph(graph,vids = Clique$name)
			#g<-induced.subgraph(graph,vids=Clique)
################## sum 			
			sum<-0
################## adding the edges weight			
			for(i in 1:ecount(g)){
				sum<-sum+E(g)[i]$weight
				}
			return(sum)
  
}
############