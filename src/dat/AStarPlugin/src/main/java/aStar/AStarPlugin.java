package aStar;

import java.util.List;
import java.util.stream.Stream;

import org.neo4j.graphalgo.CostEvaluator;
import org.neo4j.graphalgo.EstimateEvaluator;
import org.neo4j.graphalgo.GraphAlgoFactory;
import org.neo4j.graphalgo.PathFinder;
import org.neo4j.graphalgo.WeightedPath;
import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.GraphDatabaseService;
import org.neo4j.graphdb.Node;
import org.neo4j.graphdb.Path;
import org.neo4j.graphdb.Relationship;
import org.neo4j.procedure.Context;
import org.neo4j.procedure.Name;
import org.neo4j.procedure.Procedure;
import static org.neo4j.procedure.Mode.WRITE;

/**
 * Procedure Class AStarPlugin.
 * Contains The Procedures offered by the plugin.
 * Maintains the connection with the database.
 * 
 * @author Nikita Maslov
 * @version 1.0
 */
public class AStarPlugin {
	
    @Context
    public GraphDatabaseService db;

    public static Query query;
    
    public static float EARTH_DIAMETER = Float.valueOf("12756.274");
            
    /**
     * The Procedure ExtendedAStar uses the aStar algorithm to find the shortest path between two given nodes
     * which fulfills the given restrictions.
     * 
     * @param start The id of the start node.
     * @param end The id of the end node.
     * @param costProperty The property which aStar will use to calculate the costs for traversing a relationship.
     *                     Has to contain values which can be cast to a Double or a double because aStar is only working with double values.
     * @param xProperty The property which represents the x value if "XY" is used as coordinateType or the latitude if the 
     *                  coordinate type is "COORDINATES"(longitude latitude representation). Has to contain a value which can be cast to Double.
     * @param yProperty The property which represents the y value if "XY" is used as coordinateType or the longitude if the 
     *                  coordinate type is "COORDINATES"(longitude latitude representation). Has to contain a value which can be cast to Double.
     * @param coordinateType The way the nodes coordinates are represented, only "xy" and "coordinates" are accepted. 
     * @param relationshipTypes The relationship Types which can be traversed by aStar. If the List is empty all relationship types in the database can be traversed.
     * @param relationshipProperties The entry's in the list can be either names of the properties(only relationships which have this property
     *        will be traversed) or expressions(only relationships which have the property and a property value that fulfills the
     *        expression will be traversed). For further details concerning the expressions read the aStarPlugin manual.
     * @param nodeProperties The entry's in the list can be either names of the properties(only nodes which have the property
     *        will be traversed) or expressions(only nodes which have the property and a property value that fulfills the
     *        expression will be traversed). For further details concerning the expressions read the aStarPlugin manual.
     *        
     * @param direction The Direction of relationships which will be traversed. Accepted values are "outgoing","incoming" and "both".
     *        
     * @return The shortest Path between start and end node which fulfills the given restrictions. Empty record if no such path exists.
     */
    @Procedure( name = "extendedAStar", mode =WRITE)
    public Stream<ResultPath> extendedAStar( @Name("start") long start,
                        @Name("end") long end,
                        @Name("costProperty") String costProperty,
                        @Name("xProperty") String  xProperty,
                        @Name("yProperty") String  yProperty,
                        @Name("coordinateType") String coordinateType,
                        @Name("relationshipTypes") List<String> relationshipTypes,
                        @Name("nodeProperties") List<String>  nodeProperties,
                        @Name(" relationshipProperties") List<String> relationshipProperties,
                        @Name("direction") String direction){
    	
    	query = new Query(db,start,end,costProperty,xProperty,yProperty,coordinateType,relationshipTypes,nodeProperties,relationshipProperties,direction);
    	
    	
    	EstimateEvaluator<Double> estimateEvaluator = new EstimateEvaluator<Double>() {
			
    		public Double getCost(Node arg0, Node arg1) {

				double lon1 = Double.valueOf(arg0.getProperty(query.getYProperty()).toString());
				double lat1 = Double.valueOf(arg0.getProperty(query.getXProperty()).toString());
				double lon2 = Double.valueOf(arg1.getProperty(query.getYProperty()).toString());
				double lat2 = Double.valueOf(arg1.getProperty(query.getXProperty()).toString());

				if ( query.getCoordinateType() != null && query.getCoordinateType()==CoordinateType.XY) {
					return computeDistanceByXY(lon1, lat1, lon2, lat2);
				} 
				else {
					return computeDistanceByCoordinates(lon1, lat1, lon2, lat2);
				}
			}
		};
		
		CostEvaluator<Double> lengthEvaluator = new CostEvaluator<Double>() {

			
			public Double getCost(Relationship arg0, Direction arg1) {
				return Double.valueOf(arg0.getProperty(query.getcostProperty()).toString());
			}

		};

    	PathFinder<WeightedPath> pathFinder = GraphAlgoFactory.aStar(new RestrictedPathExpander(query), lengthEvaluator, estimateEvaluator);
		
    	Node node1 = db.getNodeById(start);
		Node node2 = db.getNodeById(end);
		
		WeightedPath path;
		
		try{
			path = pathFinder.findSinglePath(node1, node2);
		}
		catch(ClassCastException e){
			throw new IllegalArgumentException( "The costProperty, the xProperty or the y Property cannot be converted to Double");		
		}
			
		ResultPath result = new ResultPath(null);
				
		if(path != null){
			result = new ResultPath(path);
		}
		return Stream.of(result);	

    } 
    
    /**
	 * Computes the distance between two points using given coordinates in form of "xy". 
	 * 
	 * @param x1 x of the first point
	 * @param y1 y of the first point
	 * @param x2 x of the second point
	 * @param y2 y of the second point
	 * 
	 * @return distance between two points
	 */
    public Double computeDistanceByXY(double x1, double y1, double x2, double y2) {
		double dx = x1 - x2;
		double dy = y1 - y2;
		double distance = Math.sqrt(Math.pow(dx, 2) + Math.pow(dy, 2));
		return distance;
	}
    
    
    /**
	 * Computes the distance between two coordinates in kilometers using given
	 * coordinates in form of longitudes and latitudes.
	 * 
	 * @param rlon1 first node longitude
	 * @param rlat1 first node latitude
	 * @param rlat2 second latitude
	 * @param rlon2 second longitude
	 * 
	 * @return distance between the two nodes in kilometers
	 */
    public Double computeDistanceByCoordinates(double rlon1, double rlat1, double rlon2, double rlat2) {
		double delta_long = Math.toRadians(rlon1 - rlon2);
		double delta_lat = Math.toRadians(rlat1 - rlat2);

		double a = Math.pow(Math.sin(delta_lat / 2), 2) + Math.cos(Math.toRadians(rlat2))
				* Math.cos(Math.toRadians(rlat1)) * Math.pow(Math.sin(delta_long / 2), 2);

		double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
		double d = EARTH_DIAMETER * c / 2;

		return d;
	}
    /**
     * Class ResultPath defines the type of the record 
     * which will be returned by the procedure through a Java 8 stream.
     * For further details read the Neo4j procedures API.
     * 
     * @author Nikita Maslov
     * @version 1.0
     */	
    public static class ResultPath{
        
    	public Path path;
    	  
    	public ResultPath( Path p ){
    		path= p;
    	}
    }
}