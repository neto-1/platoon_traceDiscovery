package OSMImporter.xml;

import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public interface OSMHandler {

	public void createNode(OSMNode n);
	
	public void createWay(OSMWay w);
	
	public void createRelation(OSMRelation r);
	
}
