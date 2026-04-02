package OSMImporterV2.batch.run;

import OSMImporterV2.batch.BatchTemplate;
import OSMImporterV2.filter.model.Constants;
import OSMImporterV2.filter.model.PrimaryKey;

public class Test2 extends BatchTemplate{

	@Override
	public void setup() {
		
		//OsmFile
		this.setOsmFile("G:/data/bl/niedersachsen-latest.osm");
		
		//this.autobahn();
		//this.primary();
		this.secondary();
		//this.tertiary();
		
		
		//Grenzen
		this.getConfiguration().setBoundaryAdmin_Level(6);
		
		//Database
		this.setDatabase("bolt://127.0.0.1:7687", "neo4j", "12345678");
	}
	
	private void autobahn(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link");

		
		this.getConfiguration().setRule(highway);
	}

	private void primary(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link");
		
		this.getConfiguration().setRule(highway);
	}
	
	private void secondary(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link");
		
		this.getConfiguration().setRule(highway);
	}
	
	private void tertiary(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link",
				"tertiary", "tertiary_link");
		
		this.getConfiguration().setRule(highway);
	}

	public static void main(String arg[]){
		new Test2().run();
	}

}
