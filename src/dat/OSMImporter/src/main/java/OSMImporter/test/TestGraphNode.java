package OSMImporter.test;

import OSMImporter.model.GraphNode;

public class TestGraphNode {

	public static void main(String[] args) {
	
		GraphNode n1 = new GraphNode(1);
		GraphNode n2 = new GraphNode(2);
		GraphNode n3 = new GraphNode(3);
		
		n1.neighbours.add(n2);
		n2.neighbours.add(n1);
		
		n3.neighbours.add(n2);
		
		System.out.println(n2.neighbours.contains(n1));
		
		System.out.println(n1.neighbours.size());
		System.out.println(n2.neighbours.size());
		
		GraphNode n4 = n1.neighbours.get(0);
		System.out.println("N4: " + n4.getId());
		
		n1.neighbours.remove(n4);
		
		System.out.println(n1.neighbours.size());
		System.out.println(n2.neighbours.size());
		
		GraphNode n5 = new GraphNode(3);
		System.out.println(n3.equals(n5));
		
//		n2.neighbours.setRelationship("Hallo", n1);
//		
//		System.out.println(n2.neighbours.getRelationship(n1));
//		System.out.println(n1.neighbours.getRelationship(n2));

	}

}
