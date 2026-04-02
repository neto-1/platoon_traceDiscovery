package OSMImporter;

import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.neo4j.driver.v1.AccessMode;

import OSMImporter.database.Builder;
import OSMImporter.database.Builder.Neo4JConnection;
import OSMImporter.util.StatusCounter;
import OSMImporter.util.StatusCounterRegistry;
import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public class OnePassFullOSMImporter extends AbstractOSMImporter {

	private long start;
	private long finish;
	
	protected StatusCounterRegistry counters = StatusCounterRegistry.instance;
	
	private List<String> tags = new LinkedList<String>();
	private List<String> found_tags = new LinkedList<String>();
	
	
	protected Neo4JConnection graphDB;
	
	public OnePassFullOSMImporter(String uri, String username, String password) {
		super();
		
		graphDB = Builder.instance.
				buildNeo4JConnection(uri, username, password, AccessMode.WRITE);
	}

	@Override
	public void createNode(OSMNode n) {

//		boolean print = false;
//		
//		for(Map.Entry<String, String> entry : n.tag.entrySet()){
//			if(tags.contains(entry.getKey()) && entry.getValue().equals("traffic_signals")){	
//				print = true;
//			}
//		}
//				
//		if(print){ counters.get("node").increment(); printNode(n); }
		
	}
	
	private void printNode(OSMNode n){
		
		if(n.tag.size() == 0){ return; }
		
		System.out.print(n.getId() + ": ");
		
		for(Map.Entry<String, String> entry : n.tag.entrySet()){
			//System.out.print(entry.getKey()+ ", ");
			System.out.print(entry.getKey()+" ["+ entry.getValue()+"], ");
		}
		
		System.out.print("\n");
	}
	
	@Override
	public void createWay(OSMWay w) {

		boolean print = false;
		
		for(Map.Entry<String, String> entry : w.tag.entrySet()){
			if(tags.contains(entry.getKey())){
				print = true;
			}
		}
				
		if(print){ counters.get("way").increment(); printWay(w); }
	}

	private void printWay(OSMWay w){
		
		if(w.tag.size() == 0){ return; }
		
		System.out.print(w.getId() + ": ");
		
		for(Map.Entry<String, String> entry : w.tag.entrySet()){
			//System.out.print(entry.getKey()+ ", ");
			System.out.print(entry.getKey() + " ["+ entry.getValue()+"], ");
			if(found_tags.contains(entry.getKey()) == false){
				found_tags.add(entry.getKey());
			}
		}
		
		System.out.print("\n");
	}
	
	@Override
	public void createRelation(OSMRelation r) {

//		boolean print = false;
//		
//		for(Map.Entry<String, String> entry : r.tag.entrySet()){
//			if(tags.contains(entry.getKey())){
//				print = true;
//			}
//		}
//				
//		if(print){ counters.get("relation").increment(); printRelation(r); }

	}

	private void printRelation(OSMRelation r){
		
		if(r.tag.size() == 0){ return; }
		
		System.out.print(r.getId() + ": ");
		
		for(Map.Entry<String, String> entry : r.tag.entrySet()){
			System.out.print(entry.getKey()+ ", ");
		}
		
		System.out.print("\n");
	}	
	
	
	private void flush(){
		
	}
	
	@Override
	public void init() {

		counters.add("node", new StatusCounter(200000,"Node"));
		counters.add("way", new StatusCounter(50000,"Way"));
		counters.add("relation", new StatusCounter(50000,"Relation"));
	
		//Lookup
//		tags.add("traffic_sign");
//		tags.add("traffic_sign:forward");
//		tags.add("traffic_sign:backward");
//		tags.add("restriction");
		tags.add("lanes");
		
//		//Node Strukturen
//		tags.add("emergency");
//		tags.add("amenity");
//		tags.add("natural");
//		tags.add("shop");
//		tags.add("barrier");
//		tags.add("entrance");
//		tags.add("craft");
//		tags.add("crossing");
//		tags.add("highway"); //einzelne Laterne
//		tags.add("office");
//		tags.add("railway");
//		tags.add("leisure");
//		tags.add("power");
//		tags.add("sport");
//		tags.add("created_by");
//		tags.add("noexit");
//		tags.add("playground");
//		tags.add("waterway");
//		tags.add("traffic_calming");
//		tags.add("aeroway");
//		tags.add("manhole");
//		tags.add("historic");
//		tags.add("man_made");
//		tags.add("seamark:type");
//		tags.add("bus");
//		tags.add("tram");
//		tags.add("advertising");
//		tags.add("tourism");
//		tags.add("place");
//		tags.add("train");
//		tags.add("traffic_sign:backward");
//		tags.add("traffic_sign:forward");
//		tags.add("healthcare");
//		tags.add("traffic_sign");
//		tags.add("military");
//		tags.add("bicycle");
//		tags.add("disused:amenity");
//		tags.add("door");
//		tags.add("exit");
//		tags.add("communication");
//		tags.add("vending");
//		tags.add("name");
//		tags.add("surveillance");
//		
//		
//		tags.add("fixme");
//		tags.add("source");
//		tags.add("addr:city");
		
		
//		//Way Strukturen	
//		tags.add("building");
//		tags.add("building:part");
//		tags.add("highway");
//		tags.add("waterway");
//		tags.add("landuse");
//		tags.add("natural");
//		tags.add("barrier");
//		tags.add("man_made");
//		tags.add("railway");
//		tags.add("amenity");
//		tags.add("aeroway");
//		tags.add("leisure");
//		tags.add("boundary");
//		tags.add("shop");
//		tags.add("power");
//		tags.add("office");
//		tags.add("playground");
//		tags.add("footway");
//		tags.add("roof:ridge");
//		tags.add("roof:hip");
//		tags.add("heritage");
//		tags.add("area");
//		tags.add("area:highway");
//		tags.add("craft");
//		tags.add("indoor");
//		tags.add("embankment");
//		tags.add("roof:edge");
//		tags.add("public_transport");
//		tags.add("tourism");
//		tags.add("note");
//		tags.add("discgolf");
//		tags.add("disc_golf");
//		tags.add("indoor:highway");
//		tags.add("route");
//		tags.add("landcover");
//		tags.add("seamark:type");
//		tags.add("disused:shop");
//		tags.add("military");
//		tags.add("garden"); //kaputt
//		tags.add("room");
//		tags.add("leaf_type"); //kaputt 355791655
//		tags.add("stairwell");
//		tags.add("fixme");
//		tags.add("demolished:building");
//		tags.add("phone");
//		tags.add("mooring");
//		tags.add("historic");
//		tags.add("outdoor");
//		tags.add("addr:interpolation");
//		tags.add("parking");
//		tags.add("tactile_paving");
//		tags.add("historic:highway");
//		tags.add("roof:colour");
//		tags.add("roof:shape");
//		tags.add("disused:route");
//		tags.add("disused:highway");
//		tags.add("roof:valley");
//		tags.add("wall");
//		tags.add("foot");
//		tags.add("sport");
//		tags.add("construction");
//		tags.add("proposed");
//		tags.add("place");
//		tags.add("attraction");

//		//Relation Strukturen
//		tags.add("restriction");
//		tags.add("natural");
//		tags.add("landuse");
//		tags.add("route");
//		tags.add("boundary");
//		tags.add("name");
//		tags.add("area");		
		
		//graphDB.open();
				
		start = System.currentTimeMillis() / 1000;	
	}

	@Override
	public void shutdown() {
				
		finish = (System.currentTimeMillis() / 1000) - start;	

		//graphDB.close();
		
		System.out.println("Tags:");
		
		for(String tag : found_tags){
			System.out.println(tag);
		}
		
		System.out.println("Insgesamt bearbeitet in " + getCurrentIteration() +" Durchlaeufen");
		counters.print("node", "way", "relation");
				
		System.out.println("Duration: " + finish + " s");		
	}

}
