package aStar;

import java.util.ArrayList;
import java.util.List;

import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.ResourceIterable;
import org.neo4j.graphdb.ResourceIterator;

/**
 * The Class Query is used to store the information 
 * concerning the aStar. It hold start and end node id,
 * cost and x,y properties, and all the restrictions which have
 * to be fulfilled by the aStar during traversal.
 * It also ensure that the given properties keys and relationship types do exist within the database.
 * 
 * @author Nikita Maslov
 * @version 1.0
 */
public class Query {
	
	public long start;

	public long end;
	
	public GraphDatabaseService graphService;

	public String costProperty;

	public String xProperty;

	public String yProperty;

	public CoordinateType coordinateType;

	public List<String> relationshipTypes;
	
	public ArrayList<ExpanderRestriction> nodeProperties = new ArrayList<ExpanderRestriction>();
	
	public ArrayList<ExpanderRestriction> relProperties = new ArrayList<ExpanderRestriction>();
	
	public Direction direction;
	
	 /**
     * Constructor for the Class Query.
     * 
     * @param graphService A GraphDatabaseService which is used for checking relationship types and properties.
     * @param start The id of the start node.
     * @param end The id of the end node.
     * @param costProperty The property which aStar will use to calculate the costs for traversing a relationship.
     * @param xProperty The property which represents the x value if "XY" is used as coordinateType or the latitude if the 
     *                  coordinate type is "COORDINATES"(longitude latitude representation).
     * @param yProperty The property which represents the y value if "XY" is used as coordinateType or the longitude if the 
     *                  coordinate type is "COORDINATES"(longitude latitude representation).
     * @param coordinateType The way the nodes coordinates are represented.
     * @param relationshipTypes The relationship Types which can be traversed by aStar.
     * @param relationshipProperties The entry's in the list can be either names of the properties(only relationships which have this property
     *        will be traversed) or expressions(only relationships which have the property and a property value that fulfills the
     *        expression will be traversed). For further details concerning the expressions read the aStarPlugin manual.
     * @param nodeProperties The entry's in the list can be either names of the properties(only nodes which have the property
     *        will be traversed) or expressions(only nodes which have the property and a property value that fulfills the
     *        expression will be traversed). For further details concerning the expressions read the aStarPlugin manual.
     *        
     * @param direction The Direction of relationships which will be traversed.
     * 
     */
	public Query( GraphDatabaseService graphService ,long start,long end,String costProperty,String xProperty,String yProperty,
				 String coordinateType, List<String> relationshipTypes,List<String> nodeProperties,
				 List<String> relationshipProperties,String direction) throws IllegalArgumentException{
		
		ResourceIterable<String> iterable = graphService.getAllPropertyKeys();
		 
		
		propertyCheck(iterable,costProperty);
		propertyCheck(iterable,xProperty);
		propertyCheck(iterable,yProperty);
		this.graphService = graphService;
		this.start = start;
		this.end = end;
		this.costProperty= costProperty;
		this.xProperty = xProperty;
		this.yProperty = yProperty;
		
		switch(coordinateType.toUpperCase()){
		
			case("XY"):
				this.coordinateType = CoordinateType.XY;
				break;
			
			case("COORDINATES"):
				this.coordinateType = CoordinateType.COORDINATES;
				break;
								
			default:
				throw new IllegalArgumentException( "The coordinate type is not valid");
	
		}
		//Checks if all given relationship types exist
		if((relationshipTypes.isEmpty() != true)){
			
			boolean exists;
			ResourceIterable<RelationshipType> relationshipTypeIterable = graphService.getAllRelationshipTypesInUse();
			
			for (String relName : relationshipTypes){
				
				exists = false;
				
				
				for (RelationshipType relType : relationshipTypeIterable) {
					if(relType.name().equals(relName)){
						exists=true;
						break;
					}
				}
				
				if (exists == false){
					
					throw new IllegalArgumentException( "The Relationship Type '"+ relName +"' does not exist in the given Database");
					
				}
			}
		}
		
		this.relationshipTypes=relationshipTypes;

		for(int j=0;j < nodeProperties.size();j++){
			this.nodeProperties.add(new ExpanderRestriction(nodeProperties.get(j)));
			propertyCheck(iterable,this.nodeProperties.get(j).getName());
		}
		

		for(int j=0;j < relationshipProperties.size();j++){
			this.relProperties.add(new ExpanderRestriction(relationshipProperties.get(j)));
			propertyCheck(iterable,this.relProperties.get(j).getName());	
		}
		

		switch(direction.toLowerCase()){
		
		case("incoming"):
			this.direction = Direction.INCOMING;
			break;
		
		case("outgoing"):
			this.direction = Direction.OUTGOING;
			break;
			
		case("both"):
			this.direction = Direction.BOTH;
			break;
				
		default:
			throw new IllegalArgumentException( "The direction type is not valid");
		}	
	}
	
	/**
	 * The Method propertyCheck checks if the database contains a property key with the given name.
	 * 
	 * @param propertyKey The name of the property which is checked.
	 * @param propertyKeyIterable A resource iterable with all property key in the database.
	 */
	private void propertyCheck(ResourceIterable<String> propertyKeyIterable, String propertyKey){
		
			
		boolean exists;		
		exists = false;
				
		
		ResourceIterator<String> iterator = propertyKeyIterable.iterator();

		     while ( iterator.hasNext() )
		     {
		    	 if(iterator.next().equals(propertyKey)){
						exists=true;
						iterator.close();
						break;
					}
		     }
		
				
		if (exists == false){
					
			throw new IllegalArgumentException( "The Property '"+ propertyKey +"' does not exist in the given Database");			
		}	
	}
	
	/**
	 * The Method getEnd returns the id of the end node.
	 * 
	 * @return Id of the end node.
	 */
	public long getEnd(){
		return this.end;
	}
	
	/**
	 * The Method getStart returns the id of the start node.
	 * 
	 * @return Id of the start node.
	 */
	public long getStart(){
		return this.start;
	}
	
	/**
	 * The Method getCostProperty property returns the property key of cost property.
	 * 
	 * @return Property key of cost property.
	 */
	public String getcostProperty(){
		return this.costProperty;
	}
	
	/**
	 * The Method getXProperty returns the property key of the X property.
	 * 
	 * @return Property key of the X property.
	 */
	public String getXProperty(){
		return this.xProperty;
	}
	
	/**
	 * The Method getYProperty returns the property key of the Y property.
	 * 
	 * @return Property key of the Y property.
	 */
	public String getYProperty(){
		return this.yProperty;
	}
	
	/**
	 * The Method getYProperty returns the property key of the Y property.
	 * 
	 * @return Property key of the Y property.
	 */
	public CoordinateType getCoordinateType(){
		return this.coordinateType;
	}
	
	/**
	 * The Method getRelationshipTypes returns the names of the relationship types.
	 * 
	 * @return Names of the relationship types.
	 */
	public List<String> getRelationshipTypes(){
		return this.relationshipTypes;
	}
	
	/**
	 * The Method getnodeProperties returns the restrictions for the Node properties.
	 * 
	 * @return Restrictions for the Node properties.
	 */
	public ArrayList<ExpanderRestriction> getnodeProperties(){
		return this.nodeProperties;
	}
	
	/**
	 * The Method getrelProperties returns the the restrictions for the Relationship properties.
	 * 
	 * @return Restrictions for the Relationship properties.
	 */
	public ArrayList<ExpanderRestriction> getrelProperties(){
		return this.relProperties;
	}
	
	/**
	 * The Method getDirection returns the direction of Relationship which aStar should traverse.
	 * 
	 * @return Direction of the Relationship.
	 */
	public Direction  getDirection(){
		return this.direction;
	}
}