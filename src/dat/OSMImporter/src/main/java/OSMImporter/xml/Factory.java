package OSMImporter.xml;

import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public class Factory {

	public static final Factory instance = new Factory();
	
	public OSMNode createNode(long id, float lat, float lon){
		return new OSMNode(id,lat,lon);
	}
	
	public OSMWay createWay(long id){
		return new OSMWay(id);
	}
	
	public OSMRelation createRelation(long id){
		return new OSMRelation(id);
	}
}
