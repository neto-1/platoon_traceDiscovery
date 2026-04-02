package OSMImporterV2.filter;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import OSMImporterV2.filter.model.PrimaryKey;

public class DefaultConfiguration implements IConfiguration{

	protected Factory factory = Factory.instance;
	private Map<String,List<PrimaryKey>> primaryKeys = new HashMap<String,List<PrimaryKey>>();
	
	private int boundaryAdmin_Level = 6;
	
	public List<PrimaryKey> getRules(String name){
		return primaryKeys.get(name);
	}
	
	public void setRule(PrimaryKey value){
		
		List<PrimaryKey> result = primaryKeys.get(value.getName());
		
		if(result == null){
			result = new LinkedList<PrimaryKey>();
			primaryKeys.put(value.getName(), result);
		}

		result.add(value);
	}
	
	public boolean contains(String name){
		return primaryKeys.containsKey(name);
	}

	public void setBoundaryAdmin_Level(int level) {
		this.boundaryAdmin_Level = level;		
	}

	public int getBoundaryAdmin_Level() {
		return this.boundaryAdmin_Level;
	}
}
