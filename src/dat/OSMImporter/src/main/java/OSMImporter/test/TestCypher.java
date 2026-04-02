package OSMImporter.test;

import static org.neo4j.driver.v1.Values.parameters;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.Record;
import org.neo4j.driver.v1.StatementResult;
import org.neo4j.driver.v1.Transaction;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;

public class TestCypher {

	public static void main(String[] args) {

		Neo4JConnection graphDB = Builder
				.instance.buildNeo4JConnection("bolt://127.0.0.1:7687", "neo4j", "12345678",AccessMode.WRITE);
		
		
		graphDB.open();
				
		Transaction tx = graphDB.beginTransaction();
		
//		System.out.println("Rank hinzufuegen");
//		
//		tx.run("MATCH (a:Highway)-[r]-() WITH COUNT(r) AS rank, a set a.rank=rank");
		
		System.out.println("Short Links erstellen");
		StatementResult result = 
				tx.run("match (a)-[:motorway*1]-(b) where a.rank > 2 and b.rank = 2 return a.osm_id, b.osm_id, a.rank, b.rank");

		
		while(result.hasNext()){
			
			long startpoint;
			long endpoint;
			
			long pathStartpoint;
			long pathEndpoint;
			
			Record next = result.next();
			
			startpoint = next.get("a.osm_id").asLong();			
			pathStartpoint = next.get("b.osm_id").asLong();
			
//			System.out.println(startpoint +  "|" + next.get("a.rank").asInt()	+ " -> " + pathStartpoint + "|" + next.get("b.rank").asInt());
			
				
			StatementResult result2 = tx.run("match (a {osm_id: {s_osm_id}})-[:motorway*]-(c) where c.rank = 2 with last(collect(c)) as e return e.osm_id",
					parameters("s_osm_id",pathStartpoint));
					


				pathEndpoint = result2.next().get("e.osm_id").asLong();
				
				StatementResult result3 = tx.run("match (a {osm_id: {e_osm_id}})-[:motorway*1]-(b) where b.rank > 2 and a.rank = 2 return b.osm_id",
						parameters("e_osm_id",pathEndpoint));
				
				endpoint = result3.next().get("b.osm_id").asLong();
				
				tx.run("match (a:Highway {osm_id: {s_osm_id}}), (b:Highway {osm_id: {e_osm_id}}) merge (a)-[:short_motorway]-(b)",
						parameters("s_osm_id",startpoint, "e_osm_id", endpoint));
				
				System.out.println(startpoint + "---" + endpoint);
			
		}
//		
//		tx.run("match (a)-[:motorway*1]-(b) where b.rank > 2 and a.rank = 1 "
//				+ "merge (b)-[:short_motorway]-(a)");
		
		tx.success();
		tx.close();
		
		graphDB.close();
	}

}
