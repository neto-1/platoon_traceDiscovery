package OSMImporter.test;

import static org.neo4j.driver.v1.Values.parameters;

import java.util.HashMap;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.Record;
import org.neo4j.driver.v1.StatementResult;
import org.neo4j.driver.v1.Transaction;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;

public class TestCypher2 {

	// key = first path node, value = shortlink candidate
	private Map<Long,Long> pathStartpoints = new HashMap<Long,Long>();
	// key = from, value = to
	private Map<Long,Long> shortLinks = new HashMap<Long,Long>();
	
	private Neo4JConnection graphDB;
	
	public TestCypher2(String uri, String username, String password) {
		graphDB = Builder.instance
				.buildNeo4JConnection(uri,username,password,AccessMode.WRITE);
	}

	private void addRankProperty(){
		
		graphDB.open();
		
		Transaction tx = graphDB.beginTransaction();
		
		System.out.println("Rank hinzufuegen");		
		tx.run("MATCH (a:Highway)-[r]-() WITH COUNT(r) AS rank, a set a.rank=rank");
		
		tx.success();
		tx.close();
		
		graphDB.close();
	}

	private void findPathCandidates(String relation){
		
		graphDB.open();
		
		Transaction tx = graphDB.beginTransaction();

		// Fall 1:
		
		StatementResult result = 
				tx.run("match (a)-[:"+relation+"*1]-(b) where a.rank > 2 and b.rank = 2 return a.osm_id, b.osm_id");

		int i = 0;
		
		while(result.hasNext()){
			
			long startpoint;
			long pathStartpoint;
			
			Record next = result.next();
			
			startpoint = next.get("a.osm_id").asLong();			
			pathStartpoint = next.get("b.osm_id").asLong();
			
			System.out.println(i + ": " + startpoint);
			i++;
			
			pathStartpoints.put(pathStartpoint, startpoint);
		}
		
		
		//Fall 2:
//		
//		result = 
//			tx.run("match (a)-[*1]-(b)-[:"+relation+"*1]-(c) where not (a)-[:"+relation+"*1]-(b) and b.rank = 2 return b.osm_id, c.osm_id");
//		
//		while(result.hasNext()){
//			
//			long startpoint;
//			long pathStartpoint;
//			
//			Record next = result.next();
//			
//			startpoint = next.get("b.osm_id").asLong();			
//			pathStartpoint = next.get("c.osm_id").asLong();
//			
//			//pathStartpoints.put(pathStartpoint, startpoint);
//			pathStartpoints.put(startpoint, startpoint);
//		}
//		
//		
//		//Fall 3:
//		
//		result = 
//				tx.run("match (a)-[:"+relation+"*1]-(b)-[:"+relation+"*1]-(c) where b.rank = 2 and c.rank = 1 return b.osm_id, c.osm_id");
//			
//			while(result.hasNext()){
//				
//				long startpoint;
//				long pathStartpoint;
//				
//				Record next = result.next();
//				
//				startpoint = next.get("c.osm_id").asLong();			
//				pathStartpoint = next.get("b.osm_id").asLong();
//				
//				pathStartpoints.put(pathStartpoint, startpoint);
//			}
		
		
		tx.success();
		tx.close();
		
		graphDB.close();
	}
	
	private void addShortLink(String relation){
		
		int i = 0;
		
		graphDB.open();
		
		Transaction tx = graphDB.beginTransaction();

		for(Map.Entry<Long, Long> candidate : pathStartpoints.entrySet()){
			
			long startpoint = candidate.getValue();
			
			StatementResult result2 = tx.run("match (a {osm_id: {s_osm_id}})-[:"+relation+"*]-(c) where c.rank = 2 with last(collect(c)) as e return e.osm_id",
					parameters("s_osm_id",candidate.getKey()));	
			
			long pathEndpoint = result2.next().get("e.osm_id").asLong();
			//System.out.println(pathEndpoint + " contains " + pathStartpoints.containsKey(pathEndpoint));
			long endpoint = pathStartpoints.get(pathEndpoint);
			
			System.out.println(relation + " " + i + ": " +startpoint + "---" + endpoint);
			i++;
//			tx.run("match (a:Highway {osm_id: {s_osm_id}}), (b:Highway {osm_id: {e_osm_id}}) merge (a)-[:short_"+relation+"]-(b)",
//					parameters("s_osm_id",startpoint, "e_osm_id", endpoint));
			
		}
				
		tx.success();
		tx.close();
		
		graphDB.close();
	}
	
	public void createShortlink(String... relations){
	
		 //addRankProperty();
		
		for(String relation : relations){
			findPathCandidates(relation);
//			addShortLink(relation);

			pathStartpoints.clear();
		}		
	}
	
	public static void main(String[] args) {
		
		TestCypher2 test = new TestCypher2("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		test.createShortlink("motorway");	
		
//		test.createShortlink("motorway","motorway_link",
//				"trunk","trunk_link",
//				"primary","primary_link",
//				"secondary","secondary_link",
//				"tertiary","tertiary_link");	
	}

}
