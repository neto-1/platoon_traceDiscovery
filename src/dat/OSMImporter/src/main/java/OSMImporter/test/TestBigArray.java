package OSMImporter.test;

public class TestBigArray {

	public static void main(String[] args) throws InterruptedException {
		// TODO Auto-generated method stub

		long[] big = new long[1000000000];
		
		for(int i = 0; i<100000000;i++){
			big[i]=i;
			if(i%1000000==0){
				System.out.println(i);
			}
		}

		long start = System.currentTimeMillis();
		
		for(int i = 0; i<1000000000;i++){
			big[i]=big[i] + 123;
			if(i%1000000==0){
			}
		}
		
		long finish = System.currentTimeMillis() - start;
		
		System.out.println(finish + " ms");
		
		Thread.sleep(5000);
		
	}

}
