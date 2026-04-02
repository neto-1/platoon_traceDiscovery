package OSMImporterV2.batch.run;

import OSMImporterV2.batch.BatchTemplate;
import OSMImporterV2.filter.model.Constants;
import OSMImporterV2.filter.model.PrimaryKey;

public class Test1 extends BatchTemplate{

	@Override
	public void setup() {
		
		//OsmFile
		this.setOsmFile("G:/data/bl/berlin-latest.osm");
		
		//this.ohne();
		this.mit5Attr();
		//this.mit10Attr();
		
		
		//Grenzen
		this.getConfiguration().setBoundaryAdmin_Level(6);
		
		//Database
		this.setDatabase("bolt://127.0.0.1:7687", "neo4j", "12345678");
	}
	
	private void ohne(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link",
				"tertiary", "tertiary_link");
		
		this.getConfiguration().setRule(highway);
	}
	
	private void mit5Attr(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link",
				"tertiary", "tertiary_link");
		
			factory.createSecondaryKey(highway, "tunnel", Constants.PROPERTY);	
			factory.createSecondaryKey(highway, "bridge", Constants.PROPERTY);	
			factory.createSecondaryKey(highway, "lanes", Constants.PROPERTY);
			factory.createSecondaryKey(highway, "name", Constants.PROPERTY);
			factory.createSecondaryKey(highway, "maxspeed", Constants.RESTRICTION);	
		
		this.getConfiguration().setRule(highway);
	}
	
	
	private void mit10Attr(){
		
		PrimaryKey highway = factory.createPrimaryKey("highway", Constants.LABEL, "motorway", "motorway_link",//);
				"primary", "primary_link",
				"secondary", "secondary_link",
				"tertiary", "tertiary_link");
		
			factory.createSecondaryKey(highway, "tunnel", Constants.PROPERTY);	
			factory.createSecondaryKey(highway, "bridge", Constants.PROPERTY);	
			factory.createSecondaryKey(highway, "lanes", Constants.PROPERTY);
			factory.createSecondaryKey(highway, "name", Constants.PROPERTY);
			factory.createSecondaryKey(highway, "crossinge", Constants.PROPERTY);
			factory.createSecondaryKey(highway, "surface", Constants.PROPERTY);
			
			factory.createSecondaryKey(highway, "maxspeed", Constants.RESTRICTION);	
			factory.createSecondaryKey(highway, "oneway", Constants.RESTRICTION);
			factory.createSecondaryKey(highway, "motorcar", Constants.RESTRICTION);	
			factory.createSecondaryKey(highway, "bicycle", Constants.RESTRICTION);	
			
		this.getConfiguration().setRule(highway);
	}
	

	public static void main(String arg[]){
		new Test1().run();
	}
}
