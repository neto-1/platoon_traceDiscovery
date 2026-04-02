package OSMImporter.xml.model;

import java.util.LinkedList;
import java.util.List;

public class OSMRelation extends OSMElement{

	public final List<Long> member_ref = new LinkedList<Long>();
	
	public OSMRelation(long id) {
		super(id);
	}
}
