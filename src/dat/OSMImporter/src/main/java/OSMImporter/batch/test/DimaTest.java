package OSMImporter.batch.test;

import OSMImporter.TwoPassSimpleOSMImporter;

public class DimaTest {

	public static void main(String[] args) {

		TwoPassSimpleOSMImporter importer = new TwoPassSimpleOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		//importer.optimize = false;
		//importer.removeArtefacts = false;
		
		importer.addFeature("highway", "motorway");
		importer.addFeature("highway", "motorway_link");

//		importer.addFeature("highway", "trunk");
//		importer.addFeature("highway", "trunk_link");
//		
//		importer.addFeature("highway", "primary");
//		importer.addFeature("highway", "primary_link");
//		
//		importer.addFeature("highway", "secondary");
//		importer.addFeature("highway", "secondary_link");
//		
//		importer.addFeature("highway", "tertiary");
//		importer.addFeature("highway", "tertiary_link");
		
		
	
		
		//importer.importFromFile("G:\\data\\germany-latest.osm","G:\\data\\poland-latest.osm");
		importer.importFromFile("G:\\data\\us-west-latest.osm","G:\\data\\us-midwest-latest.osm");
		
	}

}
