package OSMImporter.Expression;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class Expression {

	public final Map<String,List<String>> properties = new HashMap<String,List<String>>();
	public final Map<String,List<String>> relations = new HashMap<String,List<String>>();
	
	public final Map<String,List<String>> optional_properties = new HashMap<String,List<String>>();
	public final Map<String,List<String>> optional_relations = new HashMap<String,List<String>>();
	
	private boolean optional = false;
	
	private String feature;
	private List<String> values = new LinkedList<String>();
	
	private Expression() {
		super();
	}

	public static Expression start(){
		return new Expression();
	}
	
	public Expression feature(String feature){
		this.optional = false;
		this.feature = feature;
		return this;
	}
	
	public Expression optionalFeature(String feature){
		this.optional = true;
		this.feature = feature;
		return this;
	}
	
	public Expression value(String value){
		this.values.add(value);
		return this;
	}
	
	public Expression allValues(){
		this.values.clear();
		return this;
	}
	
	public Expression asProperty(){
		
		if(!optional){
			properties.put(feature, values);
		}else{
			optional_properties.put(feature, values);
		}
		
		feature = null;
		values = new LinkedList<String>();
		
		return this;
	}
	
	public Expression asRelation(){
		
		if(!optional){
			relations.put(feature, values);
		}else{
			optional_relations.put(feature, values);
		}
		
		feature = null;
		values = new LinkedList<String>();
		
		return this;
	}
}
