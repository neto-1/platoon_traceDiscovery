package OSMImporterV2.einlesen;

import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;

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
