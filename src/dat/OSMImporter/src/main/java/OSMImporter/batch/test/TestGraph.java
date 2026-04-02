package OSMImporter.batch.test;

import OSMImporter.TwoPassOSMImporter;

public class TestGraph {

	public static void main(String[] args) {
		
		TwoPassOSMImporter importer = new TwoPassOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		importer.debug = true;
		importer.commit = true;
		importer.optimize = false;
		importer.removeArtefacts = false;
		
		importer.addFeature("highway", "motorway");

		importer.importFromFile("C:\\osm\\TestGraph.osm");
		//importer.importFromFile("C:\\osm\\berlin-latest.xml");
	}

}
