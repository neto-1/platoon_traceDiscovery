package OSMImporterV2.einlesen.parser;

import org.xml.sax.Attributes;

public class OSMSaxHelper {

	public static final OSMSaxHelper instance = new OSMSaxHelper();
	
	public long asLong(Attributes a, String qName){
		return Long.parseLong(a.getValue(qName));
	}
	
	public float asFloat(Attributes a, String qName){
		return Float.parseFloat(a.getValue(qName));
	}
	
	public boolean asBoolean(Attributes a, String qName){
		return Boolean.parseBoolean(a.getValue(qName));
	}
	
	public String asString(Attributes a, String qName){
		return a.getValue(qName);
	}
}
