package OSMImporterV2.einlesen.model;

import java.util.LinkedList;
import java.util.List;

public class OSMNode extends OSMElement{
	private float lat;
	private float lon;
	
	public final List<OSMNode> neighbours = new LinkedList<OSMNode>();
	
	public OSMNode(long id, float lat, float lon) {
		super(id);
		this.lat = lat;
		this.lon = lon;
	}

	public float getLat() {
		return lat;
	}

	public void setLat(float lat) {
		this.lat = lat;
	}

	public float getLon() {
		return lon;
	}

	public void setLon(float lon) {
		this.lon = lon;
	}

	@Override
	public void putAllAttributes(OSMElement n) {
		super.putAllAttributes(n);
		
		if(n instanceof OSMNode){ //Gnerics waeren wohl auch toll
		
			this.lat = ((OSMNode)n).lat;
			this.lon = ((OSMNode)n).lon;
			
		}
	}	
}
