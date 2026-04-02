package aStar;

import java.util.ArrayList;
import java.util.List;
 
import org.neo4j.graphdb.Direction;
import org.neo4j.graphdb.Entity;
import org.neo4j.graphdb.Path;
import org.neo4j.graphdb.PathExpander;
import org.neo4j.graphdb.Relationship;
import org.neo4j.graphdb.RelationshipType;
import org.neo4j.graphdb.traversal.BranchState;

/**
 * The Class RestrictedPathExpander implements the 
 * Interface PathExpander and is used to filter the relationships 
 * which are used by AStar during traversal so that only 
 * relationships  which have the right type and fulfill the given restrictions are used by AStar.
 * 
 * @author Nikita Maslov
 * @version 1.0
 */
public class RestrictedPathExpander implements PathExpander<String> {

	private final Query query;
	private final RelationshipType[] relTypes;

	/**
	 * Constructor for the Class RestrictedPathExpander.
	 * 
	 * @param query An Query Object which contains the relationship types and the property restrictions.
	 * 
	 */
	public RestrictedPathExpander( Query query ){
		
		this.query = query;
		if(query.getRelationshipTypes().isEmpty() != true){
			relTypes= new RelationshipType[query.getRelationshipTypes().size()];
		
			for (int i = 0; i<query.getRelationshipTypes().size();i++){
		
				relTypes[i]= RelationshipType.withName(query.getRelationshipTypes().get(i));
			}
		}
		else{
			relTypes = null;
		}
	}


	/**
	 * This method is used by AStar during traversal to get the nodes which are used to traverse further.
	 * 
	 * @param path The path which has been traversed by AStar by now.
	 * @param state The branch state. AStar always sets this to the same, default value.
	 * 
	 * @return An Iterable with relationships which are used by AStar for further traversal.
	 */
	public Iterable<Relationship> expand(Path path, BranchState<String> state){
	
		Iterable<Relationship> relations;
		List<Relationship> results = new ArrayList<Relationship>();
	
		if(relTypes != null){
	   
			if(query.getDirection()== Direction.BOTH){
				relations = path.endNode().getRelationships(relTypes); 
			}
			else{
				relations = path.endNode().getRelationships( query.getDirection(), relTypes ); 
			}	
		}
		else{
			if(query.getDirection()== Direction.BOTH){
				relations = path.endNode().getRelationships(); 
			}
			else{
				relations = path.endNode().getRelationships( query.getDirection()); 
			}
		}
		for ( Relationship r : relations){
			
			if(computeRelation(query.getrelProperties(),r) == true){
				if(computeRelation(query.getnodeProperties(),r.getOtherNode(path.endNode())) ==true){
					results.add(r);
					
				}			
			}
        }
		
		relations = results;
		return relations;
	}
	
	
	/**
	 * This Method has to be implemented by every class which implements the interface PathExpander.
	 * As it is not used by AStar in only returns null in this case.
	 * 
	 * @return null.
	 */
	public PathExpander<String> reverse(){
		return null;
	}
	
	
	/**
	 * This Method is used to check if a Entity (relationship or node) fulfills the given restrictions.
	 * 
	 * @param statements The restrictions which have to be fulfilled by the Entity.
	 * @param entity The entity which is checked.
	 * 
	 * @return true if the entity fulfills the restrictions, false if not.
	 */
	private boolean computeRelation(ArrayList<ExpanderRestriction> statements, Entity entity){
			
		if(statements==null){
			return true;
		}
		for ( ExpanderRestriction s : statements){

			if(entity.hasProperty(s.getName())){
				
				if(!s.getOperator().equals("None")){
					if(computeRestriction(s,entity)== false){
						return false;
					}
				}	
			}
			else{
				return false;
			}     
        }
		return true;
		
	}

	
	/**
	 * This Method checks if an Entity(relationship or node) fulfills a given restriction.
	 * 
	 * @param restriction The restriction which has to be fulfilled by the Entity.
	 * @param entity The entity which is checked.
	 * 
	 * @return true if the entity fulfills the restriction, false if not.
	 */
	private boolean computeRestriction(ExpanderRestriction restriction, Entity entity){
		
		boolean notRemovable = true;
		
			
			switch(restriction.getOperator()){
			
			case"=":
				notRemovable = entity.getProperty(restriction.getName()).toString().equals(restriction.getValue());
				break;
				
			case"<>":
				notRemovable = !(entity.getProperty(restriction.getName()).toString().equals(restriction.getValue()));
				break;
								
			default:
				
				if(entity.getProperty(restriction.getName()) instanceof String){
					switch(restriction.getOperator()){
					
					case"STARTSWITH":
						notRemovable = (entity.getProperty(restriction.getName()).toString().startsWith(restriction.getValue()));
						break;
						
					case"CONTAINS":
						notRemovable = (entity.getProperty(restriction.getName()).toString().contains(restriction.getValue()));
						break;
						
					case"ENDSWITH":
						notRemovable = (entity.getProperty(restriction.getName()).toString().endsWith(restriction.getValue()));
						break;
						
					default:
						throw new IllegalArgumentException( "The Operator '"+ restriction.getOperator() + "' is not valid for String properties");	
					}
				}
				else{	
					if(entity.getProperty(restriction.getName()) instanceof Character){
					
						switch(restriction.getOperator()){
					
						case">=":
							notRemovable = ((Character)(entity.getProperty(restriction.getName())) >= restriction.getValue().charAt(0));
							break;
						
						case">":
							notRemovable = ((Character)(entity.getProperty(restriction.getName())) > restriction.getValue().charAt(0));
							break;
						
						case"<=":
							notRemovable = ((Character)(entity.getProperty(restriction.getName())) <= restriction.getValue().charAt(0));
							break;
						
						case"<":
							notRemovable = ((Character)(entity.getProperty(restriction.getName())) < restriction.getValue().charAt(0));
							break;
						
						default:
							throw new IllegalArgumentException("The Operator '"+ restriction.getOperator() + "' is not valid for character properties");	
						}
					}
					else{
						if(entity.getProperty(restriction.getName()) instanceof Boolean){
							throw new IllegalArgumentException( "The Operator '"+ restriction.getOperator() + "' is not valid for boolean properties");	
						}
						else{
							
							try{
								switch(restriction.getOperator()){
							
								case">=":
									notRemovable = Double.parseDouble(entity.getProperty(restriction.getName()).toString()) >= Double.parseDouble(restriction.getValue());
									break;
								
								case">":
									notRemovable = Double.parseDouble(entity.getProperty(restriction.getName()).toString()) > Double.parseDouble(restriction.getValue());
									break;
							
								case"<=":
									notRemovable = Double.parseDouble(entity.getProperty(restriction.getName()).toString()) <= Double.parseDouble(restriction.getValue());
									break;
							
								case"<":
									notRemovable = Double.parseDouble(entity.getProperty(restriction.getName()).toString()) < Double.parseDouble(restriction.getValue());
									break;
							
								default:
									throw new IllegalArgumentException(  "The Operator '"+ restriction.getOperator() + "' is not valid for number properties");
								}
							}catch(ClassCastException e1){
								throw new IllegalArgumentException("The Operator '"+ restriction.getOperator() + "' is not valid for List properties");
								
							}catch(NumberFormatException e2){
								throw new IllegalArgumentException("The Value '"+ restriction.getValue() + "' is not valid for Number properties");
									
							}
						}					
					}
				}
			}
		
		return notRemovable;	
	}	
}

