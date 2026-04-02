from experimentum.Storage.Migrations import Migration

class AddAlgorithmsTable(Migration):

    """Create the add_algorithms_table migration."""
    revision = '20181024112545'

    def up(self):
        with self.schema.create('algorithms') as table:
            table.increments('id')
            table.primary('id')
            table.string('method')
            table.float('calculation_time')
            table.float('store_time')
            table.float('time')
            table.json('parameters').nullable()
            table.datetime('executed_at')
            table.integer('test_result_id')
            table.foreign('test_result_id').references('id').on('test_results').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('algorithms')


