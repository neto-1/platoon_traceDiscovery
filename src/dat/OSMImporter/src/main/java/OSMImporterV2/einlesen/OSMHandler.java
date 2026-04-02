package OSMImporterV2.einlesen;

import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;

public interface OSMHandler {

	public void createNode(OSMNode n);
	
	public void createWay(OSMWay w);
	
	public void createRelation(OSMRelation r);
	
}
