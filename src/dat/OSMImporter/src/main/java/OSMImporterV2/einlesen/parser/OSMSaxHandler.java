package OSMImporterV2.einlesen.parser;

import org.xml.sax.Attributes;
import org.xml.sax.SAXException;
import org.xml.sax.helpers.DefaultHandler;

import OSMImporterV2.einlesen.Factory;
import OSMImporterV2.einlesen.OSMHandler;
import OSMImporterV2.einlesen.model.OSMElement;
import OSMImporterV2.einlesen.model.OSMNode;
import OSMImporterV2.einlesen.model.OSMRelation;
import OSMImporterV2.einlesen.model.OSMWay;

public class OSMSaxHandler extends DefaultHandler {
	
	private OSMSaxHelper saxHelper = OSMSaxHelper.instance;
	private Factory factory = Factory.instance;
	
	private OSMHandler handler = null;
			
	public OSMSaxHandler(OSMHandler handler) {
		super();
		this.handler = handler;
	}

	public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException {

		if (qName.equals("node")) {
			_startNode(uri, localName, qName, attributes);
		}else if(qName.equals("tag")){
			_startTag(uri, localName, qName, attributes);	
		}else if(qName.equals("way")){
			_startWay(uri, localName, qName, attributes);	
		}else if(qName.equals("nd")){
			_startNd(uri, localName, qName, attributes);	
		}else if(qName.equals("relation")){
			_startRelation(uri, localName, qName, attributes);	
		}else if(qName.equals("member")){
			_startMember(uri, localName, qName, attributes);	
		}
		
	}

	public void endElement(String uri, String localName, String qName) throws SAXException {

		if (qName.equals("node")) {
			_endNode(uri, localName, qName);
		}else if(qName.equals("tag")){
			_endTag(uri, localName, qName);	
		}else if(qName.equals("way")){
			_endWay(uri, localName, qName);	
		}else if(qName.equals("nd")){
			_endNd(uri, localName, qName);	
		}else if(qName.equals("relation")){
			_endRelation(uri, localName, qName);	
		}else if(qName.equals("member")){
			_endMember(uri, localName, qName);	
		}
		
	}

	public void characters(char ch[], int start, int length) throws SAXException {

	}
	
	private OSMElement element = null;
	
	private void _startNode(String uri, String localName, String qName, Attributes attributes) throws SAXException {
				
		element = factory.createNode(saxHelper.asLong(attributes, "id"), saxHelper.asFloat(attributes, "lat"), 
				saxHelper.asFloat(attributes, "lon"));
	
	}

	private void _endNode(String uri, String localName, String qName) throws SAXException {

		handler.createNode((OSMNode) element);
		
	}
	
	private void _startWay(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		
		element = factory.createWay(saxHelper.asLong(attributes, "id"));
		
	}
	
	private void _endWay(String uri, String localName, String qName) throws SAXException {
		
		handler.createWay((OSMWay) element);
		
	}
	
	private void _startTag(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		
		element.tag.put(saxHelper.asString(attributes, "k"), saxHelper.asString(attributes, "v"));
	}
		
	private void _endTag(String uri, String localName, String qName) throws SAXException {
		
	}
	
	private void _startNd(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		
		((OSMWay)element).nd_ref.add(saxHelper.asLong(attributes, "ref"));
		
	}
	
	private void _endNd(String uri, String localName, String qName) throws SAXException {
		
	}
	
	private void _startRelation(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		
		element = factory.createRelation(saxHelper.asLong(attributes, "id"));
	
	}

	private void _endRelation(String uri, String localName, String qName) throws SAXException {

		handler.createRelation((OSMRelation) element);
		
	}

	
	private void _startMember(String uri, String localName, String qName, Attributes attributes) throws SAXException {
		
		((OSMRelation)element).member_ref.put(saxHelper.asLong(attributes, "ref"), saxHelper.asString(attributes, "type"));
		
	}
	
	private void _endMember(String uri, String localName, String qName) throws SAXException {
		
	}
}
