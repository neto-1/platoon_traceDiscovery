package OSMImporterV2.filter;

import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import OSMImporterV2.einlesen.model.OSMElement;
import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;
import OSMImporterV2.filter.model.PrimaryKey;
import OSMImporterV2.transformation.Transformation;

public class Filter {

	private IConfiguration configuration = null;
	private Transformation transformation = null;
	
	private boolean nodeEnd = false;
	private boolean wayEnd = false;
	private boolean relationEnd = false;
	
	public IConfiguration getConfiguration() {
		return configuration;
	}

	public void setConfiguration(IConfiguration configuration) {
		this.configuration = configuration;
	}

	public Transformation getTransformation() {
		return transformation;
	}

	public void setTransformation(Transformation transformation) {
		this.transformation = transformation;
	}

	public void start(){
		transformation.start();;
	}
	
	public void handleNode(OSMNode n, int run){
		
		if(run == 2){
			
			if(relationEnd == false){
				relationEnd = true;
				transformation.endRelationSection();
			}
		}
		else if(run == 3){
			
			List<PrimaryKey> pks = pass(n);
			
			if(pks.isEmpty() == false){		
				transformation.handleNode(n,pks);
			}
			
			transformation.handleNode(n);
		}	
	}
		
	public void handleWay(OSMWay w, int run){
		
		if(run == 2){
			
			List<PrimaryKey> pks = pass(w);	

			if(pks.isEmpty() == false){
				transformation.handleWay(w,pks);
			}
			
			transformation.handleWay(w);
			
		}else if(run == 3){
			if(nodeEnd == false){
				nodeEnd = true;
				transformation.endNodeSection();
			}
			
		}
	}
	
	public void handleRelation(OSMRelation r, int run){

		if(run == 1){
			
			List<PrimaryKey> pks = pass(r);	

			if(pks.isEmpty() == false){
				transformation.handleRelation(r,pks);
			}
			
			transformation.handleRelation(r);
			
			
		}else if(run == 2){
			
			if(wayEnd == false){
				wayEnd = true;
				transformation.endWaySection();
			}
		}
	}
	
	private List<PrimaryKey> pass(OSMElement e){
		
		List<PrimaryKey> result = new LinkedList<PrimaryKey>();
		
		for(Map.Entry<String, String> tag : e.tag.entrySet()){
			
			if(configuration.contains(tag.getKey())){
								
				List<PrimaryKey> rulePks = configuration.getRules(tag.getKey());
				
				String value = tag.getValue();
				
				for(PrimaryKey rulePk : rulePks){
					
					if(rulePk.getValues().contains(value)
							|| rulePk.getValues().isEmpty() == true){
						result.add(rulePk);
					}
				}			
			}
		}
		
		return result;
	}
	
	public void shutdown(){
		
		transformation.shutdown();
	}
}
