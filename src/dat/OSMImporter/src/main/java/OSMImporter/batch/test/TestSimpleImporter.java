package OSMImporter.batch.test;


import OSMImporter.TwoPassSimpleOSMImporter;

public class TestSimpleImporter {

	public static void main(String[] args) {
		TwoPassSimpleOSMImporter importer = new TwoPassSimpleOSMImporter("bolt://127.0.0.1:7687", "neo4j", "12345678");
		
		//importer.debug = true;
		//importer.commit = false;
		importer.optimize = false;
		
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
		
		
		importer.addFeature("highway", "residential");
		importer.addFeature("highway", "living_street");
		//importer.addFeature("highway", "unclassified");
		
		
		
		//importer.importFromFile("E:\\data\\bundeslaender\\saarland-latest.osm");
		//importer.importFromFile("E:\\data\\bundeslaender\\bayern-latest.osm");
		
		//importer.importFromFile("E:\\data\\bundeslaender\\niedersachsen-latest.osm",
		//		"E:\\data\\bundeslaender\\hessen-latest.osm");
		
		//importer.importFromFile("E:\\data\\bundeslaender\\baden-wuerttemberg-latest.osm",
		//		"E:\\data\\bundeslaender\\bayern-latest.osm");
		
		//importer.importFromFile("E:\\data\\bundeslaender\\niedersachsen-latest.osm");
		//importer.importFromFile("E:\\data\\bundeslaender\\thueringen-latest.osm");
		//importer.importFromFile("E:\\data\\bundeslaender\\nordrhein-westfalen-latest.osm");
		
		//importer.importFromFile("E:\\data\\laender\\germany-latest.osm");
		
		//importer.importFromFile("E:\\data\\laender\\france-latest.osm");
		
		importer.importFromFile("E:\\data\\north_america\\new-york-latest.osm");
		
		
//		luxembourg-latest
//		netherlands-latest
//		belgium-latest
		
		//Deutschalnd
		//Frankreich
		//Belgien
		//Luxemburg
		//Niederlande
		
		
		
	}

}
