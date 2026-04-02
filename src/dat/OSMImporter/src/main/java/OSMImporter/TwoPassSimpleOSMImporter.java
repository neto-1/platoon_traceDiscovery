package OSMImporter;

import static org.neo4j.driver.v1.Values.parameters;

import org.neo4j.driver.v1.Transaction;

import OSMImporter.model.GraphNode;

public class TwoPassSimpleOSMImporter extends TwoPassOSMImporter {

	public TwoPassSimpleOSMImporter(String uri, String username, String password) {
		super(uri, username, password);
	}

	@Override
	protected void commit(int tx_limit) {

		graphDB.open();

		Transaction tx = graphDB.beginTransaction();

		int tx_size = 0;

		for (GraphNode n : graphNodes.values()) {
			
			tx.run("CREATE (node:loc {id: {n_id}, lon: {n_lon}, lat: {n_lat}})",
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

		// Index

		System.out.println("Index Start");

		tx = graphDB.beginTransaction();

		tx.run("CREATE INDEX ON :loc(id)");

		tx.success();
		tx.close();

		System.out.println("Index Ende");
		
		tx = graphDB.beginTransaction();
		
		// Relationen
		for (GraphNode n : graphNodes.values()) {

			for (GraphNode neighbour : n.neighbours.getAll()) {
				
				tx.run("MATCH (n:loc {id: {n_id}}), (neighbour:loc {id: {neighbour_id}})"
						+ "MERGE (n)-[:NEIGHBOUR {distance: {d}}]-(neighbour)",
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
			tx.success();
			tx.close();
			tx_size = 0;
		}

		graphDB.close();
	}

	
}
