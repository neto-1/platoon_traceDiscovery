from experimentum.Storage.Migrations import Migration


class AddTestDataToTestCaseTable(Migration):

    """Create the add_test_data_to_test_case_table migration."""
    revision = '20181024112430'

    def up(self):
        """Run the migrations."""
        with self.schema.table('testcases') as table:
            table.float('avg_road_point_degree')
            table.integer('number_of_edges')
            table.integer('number_of_road_points')

    def down(self):
        """Revert the migrations."""
        with self.schema.table('testcases') as table:
            table.drop_column('avg_road_point_degree')
            table.drop_column('number_of_edges')
            table.drop_column('number_of_road_points')
