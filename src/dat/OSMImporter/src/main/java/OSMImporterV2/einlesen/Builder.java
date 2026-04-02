package OSMImporterV2.einlesen;

import java.io.BufferedInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;

import javax.xml.parsers.ParserConfigurationException;
import javax.xml.parsers.SAXParser;
import javax.xml.parsers.SAXParserFactory;

import org.apache.commons.compress.compressors.CompressorException;
import org.apache.commons.compress.compressors.CompressorInputStream;
import org.apache.commons.compress.compressors.CompressorStreamFactory;
import org.xml.sax.SAXException;

public class Builder {

	public static Builder instance = new Builder();
	
	public SAXParser buildSAXParser() throws ParserConfigurationException, SAXException{		
		SAXParserFactory factory = SAXParserFactory.newInstance();
		return factory.newSAXParser();
	}
	
	public CompressorInputStream buildCompressedFileReader(String fileIn) throws FileNotFoundException, CompressorException {
	    FileInputStream fin = new FileInputStream(fileIn);
	    BufferedInputStream bis = new BufferedInputStream(fin);
	    CompressorInputStream input = new CompressorStreamFactory().createCompressorInputStream(bis);
	    return input;
	}
	
}
