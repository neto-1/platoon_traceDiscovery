package OSMImporter.batch.test;

import OSMImporter.TwoPassShortLinkOSMImporter;

public class TestShortLinkImporter {

	public static void main(String[] args) {

		TwoPassShortLinkOSMImporter importer = new TwoPassShortLinkOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		importer.debug = false;
		importer.commit = true;
		
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
		
//		importer.addFeature("boundary", "administrative");
		
		importer.importFromFile("c:\\osm\\berlin-latest.xml");

	}

}
