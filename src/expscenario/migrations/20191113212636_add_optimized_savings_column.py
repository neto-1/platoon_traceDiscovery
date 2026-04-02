from experimentum.Storage.Migrations import Migration


class AddOptimizedSavingsColumn(Migration):

    """Create the add_optimized_savings_column migration."""
    revision = '20191113212636'

    def up(self):
        with self.schema.table('disjointness') as table:
            table.float('optimized_savings')

    def down(self):
        with self.schema.table('disjointness') as table:
            table.drop_column('optimized_savings')
