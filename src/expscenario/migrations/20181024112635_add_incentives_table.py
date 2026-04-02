from experimentum.Storage.Migrations import Migration


class AddIncentivesTable(Migration):

    """Create the add_incentives_table migration."""
    revision = '20181024112635'

    def up(self):
        """Run the migrations."""
        with self.schema.create('incentives') as table:
            table.increments('id')
            table.primary('id')
            table.float('weight_factor')
            table.integer('algorithm_id')
            table.foreign('algorithm_id').references('id').on('algorithms').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('incentives')
