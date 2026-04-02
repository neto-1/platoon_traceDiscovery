package OSMImporter;

import static org.neo4j.driver.v1.Values.parameters;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.Transaction;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;
import OSMImporter.model.GraphNode;
import OSMImporter.util.StatusCounter;
import OSMImporter.util.StatusCounterRegistry;
import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public class TwoPassOSMImporter extends AbstractOSMImporter{

	private long start;
	private long finish;
	
	public boolean debug = false;
	public boolean commit = true;
	public boolean optimize = true;
	public boolean removeArtefacts = true;
	
	
	protected Map<String,List<String>> features = new HashMap<String,List<String>>();
	
	protected Neo4JConnection graphDB;
	protected Map<Long,GraphNode> graphNodes = new HashMap<Long,GraphNode>();
	
	protected StatusCounterRegistry counters = StatusCounterRegistry.instance;
	
	public TwoPassOSMImporter(String uri, String username, String password) {
		super(2);
		
		graphDB = Builder.instance.
				buildNeo4JConnection(uri, username, password, AccessMode.WRITE);
	}

	@Override
	public void createNode(OSMNode n) {
		
		counters.get("node").increment()._notify();
		
		if(getCurrentIteration() == 2){		
			if(graphNodes.containsKey(n.getId())){
				GraphNode e1 = graphNodes.get(n.getId());
				e1.putAllAttributes(n);		
			}
		}
	}

	@Override
	public void createWay(OSMWay w) {
		
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
		counters.get("relation").increment()._notify();
	}

	protected void optimize(){
		
		List<Long> remove = new LinkedList<Long>();

		boolean run = true;

		while (run) {

			System.out.println("Optimize...");

			run = false;
			
			for (GraphNode n : graphNodes.values()) {
	
				if (n.neighbours.size() == 2) {
		
					GraphNode left = n.neighbours.get(0);
					GraphNode right = n.neighbours.get(1);

					if(n.neighbours.getRelationship(left)
							.equals(n.neighbours.getRelationship(right)) == false){
						continue;
					}
					
					run = true;
					
					String relationship = n.neighbours.getRelationship(left);
					
					n.neighbours.remove(left);
					n.neighbours.remove(right);

					left.neighbours.add(right);
					left.neighbours.setRelationship(relationship, right);

					remove.add(n.getId());
				}
			}

			for (Long n_id : remove) {				
				graphNodes.remove(n_id);
			}
		}		
	}
	
	protected void removeArtefacts(){
		
		List<Long> remove = new LinkedList<Long>();
		
		for(GraphNode n : graphNodes.values()){
			
			if(n.neighbours.size() == 1){
								
				GraphNode neighbour = n.neighbours.get(0);
				
				if(neighbour.neighbours.size() == 1
						&& neighbour.neighbours.get(0).equals(n)){
					remove.add(n.getId());
					remove.add(neighbour.getId());
				}
				
			}
		}
		
		for(Long n_id : remove){
			graphNodes.remove(n_id);
		}
	}
	
	
	protected void commit(int tx_limit){
	
		graphDB.open();

		Transaction tx = graphDB.beginTransaction();

		System.out.println("Index Start");

		tx = graphDB.beginTransaction();

		tx.run("CREATE INDEX ON :Highway(osm_id)");
		
		System.out.println("Index Ende");
		
		tx.success();
		tx.close();
		
		graphDB.close();
	
		//-------------------------------Transfer Data-------------------------------
		
		graphDB.open();

		tx = graphDB.beginTransaction();
			
		int tx_size = 0;

		for (GraphNode n : graphNodes.values()) {

			//String labels = ":Highway";
			
//			for(String label : n.labels.getAll()){
//				labels+=":" + label; 
//			}
			
			tx.run("CREATE (node:Highway {osm_id: {n_id}, lon: {n_lon}, lat: {n_lat}})",
					parameters("n_id", n.getId(), "n_lon", n.getLon(), "n_lat", n.getLat()));

			tx_size++;

			if (tx_size == tx_limit) {
				System.out.println("Commit Node");
				tx.success();
				tx.close();
				tx_size = 0;
				tx = graphDB.beginTransaction();
			}
		}

		// Flush
		if (tx_size > 0) {
			tx.success();
			tx.close();
			tx_size = 0;
		}

		tx.success();
		tx.close();
		
		graphDB.close();
		
		//-------------------------------Transfer Data-------------------------------
		
		graphDB.open();
		
		tx = graphDB.beginTransaction();
		
		// Relationen
		for (GraphNode n : graphNodes.values()) {

			for (GraphNode neighbour : n.neighbours.getAll()) {
				

//				String cypher = "MATCH (n:Highway {id: "+n.getId()+"}), (m:Highway {id: "+neighbour.getId()+"}) MERGE (n)-[:neighbour]->(m)";
//				
//				System.out.println(cypher);
//				
//				tx.run(cypher);

				
//				tx.run("MATCH (n:Highway {id: {n_id}}), (neighbour:Highway {id: {neighbour_id}})"
//						+ "MERGE (n)-[:"+n.neighbours.getRelationship(neighbour)
//						+" {distance: "+n.neighbours.getDistance(neighbour)+"}]-(neighbour)",
//						parameters("n_id", n.getId(),"neighbour_id", neighbour.getId()));
						
//				query = new StringBuilder();
//				
//				query.append("MATCH (n:Highway {id: ");
//				query.append(n.getId());
//				query.append("}), (neighbour:Highway {id: ");
//				query.append(neighbour.getId());
//				query.append("}) MERGE (n)-[:");
//				query.append(n.neighbours.getRelationship(neighbour));
//				query.append(" {distance: ");
//				query.append(n.neighbours.getDistance(neighbour));
//				query.append("}]-(neighbour)");
//
//				tx.run(query.toString());				
				
//				String query = "MATCH (n:Highway {id: _n_id}), (neighbour:Highway {id: _neighbour_id}} MERGE (n)-[:_rel {distance: _d}]-(neighbour)"
//						.replaceFirst("(_n_id)", Long.toString(n.getId()))
//						.replaceFirst("(_id: neighbour_id)", Long.toString(neighbour.getId()))
//						.replaceFirst("(_rel)", n.neighbours.getRelationship(neighbour))
//						.replaceFirst("(_d)", Double.toString(n.neighbours.getDistance(neighbour)));
				
//				tx.run("MATCH (n:Highway {id: _n_id}), (neighbour:Highway {id: _neighbour_id}) MERGE (n)-[:_rel {distance: _d}]-(neighbour)"
//						.replaceFirst("(_n_id)", Long.toString(n.getId()))
//						.replaceFirst("(_neighbour_id)", Long.toString(neighbour.getId()))
//						.replaceFirst("(_rel)", n.neighbours.getRelationship(neighbour))
//						.replaceFirst("(_d)", Double.toString(n.neighbours.getDistance(neighbour))));
				
				tx.run("MATCH (n:Highway {osm_id: {n_id}}), (neighbour:Highway {osm_id: {neighbour_id}})"
						+ "MERGE (n)-[:"+n.neighbours.getRelationship(neighbour)+" {distance: {d}}]-(neighbour)",
						parameters("n_id", n.getId(),
								"d", n.neighbours.getDistance(neighbour),
								"neighbour_id", neighbour.getId()));

				tx_size++;

			}

			if (tx_size > tx_limit) {
				System.out.println("Commit Relation");
				tx.success();
				tx.close();
				tx_size = 0;
				tx = graphDB.beginTransaction();
			}
		}

		// Flush
		if (tx_size > 0) {
			System.out.println("Commit Relation");
		    tx.success();
			tx.close();
			tx_size = 0;
		}

		graphDB.close();
	}

	@Override
	public void init() {
		
		counters.add("node", new StatusCounter(200000,"Node"));
		counters.add("way", new StatusCounter(50000,"Way"));
		counters.add("relation", new StatusCounter(50000,"Relation"));
				
		start = System.currentTimeMillis() / 1000;	
	}
		
	public void debug(){
		
		for(GraphNode n : graphNodes.values()){
			
			System.out.print("ID " + n.getId() + " : ");
			
			for(String l : n.labels.getAll())
				System.out.print(l);
			
			System.out.println();
			
			for(GraphNode neighbour : n.neighbours.getAll()){
				System.out.println(n.neighbours.getRelationship(neighbour) 
						+ " NID: " + neighbour.getId() + " distance: " + n.neighbours.getDistance(neighbour));
			}
		}
		
	}
	
	@Override
	public void shutdown() {
		
		long beforeOpt = graphNodes.size();
		
		if(optimize){optimize();}
		if(removeArtefacts){removeArtefacts();}
		
		if(commit){commit(1000);}
		if(debug){debug();}
		
		finish = (System.currentTimeMillis() / 1000) - start;	

		System.out.println("Insgesamt bearbeitet in " + getCurrentIteration() +" Durchlaeufen");
		counters.print("node", "way", "relation");
				
		System.out.println("Nodes: " + graphNodes.size() + (" (Before Optimization: " + beforeOpt + ")"));		
		System.out.println("Duration: " + finish + " s");		
	}
	
	public void addFeature(String key, String value){
				
		if(features.containsKey(key) == false){
			features.put(key, new LinkedList<String>());
		}
		features.get(key).add(value);
	}
	
	public Map<String,List<String>> getAllFeature(){		
		return features;
	}
}
