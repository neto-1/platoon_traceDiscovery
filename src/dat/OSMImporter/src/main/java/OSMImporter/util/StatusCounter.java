package OSMImporter.util;

public class StatusCounter {

	private long value;
	private long steps;
	private String name;
	
	public StatusCounter(String name) {
		super();
		this.steps = 1;
		this.name = name;
	}
	
	public StatusCounter(long steps, String name) {
		super();
		this.steps = steps;
		this.name = name;
	}
	
	public StatusCounter increment(){	
		value++;
		return this;
	}
	
	public void _notify(){	
		if(value % steps == 0){
			System.out.println("StatusCounter [name=" + name +", value=" + value+ "]");
		}
	}
	
	public StatusCounter increment(long value){
		
		if(value < 1){ return this; }
		
		this.value+=value;
		return this;
	}
	
	public long getValue(){
		return value;
	}
	
	public String getName(){
		return name;
	}

	@Override
	public String toString() {
		return "StatusCounter [name=" + name +", value=" + value+ "]";
	}
	
}
