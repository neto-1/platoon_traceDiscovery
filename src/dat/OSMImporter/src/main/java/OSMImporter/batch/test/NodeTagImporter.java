package OSMImporter.batch.test;

import OSMImporter.OnePassFullOSMImporter;

public class NodeTagImporter {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		OnePassFullOSMImporter importer = new OnePassFullOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		importer.importFromFile("e:\\data\\bundeslaender\\bremen-latest.osm");
	}

}
