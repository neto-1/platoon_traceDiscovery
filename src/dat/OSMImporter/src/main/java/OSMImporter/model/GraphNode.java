package OSMImporter.model;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import OSMImporter.xml.model.OSMNode;

public class GraphNode extends OSMNode{
	
	//public final List<GraphNode> neighbours = new LinkedList<GraphNode>();
	public final Neighbours neighbours = new Neighbours(this);	
	public final Labels labels = new Labels();
	
	public final Map<String,Object> properties = new HashMap<String,Object>();
	
	public GraphNode(long id) {
		super(id, 0.0f, 0.0f);
	}
	
	public GraphNode(long id, String... labels) {
		super(id, 0.0f, 0.0f);
		
		for(String label : labels){
			this.labels.add(label);
		}
	}
	
	public class Labels{
		
		List<String> labels = new LinkedList<String>();
		
		public void add(String label){
			if(labels.contains(label) == false){
				labels.add(label);
			}
		}
		
		public void remove(String label){
			labels.remove(label);
		}
		
		public int getSize(){
			return labels.size();
		}
		
		public String get(int index){
			return labels.get(index);
		}
		
		public String[] getAll(){
			return labels.toArray(new String[labels.size()]);
		}
	}
	
	public class Neighbours{
		
		private GraphNode node;
		protected List<GraphNode> neighbours = new LinkedList<GraphNode>();

		protected Map<Long,String> relationships = new HashMap<Long,String>();
		
		public Neighbours(GraphNode node) {
			super();
			this.node = node;
		}

		public void add(GraphNode neighbour){
			if(this.neighbours.contains(neighbour) == false){
				this.neighbours.add(neighbour);
				neighbour.neighbours.neighbours.add(node);
			}
		}
		
		public void remove(GraphNode neighbour){
			if(this.neighbours.contains(neighbour) == true){
				
				relationships.remove(neighbour.getId());
				neighbour.neighbours.relationships.remove(node.getId());
				
				this.neighbours.remove(neighbour);
				neighbour.neighbours.neighbours.remove(node);
			}
		}
		
		public boolean contains(GraphNode neighbour){
			return this.neighbours.contains(neighbour);
		}
		
		public GraphNode get(int i){
			return this.neighbours.get(i);
		}
		
		public GraphNode[] getAll(){
			return this.neighbours.toArray(new GraphNode[this.neighbours.size()]);
		}
		
		public int size(){
			return this.neighbours.size();
		}
		
		public void setRelationship(String type, GraphNode neighbour){			
			if(this.neighbours.contains(neighbour)
					&& neighbour.neighbours.contains(node)){
				relationships.put(neighbour.getId(), type);
				neighbour.neighbours.relationships.put(node.getId(), type);
			}
		}

		public String getRelationship(GraphNode neighbour){			
			return relationships.get(neighbour.getId());
		}
		
		public double getDistance(GraphNode neighbour){
			
			if(this.neighbours.contains(neighbour) == false){
				return Double.NaN;
			}
			
			double e1_lat = Math.toRadians(node.getLat());
			double e1_lon =  Math.toRadians(node.getLon());

			
			double e2_lat = Math.toRadians(neighbour.getLat());
			double e2_lon =  Math.toRadians(neighbour.getLon());
			
			double distance = 6378.388 * Math.acos(Math.sin(e1_lat) * Math.sin(e2_lat) + Math.cos(e1_lat) * Math.cos(e2_lat) * Math.cos(e2_lon - e1_lon));		
		
			return Math.round(distance*1000)/1000.0; 
		}
	}
}
