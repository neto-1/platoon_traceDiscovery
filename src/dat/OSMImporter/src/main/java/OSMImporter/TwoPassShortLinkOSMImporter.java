package OSMImporter;

public class TwoPassShortLinkOSMImporter extends TwoPassOSMImporter {

	public TwoPassShortLinkOSMImporter(String uri, String username, String password) {
		super(uri, username, password);
		this.removeArtefacts = false;
		this.optimize = false;
	}

	@Override
	protected void optimize() {
		throw new UnsupportedOperationException();
	}

	@Override
	protected void removeArtefacts() {
		throw new UnsupportedOperationException();
	}

	@Override
	protected void commit(int tx_limit) {
		super.commit(tx_limit);
		
		// Hier Optimize
		
		
	}
	
	
}
