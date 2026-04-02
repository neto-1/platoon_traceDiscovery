package OSMImporter.util;

import java.util.HashMap;
import java.util.Map;

public class StatusCounterRegistry {

	public static final StatusCounterRegistry instance = new StatusCounterRegistry();
	
	private Map<String, StatusCounter> counters = new HashMap<String, StatusCounter>();
	
	public void add(String key, StatusCounter c){
		counters.put(key, c);
	}
	
	public StatusCounter get(String key){
		return counters.get(key);
	}
	
	public boolean contains(String key){
		return counters.containsKey(key);
	}
	
	public void print(String... keys){
		
		for(String key : keys){
			if(counters.containsKey(key))
				System.out.println(counters.get(key));
		}
		
	}
	
}
