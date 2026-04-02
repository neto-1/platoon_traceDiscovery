################ function for testing weights of cliques to make comparsion for the groups input set of subgraphs output sorted weight
tempWeight<-function(tempInduced)
{
  ########### set weight variable to 0
  weig<-0
  ########### set iterator for each sub graph
  it <- ihasNext(iter(tempInduced)) 
  while (hasNext(it))
  {
    
    g<-nextElem(it)
    ############  calculate maximum clique
    cliqeList<- max_cliques(g)
    ############				
    for(i in cliqeList)
    {
      ############ set each subgraph as original to its cliques				
      x<-induced.subgraph(g,vids=i)
      #print(weight(x))
      weig<-c(weig,weight(x))
    }
    
    
    
    
  }
  ############ return sorted set of weights
  return(sort(weig,decreasing=TRUE))
}

#sort(y,decreasing=TRUE)