

################ weight of graph 
weight<-function(g){

sum<-0
if(vcount(g)>1){
		######### Summing all nodes#########
		for(i in 1:ecount(g)){
		sum<-sum+E(g)[i]$weight
						}
					}else{ sum<-0}
return(sum)

}