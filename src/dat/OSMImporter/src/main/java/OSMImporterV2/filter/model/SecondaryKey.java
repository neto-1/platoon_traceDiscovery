package OSMImporterV2.filter.model;

import java.util.LinkedList;
import java.util.List;

public class SecondaryKey {

	private String name = null;
	private List<String> values = new LinkedList<String>();
	private int typeOf = Constants.UNKNOWN;
	
	public SecondaryKey(String name) {
		super();
		this.name = name;
	}

	public SecondaryKey(String name, int typeOf) {
		super();
		this.name = name;
		this.typeOf = typeOf;
	}

	public SecondaryKey(String name, int typeOf, String... values) {
		super();
		this.name = name;
		this.typeOf = typeOf;
		
		for(String value : values)
			this.values.add(value);
	}
	
	public String getName(){
		return name;
	}
	
	public List<String> getValues(){
		return values;
	}
	
	public void addValue(String value){
		values.add(value);
	}
		
	public void setTypeOf(int typeOf){
		this.typeOf = typeOf;
	}
	
	public int getTypeOf(){
		return typeOf;
	}
}
