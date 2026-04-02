package OSMImporterV2.batch.run;

import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

public class Debug {

	public static void main(String[] args) {
		// TODO Auto-generated method stub

		List<String> l = new LinkedList<String>();
		
		l.add("Hallo");
		
		System.out.println(l.contains("Hallo"));
	
		Set<Integer> s = new TreeSet<Integer>();
		List<Integer> i = new LinkedList<Integer>();
		
		i.add(1);
		i.add(4);
		
		s.add(1);
		s.add(1);
		s.add(1);
		
		s.addAll(i);
		
		System.out.println(s.size());
		
		System.out.println(s.contains(6));
		
		Map<String,String> m = new HashMap<String,String>();
		
		m.put("ff", null);		
		System.out.println(m.get("ff"));
	
		m.put("ff", "wert");		
		System.out.println(m.get("ff"));
		
	}

}
