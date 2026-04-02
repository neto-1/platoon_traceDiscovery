package OSMImporterV2.batch.run;

import OSMImporterV2.batch.BatchTemplate;
import OSMImporterV2.filter.model.Constants;
import OSMImporterV2.filter.model.PrimaryKey;

public class Bremen extends BatchTemplate{

	@Override
	public void setup() {
		
		//OsmFile
		//this.setOsmFile("G:/data/bremen-latest.osm");
		//this.setOsmFile("G:/data/bl/niedersachsen-latest.osm");
		//this.setOsmFile("G:/data/bl/berlin-latest.osm");
		this.setOsmFile("/Users/dmitry/Documents/wd/data/databases.taxi/OSM/NewYork.osm");
		//PrimaryKeys	
//		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, 
//				"motorway", "motorway_link",
//				"primary", "primary_link",
//				"secondary", "secondary_link",
//				"tertiary", "tertiary_link");
//		
//			factory.createSecondaryKey(highway, "maxspeed", Constants.PROPERTY);
		
		
/*		importer.addFeature("highway", "motorway");
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
		*/
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link",
				"tertiary", "tertiary_link", 
				"residential", "living_street");
			//factory.createSecondaryKey(highway, "lanes", Constants.PROPERTY);	
			//factory.createSecondaryKey(highway, "maxspeed", Constants.RESTRICTION);	
			
		//PrimaryKey ampel = factory.createPrimaryKey("highway", Constants.NODE, "traffic_signals");
		
		
//		PrimaryKey primary = factory.createPrimaryKey("highway", Constants.LABEL, "primary");
//			factory.createSecondaryKey(primary, "bridge", Constants.PROPERTY);	
//			factory.createSecondaryKey(primary, "lanes", Constants.PROPERTY);
//			factory.createSecondaryKey(primary, "name", Constants.PROPERTY);
//			factory.createSecondaryKey(primary, "maxspeed", Constants.RESTRICTION);	
//			
		
		
		
		
		this.getConfiguration().setRule(highway);
	//	this.getConfiguration().setRule(ampel);
		
		//Grenzen
		this.getConfiguration().setBoundaryAdmin_Level(6);
		
		//Database
		this.setDatabase("bolt://127.0.0.1:7687", "neo4j", "12345678");
	}

	public static void main(String arg[]){
		new Bremen().run();
	}
	
}
