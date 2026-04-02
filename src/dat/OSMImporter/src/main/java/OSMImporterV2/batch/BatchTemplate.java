package OSMImporterV2.batch;

import OSMImporterV2.einlesen.Einlesen;
import OSMImporterV2.filter.Builder;
import OSMImporterV2.filter.Factory;
import OSMImporterV2.filter.Filter;
import OSMImporterV2.filter.IConfiguration;
import OSMImporterV2.speichern.Speichern;
import OSMImporterV2.transformation.Transformation;


public abstract class BatchTemplate {

	private String osmFile = null;
	private int runs = 3;
	private IConfiguration configuration = Builder
			.instance.buildConfiguration();
	private String uri;
	private String username;
	private String password;
	
	protected Factory factory = Factory.instance;
	
	private Einlesen einlesen;
	private Filter filter;
	private Transformation transformation;
	private Speichern speichern;
	
	public String getOsmFile() {
		return osmFile;
	}

	public void setOsmFile(String osmFile) {
		this.osmFile = osmFile;
	}

	public IConfiguration getConfiguration() {
		return configuration;
	}
	
	public int getRuns() {
		return runs;
	}

	public void setRuns(int runs) {
		this.runs = runs;
	}

	public void setDatabase(String uri, String username, String password){
		
		this.uri = uri;
		this.username = username;
		this.password = password;
	}

	private void orchestrierung(){
	
		einlesen = new Einlesen();
		filter = new Filter();
		transformation = new Transformation();
		speichern = new Speichern();
		
		einlesen.setOsmFile(osmFile);
		einlesen.setRuns(runs);
		einlesen.setFilter(filter);
		
		filter.setTransformation(transformation);	
		filter.setConfiguration(configuration);
		
		transformation.setSpeichern(speichern);
		
		speichern.setUri(uri);
		speichern.setUsername(username);
		speichern.setPassword(password);
	}
	
	public abstract void setup(); //osmFile, PrimarayKeys, database
	
	public void run(){
		
		setup();		
		orchestrierung();
		
		einlesen.start();
		einlesen.shutdown();
	}
}
