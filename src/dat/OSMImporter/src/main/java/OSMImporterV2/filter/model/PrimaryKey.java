package OSMImporterV2.filter.model;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class PrimaryKey {

	private String name = null;
	private List<String> values = new LinkedList<String>();
	private int typeOf = Constants.UNKNOWN;
	private Map<String,SecondaryKey> secondaryKeys = new HashMap<String,SecondaryKey>();
	
	public PrimaryKey(String name) {
		super();
		this.name = name;
	}

	public PrimaryKey(String name, int typeOf) {
		super();
		this.name = name;
		this.typeOf = typeOf;
	}

	public PrimaryKey(String name, int typeOf, String...values) {
		super();
		this.name = name;
		this.typeOf = typeOf;
		
		for(String value : values)
			this.values.add(value);
	}

	
	public String getName(){
		return name;
	}
	
	public void addValue(String value){
		values.add(value);
	}
	
	public List<String> getValues(){
		return values;
	}
		
	public void setTypeOf(int typeOf){
		this.typeOf = typeOf;
	}
	
	public int getTypeOf(){
		return typeOf;
	}
		
	public void addSecondaryKey(SecondaryKey name){
		secondaryKeys.put(name.getName(), name);
	}
	
	public SecondaryKey getSecondaryKey(String name){
		return secondaryKeys.get(name);
	}
	
	public Map<String,SecondaryKey> getAllSecondaryKeys(){
		return secondaryKeys;
	}
	
}
