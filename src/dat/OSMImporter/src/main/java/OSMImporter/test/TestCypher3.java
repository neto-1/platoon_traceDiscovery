package OSMImporter.test;

import static org.neo4j.driver.v1.Values.parameters;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.Record;
import org.neo4j.driver.v1.StatementResult;
import org.neo4j.driver.v1.Transaction;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;
import OSMImporter.model.GraphNode;

public class TestCypher3 {
	
	private Neo4JConnection graphDB;
	
	protected Map<Long,GraphNode> graphNodes = new HashMap<Long,GraphNode>();
	private String shortRelation;
	
	public TestCypher3(String uri, String username, String password) {
		graphDB = Builder.instance
				.buildNeo4JConnection(uri,username,password,AccessMode.WRITE);
	}

	private void loadGraph(String relation){
			
		graphDB.open();
		
		Transaction tx = graphDB.beginTransaction();
				
		System.out.println("Graph laden");		
		
		StatementResult result = 
				tx.run("match (n)-[:"+relation+"]-(m) return n.osm_id,m.osm_id");
			
		while(result.hasNext()){
						
			Record next = result.next();
		
			long n_id = next.get("n.osm_id").asLong();
			long m_id = next.get("m.osm_id").asLong();
			
			GraphNode n =  graphNodes.get(n_id);
			GraphNode m =  graphNodes.get(m_id);
			
			if(n == null){
				n = new GraphNode(n_id);
				graphNodes.put(n_id, n);
			}
			
			if(m == null){
				m = new GraphNode(m_id);
				graphNodes.put(m_id, m);
			}
			
			n.neighbours.add(m);
			n.neighbours.setRelationship(shortRelation, m);
		}
		
		tx.success();
		tx.close();
				
		graphDB.close();						
	}
	
	private void optimize(){
		
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
	
	private void commit(int tx_limit){
		
		graphDB.open();
		
		Transaction tx = graphDB.beginTransaction();
		
		int tx_size = 0;
		
		String query = "match (a:Highway {osm_id: {s_osm_id}}), (b:Highway {osm_id: {e_osm_id}}) merge (a)-[:"+shortRelation+"]-(b)";
		
		// Relationen
		for (GraphNode n : graphNodes.values()) {

			for (GraphNode neighbour : n.neighbours.getAll()) {
		
				tx.run(query, parameters("s_osm_id",n.getId(), "e_osm_id", neighbour.getId()));

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

		tx.success();
		tx.close();
				
		graphDB.close();		
		
	}
	
	public void createShortlink(String... relations){
		
		long start = (System.currentTimeMillis() / 1000);
		
		for(String relation : relations){
			
			shortRelation = "short_" + relation;
			
			loadGraph(relation);
			optimize();
			commit(1000);
		}
		
		long finish = (System.currentTimeMillis() / 1000) - start;
		
		System.out.println("Duration: " + finish + " s");
		
	}
	
	public static void main(String[] args) {
		
		TestCypher3 test = new TestCypher3("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		//test.createShortlink("motorway");	
		
		test.createShortlink("motorway","motorway_link",
				"trunk","trunk_link",
				"primary","primary_link",
				"secondary","secondary_link",
				"tertiary","tertiary_link");	
	}	
	
}
