package OSMImporterV2.einlesen;

import javax.xml.parsers.SAXParser;

import OSMImporterV2.einlesen.parser.OSMSaxHandler;
import OSMImporterV2.einlesen.Builder;
import OSMImporterV2.einlesen.OSMHandler;
import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;
import OSMImporterV2.filter.Filter;

public class Einlesen implements OSMHandler{

	private Builder builder = Builder.instance;
	
	private String osmFile = null;
	private Filter filter = null;
	private int runs = 1;
	private int current_run = 0;
	
	public String getOsmFile() {
		return osmFile;
	}

	public void setOsmFile(String osmFile) {
		this.osmFile = osmFile;
	}

	public Filter getFilter() {
		return filter;
	}

	public void setFilter(Filter filter) {
		this.filter = filter;
	}

	public int getRuns() {
		return runs;
	}

	public void setRuns(int runs) {
		this.runs = runs;
	}

	public void start(){
		try{
			
			filter.start();
			
			while(current_run < runs){
				
				current_run++;
			
				SAXParser parser = builder.buildSAXParser();
				parser.parse(osmFile, new OSMSaxHandler(this));
			}		
		}catch(Exception e){
			e.printStackTrace();
		}		
	}

	public void createNode(OSMNode n) {
		filter.handleNode(n, current_run);
	}

	public void createWay(OSMWay w) {
		filter.handleWay(w, current_run);		
	}

	public void createRelation(OSMRelation r) {
		filter.handleRelation(r, current_run);
	}
	
	public void shutdown(){
		filter.shutdown();
	}
}
