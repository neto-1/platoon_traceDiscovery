package OSMImporterV2.speichern;

import org.neo4j.driver.v1.AccessMode;
import org.neo4j.driver.v1.AuthTokens;
import org.neo4j.driver.v1.Driver;
import org.neo4j.driver.v1.GraphDatabase;
import org.neo4j.driver.v1.Session;
import org.neo4j.driver.v1.Transaction;

public class Builder {
	
	public static Builder instance = new Builder();
	
	public Neo4JConnection buildNeo4JConnection(String uri, String username, String password, AccessMode mode){
		return new Neo4JConnection(uri,username,password,mode);
	}
	
	public static class Neo4JConnection{
		
		private Driver driver;
		private Session session;
		
		private String uri;
		private String username;
		private String password;
		private AccessMode accessMode;
		
		private Transaction tx;
		
		private boolean isOpen = false;
		
		
		Neo4JConnection(String uri, String username, String password, AccessMode accessMode){
			this.uri = uri;
			this.username = username;
			this.password = password;
			this.accessMode = accessMode;
		}
		
		public void open(){		
			this.driver = GraphDatabase.driver(uri, AuthTokens.basic(username, password));	
			this.session = driver.session(accessMode);	
			isOpen = true;
		}
		
		public Transaction beginTransaction(){
			
			if(isOpen == false) open();
		
			if(tx == null || tx.isOpen() == false){
				tx = session.beginTransaction();
			}
		
			return tx;
		}
		
		public void close(){
			session.close();
			driver.close();
			
			isOpen = false;
		}
		
		public void flush(){
			tx.success();
			tx.close();
		}
		
		public boolean isOpen(){
			return isOpen;
		}
	}
}
