package OSMImporterV2.filter;

public class Builder {

	public static Builder instance = new Builder();
	
	public IConfiguration buildConfiguration(){
		return new DefaultConfiguration();
	}
}
