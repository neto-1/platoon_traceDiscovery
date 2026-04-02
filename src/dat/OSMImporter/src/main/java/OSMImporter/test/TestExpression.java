package OSMImporter.test;

import OSMImporter.Expression.Expression;

public class TestExpression {

	public static void main(String[] args) {
		
		
		Expression.start().feature("highway").value("highway").asProperty().optionalFeature("name").allValues().asRelation();

	}

}
