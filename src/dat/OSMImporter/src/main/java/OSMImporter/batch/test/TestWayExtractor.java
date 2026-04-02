package OSMImporter.batch.test;

import OSMImporter.WayExtractor;

public class TestWayExtractor {

	public static void main(String[] args) {
		
		WayExtractor we = new WayExtractor();
		
		//we.setOutputFile("C:\\tmp\\output.osm");
		we.setOutputFile("e:\\tmp\\output.osm");
		we.importFromFile("C:\\osm\\berlin-latest.xml");

	}

}
