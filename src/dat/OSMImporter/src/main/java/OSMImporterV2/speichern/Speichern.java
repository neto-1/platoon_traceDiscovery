package OSMImporterV2.speichern;

import static org.neo4j.driver.v1.Values.parameters;

import java.util.HashMap;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.StatementResult;
import org.neo4j.driver.v1.Transaction;

import OSMImporterV2.batch.util.Logger;
import OSMImporterV2.speichern.Builder.Neo4JConnection;
import OSMImporterV2.transformation.model.Polygon;

public class Speichern {
	
	private String uri;
	private String username;
	private String password;
	
	private Neo4JConnection graphDB;
	
	private Map<String,String> labelCache = new HashMap<String,String>();
	private Map<String,String> attributeCache = new HashMap<String,String>();
	private Map<String,String> propertyCache = new HashMap<String,String>();
	private Map<String,String> restrictionCache = new HashMap<String,String>();
	
	public String getUri() {
		return uri;
	}

	public void setUri(String uri) {
		this.uri = uri;
	}

	public String getUsername() {
		return username;
	}

	public void setUsername(String username) {
		this.username = username;
	}

	public String getPassword() {
		return password;
	}

	public void setPassword(String password) {
		this.password = password;
	}

	public void beginTransaction(){
		
		Logger.log("Begin Transaction");
		tx = graphDB.beginTransaction();
	}
	
	public void commit(){
			
		Logger.log("Commit");
		tx.success();
		tx.close();
		
		Logger.log( Long.toString(Runtime.getRuntime().freeMemory() / (1024*1024*1024)));
	}
	
	private Transaction tx = null;
	
	public void createPointLayer(){		

		Logger.log("CREATE Point Layer");		
		tx.run("CALL spatial.addPointLayerWithConfig('data','lon:lat')");
		
	}
		
	public void createWKTLayer(){
		
		Logger.log("CREATE WKT Layer");		
		tx.run("CALL spatial.addWKTLayer('grenzen', 'wkt')");
		
	}
	
	public void createIndex(){
		
		Logger.log("CREATE Index on Road");
		tx.run("CREATE INDEX ON :Road(osm_id)");
		
	}	
	
	
	public void createNode(long osm_id){
		
		tx.run("CREATE (n:Road {osm_id: {n_id}}) RETURN n;",
				parameters("n_id", osm_id));
		
	}
	
	public void addCoordinates(long osm_id, float lat, float lon){
		
		tx.run("match (n:Road {osm_id: {n_id}}) set n.lon = {lon}, n.lat = {lat} return n",
			parameters("n_id", osm_id, "lon", lon, "lat", lat));
		
	}
	
	public void addToPointLayer(long osm_id){
				
		tx.run("MATCH (n:Road {osm_id: {n_id}}) WITH n CALL spatial.addNode('data',n) YIELD node RETURN n;",
				parameters("n_id", osm_id));
		
	}
	
	public void addLabel(long osm_id, String label){
				
		if(labelCache.containsKey(label) == false){
			labelCache.put(label, "match (n:Road {osm_id: {n_id}}) set n :"+label+" return n");
		}
		
		tx.run(labelCache.get(label),
			parameters("n_id", osm_id));
	}
	
	public void addAttribute(long osm_id, String attribute, String value){
		
		if(attributeCache.containsKey(attribute) == false){
			attributeCache.put(attribute, "match (n:Road {osm_id: {n_id}}) set n."+attribute+" = {value} return n");
		}

		tx.run(attributeCache.get(attribute),
			parameters("n_id", osm_id, "value", value));
	}
	
	public void addNeighbourEdge(long n, long m, float distance){
			
		tx.run("MATCH (n:Road {osm_id: {n_id}}), (m:Road {osm_id: {m_id}}) MERGE (n)-[:neighbour {distance: {d}}]-(m)",
				parameters("n_id", n,"d", distance,"m_id", m));
		
	}
	
	public long getPropertyID(long n, long m){
		
		StatementResult result = tx.run("MATCH (n:Road {osm_id: {n_id}})-[]-(p:Property)-[]-(m:Road {osm_id: {m_id}}) return id(p) as propertyID",
				parameters("n_id", n,"m_id", m));
		
		if(result.hasNext()){		
			return result.next().get("propertyID").asLong();
		}
		
		return -1L;
	}
	
	public long createPropertyID(long n, long m){
		
		StatementResult result = tx.run("MATCH (n:Road {osm_id: {n_id}}), (m:Road {osm_id: {m_id}}) CREATE (p:Property) MERGE (n)-[:property]-(p)-[:property]-(m) return id(p) as propertyID",
				parameters("n_id", n,"m_id", m));
		
		if(result.hasNext()){		
			return result.next().get("propertyID").asLong();
		}
		
		return -1L;
				
	}
	
	public void addAttributeToProperty(long propertyID, String attribute, String value){
		
		if(propertyCache.containsKey(attribute) == false){
			propertyCache.put(attribute, "match (n:Property) where id(n) = {n_id} set n."+attribute+" = {value} return n");
		}
		
		tx.run(propertyCache.get(attribute),
			parameters("n_id", propertyID, "value", value));
	}
	
	public long getRestrictionID(long n, long m){
		
		StatementResult result = tx.run("MATCH (n:Road {osm_id: {n_id}})-[]-(r:Restriction)-[]-(m:Road {osm_id: {m_id}}) return id(r) as restrictionID",
				parameters("n_id", n,"m_id", m));
		
		if(result.hasNext()){		
			return result.next().get("restrictionID").asLong();
		}
		
		return -1L;
	}
	
	public long createRestrictionID(long n, long m){
		
		StatementResult result = tx.run("MATCH (n:Road {osm_id: {n_id}}), (m:Road {osm_id: {m_id}}) CREATE (r:Restriction) MERGE (n)-[:forward]-(r)-[:backward]-(m) Return id(r) as restrictionID",
				parameters("n_id", n,"m_id", m));
		
		if(result.hasNext()){		
			return result.next().get("restrictionID").asLong();
		}
		
		return -1L;		
	}
	
	public void addAttributeToRestriction(long restrictionID, String attribute, String value){
		
		if(restrictionCache.containsKey(attribute) == false){
			restrictionCache.put(attribute, "match (n:Restriction) where id(n) = {n_id} set n."+attribute+" = {value} return n");
		}
		
		tx.run(restrictionCache.get(attribute),
			parameters("n_id", restrictionID, "value", value));
	}
	
	public long createPolygon(Polygon p){
					
		//tx.run("CREATE (p:Polygon { name : {name}, admin_level : {admin_level}, wkt : {wkt}}) return p;",
		//		parameters("name", p.name,"admin_level", p.admin_level,"wkt", wkt));
		
		StatementResult result = tx.run("CREATE (p:Polygon { wkt: \""+ p.buildWKT() +"\"}) WITH p CALL spatial.addNode('grenzen',p) YIELD node RETURN id(p) as polyID;");
		
		if(result.hasNext()){		
			return result.next().get("polyID").asLong();
		}
		
		return -1L;
	}
	
	
	public void addNameToPolygon(long id, String name){
				
		tx.run("match (n:Polygon) where id(n) = {n_id} set n.polygonname = {value} return n",
			parameters("n_id", id, "value", name));
	}
	
	public void start(){
		
		graphDB = Builder.instance.
				buildNeo4JConnection(uri, username, password, AccessMode.WRITE);
		
		Logger.log("Open DB");
		graphDB.open();
	}
	
	public void shutdown(){
		
		Logger.log("Close DB");
		graphDB.close();
	}
}
