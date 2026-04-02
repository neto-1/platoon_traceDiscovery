package OSMImporter;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Map;

import org.apache.commons.io.FileUtils;

import OSMImporter.xml.model.OSMNode;
import OSMImporter.xml.model.OSMRelation;
import OSMImporter.xml.model.OSMWay;

public class WayExtractor extends AbstractOSMImporter {

	String outFile = "output.osm";
	FileOutputStream fos = null;
	FileChannel out = null;
	
	ByteBuffer bytebuf = null;
	
	int bufferSizeKB = 4;
	int bufferSize = bufferSizeKB*1024;
		
	@Override
	public void createNode(OSMNode n) {
		// TODO Auto-generated method stub

	}

	@Override
	public void createWay(OSMWay w) {
		// TODO Auto-generated method stub
		
		write("\t<way id=\""+w.getId()+"\" >\n");
		
		for(long id_ref : w.nd_ref)
			write("\t\t<nd ref=\""+id_ref+"\" />\n");
		
		for(Map.Entry<String, String> e : w.tag.entrySet())
				write("\t\t<tag k=\""+e.getKey()+"\" v=\""+e.getValue()
					.replaceAll("(&)", "&amp;")
					.replaceAll("(\")", "&quot;")
					.replaceAll("(')",  "&apos; ")
					.replaceAll("(<)", "&lt; ")
					.replaceAll("(<)", "&gt;")
					+"\" />\n");
		
		write("\t</way>\n");
	}

	@Override
	public void createRelation(OSMRelation r) {
		// TODO Auto-generated method stub

	}

	@Override
	public void init() {

		try {

			File yourFile = new File(outFile);
			fos = FileUtils.openOutputStream(yourFile);
			fos = new FileOutputStream(outFile,false);
			out = fos.getChannel();
			bytebuf = ByteBuffer.allocateDirect(bufferSize);
					
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
		write("<osm version=\"0.6\" generator=\"CGImap 0.0.2\">\n");

	}

	@Override
	public void shutdown() {
		
		write("</osm>\n");
		
		try {
			out.close();
			fos.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	private void write(String s){		      
        try {
        	
        	bytebuf = ByteBuffer.wrap(s.getBytes("UTF-8"));
        	
	    	//  while (bytebuf.hasRemaining()) { // Read data from file into ByteBuffer
	  //          bytebuf.flip();
	            out.write(bytebuf);
	    //        bytebuf.clear(); 
	        // }

		} catch (IOException e) {
			e.printStackTrace();
		}		
	}
	
	public String getOutputFile() {
		return outFile;
	}

	public void setOutputFile(String outputFile) {
		this.outFile = outputFile;
	}
}
