package OSMImporterV2.filter;

import java.util.List;

import OSMImporterV2.filter.model.PrimaryKey;

public interface IConfiguration {

	public List<PrimaryKey> getRules(String name);
	public void setRule(PrimaryKey value);
	public boolean contains(String name);
	
	public void setBoundaryAdmin_Level(int level);
	public int getBoundaryAdmin_Level();
	
}
