package aStar;

/**
 * The Class ExpanderRestriction 
 * transforms the String representation of one of the restrictions given in the procedure CALL into an
 * restriction object which is used to ensure that this restriction is fulfilled by all Nodes or Relationships
 * which are traversed by aStar.
 * 
 * @author Nikita Maslov
 * @version 1.0
 */
public class ExpanderRestriction {
	
	private String name;//name of the property(property key)
	private String operator;//operator used in the restriction
	private String value;// value which is compared with the properties value
	
	/**
	 * Constructor for the Class ExpanderRestriction.
	 * 
	 * @param restriction The String representation of the restriction held by this instance of ExpanderRestriction.  
	 */
	public ExpanderRestriction(String restriction) throws IllegalArgumentException{
		
		String[] temp = restriction.split(" ",3);
		//Generates ExpanderRestrictions which are used to ensure that the given entity has the has the required property and a property value which fulfills the expression
		if(temp.length==3&&(temp[1].equals("=")||temp[1].equals("<>")||temp[1].equals("<")||temp[1].equals(">")||temp[1].equals("<=")||temp[1].equals(">=")||
		   temp[1].equals("STARTSWITH")||temp[1].equals("ENDSWITH")||temp[1].equals("CONTAINS"))){
			
			name=temp[0];
			operator = temp[1];
			value=temp[2];	
		}		
		else{
				
			if(temp.length==1){
				//Generates ExpanderRestrictions which are used to ensure that the given entity has the has the Property but do not contain a value
				name=temp[0];
				operator = "None";
				value=null;		
					
			}
			else{
				throw new IllegalArgumentException( "The Restriction '" + restriction +"' is not valid");
			}			
		}		
	}
	
	/**
	 * The Method getName returns the name(property key) of the property which is checked if it fulfills the restriction.
	 * 
	 * @return property name
	 */
	public String getName(){
		return name;
	}
	
	/**
	 * The Method getOperator returns value of the restriction.
	 * 
	 * @return property name
	 */
	public String getOperator(){
		return operator;
	}
	
	/**
	 * The Method getValue returns the value of the restriction.
	 * 
	 * @return property name
	 */
	public String getValue(){
		return value;
	}	
}