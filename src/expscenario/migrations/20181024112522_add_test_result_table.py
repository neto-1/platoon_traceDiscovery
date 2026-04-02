from experimentum.Storage.Migrations import Migration


class AddTestResultTable(Migration):

    """Create the add_test_result_table migration."""
    revision = '20181024112522'

    def up(self):
        """Run the migrations."""
        with self.schema.create('test_results') as table:
            table.increments('id')
            table.primary('id')
            table.float('saving_factor')
            table.string('vehicle_set_type')
            table.integer('vehicle_set_size')
            table.integer('test_id')
            table.foreign('test_id').references('id').on('testcases').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('test_results')
