package OSMImporter;

import javax.xml.parsers.SAXParser;

import OSMImporter.xml.Builder;
import OSMImporter.xml.OSMHandler;
import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;
import OSMImporter.xml.parser.OSMSaxHandler;

public abstract class AbstractOSMImporter implements OSMHandler{

	private Builder builder = Builder.instance;
	
	private int iterations = 1;
	private int current_iteration = 0;
	
	public AbstractOSMImporter() {
		super();
	}	
		
	public AbstractOSMImporter(int iterations) {
		super();
		this.iterations = (iterations > 0) ? iterations : 1;
	}

	public void init(){}
	
	public void shutdown(){}
	
	public void initParser(String file){}
	
	public void shutdownParser(String file){}
	
	public abstract void createNode(OSMNode n);

	public abstract void createWay(OSMWay w);

	public abstract void createRelation(OSMRelation r);
		
	public int getIterations() {
		return iterations;
	}
	
	public int getCurrentIteration() {
		return current_iteration;
	}
	
	public void importFromFile(String...files){
		try{
			
			init();
			
			SAXParser parser = builder.buildSAXParser();
					
			while(current_iteration < iterations){
				
				current_iteration++;
				
				for(String file : files){
					if(fileCompression){
						parser.parse(builder.buildCompressedFileReader(file), new OSMSaxHandler(this));
					}else{
						parser.parse(file, new OSMSaxHandler(this));
					}
				}
				
			}
		
			shutdown();
			
		}catch(Exception e){
			e.printStackTrace();
		}
	}
	
	private boolean fileCompression = false;
		
	public boolean getCompression(){
		return this.fileCompression;
	}
	
	public AbstractOSMImporter enableCompression(){
		fileCompression = true;
		return this;
	}
	
	public AbstractOSMImporter disableCompression(){
		fileCompression = false;
		return this;
	}	
}
