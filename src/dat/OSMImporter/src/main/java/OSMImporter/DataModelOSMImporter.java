package OSMImporter;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;
import OSMImporter.model.GraphNode;
import OSMImporter.util.StatusCounter;
import OSMImporter.util.StatusCounterRegistry;
import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public class DataModelOSMImporter extends AbstractOSMImporter {

	private long start;
	private long finish;
	
	protected Map<String,List<String>> features = new HashMap<String,List<String>>();
	protected Map<Long,GraphNode> graphNodes = new HashMap<Long,GraphNode>();
	
	protected Neo4JConnection graphDB;
	protected StatusCounterRegistry counters = StatusCounterRegistry.instance;
	
	public DataModelOSMImporter(String uri, String username, String password) {
		super(2);
		
		graphDB = Builder.instance.
				buildNeo4JConnection(uri, username, password, AccessMode.WRITE);
	}	
	
	@Override
	public void createNode(OSMNode n) {
		// TODO Auto-generated method stub
	}

	@Override
	public void createWay(OSMWay w) {
		
		//w.nd_ref
		//w.tag
		//w.getId()
		
		//features.get(key)<--List<--Value
		
		
		
		
		//-------------------------------------------

		counters.get("way").increment()._notify();
		
		if(getCurrentIteration() == 1){			
	
			for(Map.Entry<String, List<String>> feature : features.entrySet()){
				
				if(w.tag.containsKey(feature.getKey())){
				
					String value = w.tag.get(feature.getKey());
					
					if(feature.getValue().contains(value)){
					
						for(int i = 0; i + 1 < w.nd_ref.size(); i++){
							
							GraphNode e1 = null;
							GraphNode e2 = null;
							
							if(graphNodes.containsKey(w.nd_ref.get(i))){
								e1 = graphNodes.get(w.nd_ref.get(i));
								e1.labels.add(feature.getKey());
							}else{
								e1 = new GraphNode(w.nd_ref.get(i),feature.getKey());
								graphNodes.put(e1.getId(), e1);
							}
							
							if(graphNodes.containsKey(w.nd_ref.get(i+1))){
								e2 = graphNodes.get(w.nd_ref.get(i+1));
								e2.labels.add(feature.getKey());
							}else{
								e2 = new GraphNode(w.nd_ref.get(i+1),feature.getKey());
								graphNodes.put(e2.getId(), e2);
							}	
												
							e1.neighbours.add(e2);
							e1.neighbours.setRelationship(value, e2);
						}						
					}
				}
			}			
		}	

	}

	@Override
	public void createRelation(OSMRelation r) {
		// TODO Auto-generated method stub

	}

	@Override
	public void init() {
		
		counters.add("node", new StatusCounter(200000,"Node"));
		counters.add("way", new StatusCounter(50000,"Way"));
		counters.add("relation", new StatusCounter(50000,"Relation"));
				
		start = System.currentTimeMillis() / 1000;	
	}

	@Override
	public void shutdown() {
		
		finish = (System.currentTimeMillis() / 1000) - start;	

		System.out.println("Insgesamt bearbeitet in " + getCurrentIteration() +" Durchlaeufen");
		counters.print("node", "way", "relation");
				
		//System.out.println("Nodes: " + graphNodes.size() + (" (Before Optimization: " + beforeOpt + ")"));		
		//System.out.println("Duration: " + finish + " s");		
	}

}
