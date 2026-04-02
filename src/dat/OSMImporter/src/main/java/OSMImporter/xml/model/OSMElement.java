package OSMImporter.xml.model;

import java.util.HashMap;
import java.util.Map;

public class OSMElement {
	private long id;
	
	public final Map<String,String> tag = new HashMap<String,String>();
	
	public OSMElement(long id) {
		super();
		this.id = id;
	}

	public long getId() {
		return id;
	}

	public void setId(long id) {
		this.id = id;
	}
	
	public void putAllAttributes(OSMElement n){
		this.tag.putAll(n.tag);
	}

	@Override
	public boolean equals(Object arg0) {

		if(!(arg0 instanceof OSMElement)){
			return false;
		}
		
		return this.id == ((OSMElement)arg0).id;
	}
}
