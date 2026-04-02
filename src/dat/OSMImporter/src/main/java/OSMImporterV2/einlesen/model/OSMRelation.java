package OSMImporterV2.einlesen.model;

import java.util.HashMap;
import java.util.Map;

public class OSMRelation extends OSMElement{

	public final Map<Long,String> member_ref = new HashMap<Long,String>();
	
	public OSMRelation(long id) {
		super(id);
	}
}
