from experimentum.Storage.Migrations import Migration


class AddShortestPathSavingsColumn(Migration):

    """Create the add_shortest_path_savings_column migration."""
    revision = '20190530130009'

    def up(self):
        with self.schema.table('test_results') as table:
            table.float('shortest_path_savings')

    def down(self):
        with self.schema.table('test_results') as table:
            table.drop_column('shortest_path_savings')
