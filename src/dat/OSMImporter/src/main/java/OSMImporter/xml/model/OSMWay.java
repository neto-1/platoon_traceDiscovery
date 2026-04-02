package OSMImporter.xml.model;

import java.util.LinkedList;
import java.util.List;

public class OSMWay extends OSMElement{

	public final List<Long> nd_ref = new LinkedList<Long>();
	
	public OSMWay(long id) {
		super(id);
	}
	
}
