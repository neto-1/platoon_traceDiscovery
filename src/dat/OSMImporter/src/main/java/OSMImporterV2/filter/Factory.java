package OSMImporterV2.filter;

import OSMImporterV2.filter.model.PrimaryKey;
import OSMImporterV2.filter.model.SecondaryKey;

public class Factory {

	public static final Factory instance = new Factory();
	
	public PrimaryKey createPrimaryKey(String name, int typeOf){
		return new PrimaryKey(name,typeOf);
	}
	
	public PrimaryKey createPrimaryKey(String name, int typeOf, String...values){
		return new PrimaryKey(name,typeOf,values);
	}
	
	public PrimaryKey createSecondaryKey(PrimaryKey primaryKey, String name, int typeOf){
		
		SecondaryKey scondaryKey = new SecondaryKey(name, typeOf);
		primaryKey.addSecondaryKey(scondaryKey);
		return primaryKey;
	}
	
	public PrimaryKey createSecondaryKey(PrimaryKey primaryKey, String name, int typeOf,String...values){
		
		SecondaryKey scondaryKey = new SecondaryKey(name, typeOf,values);
		primaryKey.addSecondaryKey(scondaryKey);
		return primaryKey;
	}
	
}
