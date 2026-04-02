from experimentum.Storage.Migrations import Migration


class AddGroupingTable(Migration):

    """Create the add_grouping_table migration."""
    revision = '20181024112625'

    def up(self):
        """Run the migrations."""
        with self.schema.create('grouping') as table:
            table.increments('id')
            table.primary('id')
            table.integer('number')
            table.integer('algorithm_id')
            table.foreign('algorithm_id').references('id').on('algorithms').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('grouping')
