package OSMImporter.batch.bundeslaender;

import OSMImporter.TwoPassOSMImporter;

public class MecklenburgVorpommern {

	public static void main(String[] args) {

		TwoPassOSMImporter importer = new TwoPassOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		//importer.debug = true;
		//importer.commit = false;
		
		importer.addFeature("highway", "motorway");
		importer.addFeature("highway", "motorway_link");

		importer.addFeature("highway", "trunk");
		importer.addFeature("highway", "trunk_link");
		
		importer.addFeature("highway", "primary");
		importer.addFeature("highway", "primary_link");
		
		importer.addFeature("highway", "secondary");
		importer.addFeature("highway", "secondary_link");
		
		importer.addFeature("highway", "tertiary");
		importer.addFeature("highway", "tertiary_link");
				
		importer.importFromFile("E:\\data\\bundeslaender\\mecklenburg-vorpommern-latest.osm");

	}

}
