package OSMImporterV2.transformation;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import OSMImporterV2.batch.util.Logger;
import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;
import OSMImporterV2.filter.model.Constants;
import OSMImporterV2.filter.model.PrimaryKey;
import OSMImporterV2.filter.model.SecondaryKey;
import OSMImporterV2.speichern.Speichern;
import OSMImporterV2.transformation.model.Polygon;

public class Transformation {

	private Set<Long> implizierteNodeIds = new HashSet<Long>();
	private Set<Polygon> polygone = new HashSet<Polygon>();
	
	private Speichern speichern = null;
		
	public Speichern getSpeichern() {
		return speichern;
	}

	public void setSpeichern(Speichern speichern) {
		this.speichern = speichern;
	}


	public void start(){
		
		start = System.currentTimeMillis() / 1000;
		
		speichern.start();
		
		speichern.beginTransaction();
		speichern.createPointLayer();
		speichern.createWKTLayer();
		speichern.commit();
		
		speichern.beginTransaction();
		speichern.createIndex();
		speichern.commit();
	}
		
	int knoten_gesamt = 0;
	int knoten_trans = 0;
	
	int kanten_gesamt = 0;
	
	int neighbout_kanten = 0;
	int prop_knoten = 0;
	int prop_eintraege = 0;
	int rest_knoten = 0;
	int rest_eintraege = 0;
	int attribute = 0;
	
	long start = 0;
	long end = 0;
	
	boolean polygon = false;
	boolean addSpatial = false;
	
	public void handleNode(OSMNode n, List<PrimaryKey> pks){
			
		long osm_id = n.getId();
						
		for(PrimaryKey pk : pks){
			
			if(pk.getTypeOf() == Constants.NODE){
				
				String value = n.tag.get(pk.getName());
				
				checkBeginTransaction();
					speichern.addAttribute(osm_id, pk.getName(), value); attribute++;
				checkCommit();					
				
			}
			
			for(SecondaryKey sk : pk.getAllSecondaryKeys().values()){
				
				if(sk.getTypeOf() == Constants.NODE 
						&& n.tag.containsKey(sk.getName())){
					
					String value = n.tag.get(sk.getName());
					
					if(sk.getValues().contains(value)
							|| sk.getValues().isEmpty() == true){
						checkBeginTransaction();
							speichern.addAttribute(osm_id, sk.getName(), value); 
						checkCommit();							
					}		
				}				
			}
		}
		
	}
		
	public void handleNode(OSMNode n){
	
		knoten_gesamt++;
		
		long osm_id = n.getId();
		
		if(implizierteNodeIds.contains(osm_id)){ //Nur Punkte, die auf Wegen liegen!

			checkBeginTransaction();
				speichern.addCoordinates(osm_id, n.getLat(), n.getLon());
			checkCommit();
			
			if(addSpatial){
				checkBeginTransaction();
					speichern.addToPointLayer(osm_id);
					checkCommit();
			}
		}
		
		//Polygon
		if(polygon){
			for(Polygon p : polygone){
				
				if(p.nodes.containsKey(n.getId())){
					p.nodes.put(n.getId(),n);
				}
			}	
	    }
		
	}
	
	public void endNodeSection(){
		
		Logger.log("END NODE SECTION");
		
		if(polygon){
			for(Polygon p : polygone){		
			
				//System.out.println(p.buildWKT());
			
				checkBeginTransaction();
					long id = speichern.createPolygon(p);
				checkCommit();
			
				checkBeginTransaction();
					speichern.addNameToPolygon(id, p.name);
				checkCommit();
			}
		}
		
		flush();
	}
	
	public void handleWay(OSMWay w, List<PrimaryKey> pks){
	
		//Implizierte Nodes Label Properties Restriction Neighbour mit distance
		
		//Implizierte Nodes
		for(Long nd_ref : w.nd_ref){
			
			if(implizierteNodeIds.contains(nd_ref) == false){
				
				implizierteNodeIds.add(nd_ref);
				
				checkBeginTransaction();
					speichern.createNode(nd_ref); knoten_trans++;
				checkCommit();
			}
		}
				
		Set<String> labels = new HashSet<String>();
		Map<String,String> properties = new HashMap<String,String>();
		Map<String,String> restrictions = new HashMap<String,String>();
		
		for(PrimaryKey pk : pks){
			
			if(pk.getTypeOf() == Constants.LABEL){
				labels.add(w.tag.get(pk.getName()));
			}else{ break; }
			
			for(SecondaryKey sk : pk.getAllSecondaryKeys().values()){
				
				if(w.tag.containsKey(sk.getName())){ //Schluessel kommt in Tags vor
					
					if(sk.getValues().isEmpty() == true
							|| sk.getValues().contains(w.tag.get(sk.getName()))){
							
						if(sk.getTypeOf() == Constants.PROPERTY){
							properties.put(sk.getName(),w.tag.get(sk.getName()));
						}
						else if(sk.getTypeOf() == Constants.RESTRICTION){
							restrictions.put(sk.getName(),w.tag.get(sk.getName()));
						}
					}		
				}
			}			
		}
				
		//Label hinzufuegen
		for(long node : w.nd_ref){
			
			for(String label : labels){
				checkBeginTransaction();
					speichern.addLabel(node, label);
				checkCommit();	
			}
		}
		
		for(int i = 1; i < w.nd_ref.size(); i++){		
				
			//Neighbour Kante
			checkBeginTransaction();
				speichern.addNeighbourEdge(w.nd_ref.get(i-1), w.nd_ref.get(i), 0.0f); neighbout_kanten++;
			checkCommit();	
			
			//Properties
			if(properties.size() > 0){
			
				checkBeginTransaction();
					long propertyID = speichern.getPropertyID(w.nd_ref.get(i-1), w.nd_ref.get(i));
				checkCommit();
			
				if(propertyID == -1){
				
					checkBeginTransaction();
						propertyID = speichern.createPropertyID(w.nd_ref.get(i-1), w.nd_ref.get(i)); prop_knoten++;
					checkCommit();			
				}
					
				for(Map.Entry<String, String> property : properties.entrySet()){
					checkBeginTransaction();
							speichern.addAttributeToProperty(propertyID,property.getKey(), property.getValue()); prop_eintraege++;
					checkCommit();	
				}	
			}
			
			//Restrictions
			if(restrictions.size() > 0){
				checkBeginTransaction();
					long restrictionID = speichern.getRestrictionID(w.nd_ref.get(i-1), w.nd_ref.get(i));
				checkCommit();
			
				if(restrictionID == -1){
				
					checkBeginTransaction();
					restrictionID = speichern.createRestrictionID(w.nd_ref.get(i-1), w.nd_ref.get(i)); rest_knoten++;
					checkCommit();			
				}
			
				for(Map.Entry<String, String> restriction : restrictions.entrySet()){
					checkBeginTransaction();
						speichern.addAttributeToRestriction(restrictionID,restriction.getKey(), restriction.getValue()); rest_eintraege++;
					checkCommit();	
				}
			
			}
		}
					
	}

	public void handleWay(OSMWay w){
		
		kanten_gesamt = kanten_gesamt + (w.nd_ref.size() - 1);
		
		//Polygon
		if(polygon){
			for(Polygon p : polygone){
			
				if(p.ways.containsKey(w.getId())){
					p.ways.put(w.getId(),w);
				}
			
				for(long nd_ref : w.nd_ref){
					p.nodes.put(nd_ref, null);
				}
			
			}	
		}
	}
	
	
	public void endWaySection(){
		Logger.log("END WAY SECTION");
		flush();
	}	

	public void handleRelation(OSMRelation r, List<PrimaryKey> key){
				

	}	
	
	public void handleRelation(OSMRelation r){
		
		if(polygon){
			//Grenze und Polygon
			if(r.tag.containsKey("boundary")
				&& r.tag.get("boundary").equals("administrative")
				&&r.tag.get("admin_level") != null
				&&r.tag.get("admin_level").equals("6")){
		
				Polygon p = new Polygon();
		
				p.relation = r;
		
				if(r.tag.containsKey("name")){
					p.name = r.tag.get("name");
				}
		
				if(r.tag.containsKey("admin_level")){
					p.admin_level = r.tag.get("admin_level");
				}
			
				for(Map.Entry<Long, String> member_ref : r.member_ref.entrySet()){
				
					if(member_ref.getValue().equals("way")){
						p.ways.put(member_ref.getKey(), null);
					}
					else if(member_ref.getValue().equals("node")){
						p.nodes.put(member_ref.getKey(), null);
					}
				}		
			
				polygone.add(p);
			}
		}
	}
	
	public void endRelationSection(){
		Logger.log("END RELATION SECTION");
		System.out.println("Polygone: " + polygone.size());
	}		
	
	public void shutdown(){

		end = (System.currentTimeMillis() / 1000) - start;
			
		System.out.println("Knoten: " + knoten_gesamt +"/"+ knoten_trans +" (gessamt/transormiert)");
		System.out.println("Kanten: " + kanten_gesamt +" (gesamt)");
		
		System.out.println("Neighbour Kanten: " + neighbout_kanten);
		System.out.println("Attribute: " + attribute);
		System.out.println("Property Knoten: " + prop_knoten);
		System.out.println("Property Eintraege: " + prop_eintraege);
		System.out.println("Restriction Knoten: " + rest_knoten);
		System.out.println("Restriction Eintaege: " + rest_eintraege);
		
		System.out.println("Laufzeit: " + end + "s");
		
		
		System.out.println("Knoten gesamt; Knoten transformiert; Kanten gesamt; Neigbour Kanten; Attributte; Property Knoten; Restrictionen; Polygone; Laufzeit");
		System.out.println(knoten_gesamt + "; " + knoten_trans + "; " + kanten_gesamt + "; " + neighbout_kanten + "; " +  attribute + "; " + prop_knoten + "; " + rest_knoten +"; " + polygone.size() + "; " + end);
		
		speichern.shutdown();
	}
		
	int txLimit = 999;
	int uncommitedChanges = 0;
	
	private void checkBeginTransaction(){
		
		if(uncommitedChanges == 0){
			speichern.beginTransaction();
		}
	}
	
	private void checkCommit(){
		
		uncommitedChanges++;
		
		if(uncommitedChanges >= txLimit){
			speichern.commit();
			uncommitedChanges = 0;
		}
	}
	
	private void flush(){
		if(uncommitedChanges > 0){
			speichern.commit();
			uncommitedChanges = 0;
		}
	}
}
