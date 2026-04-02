from experimentum.Storage.Migrations import Migration


class AddRoutingTable(Migration):

    """Create the add_routing_table migration."""
    revision = '20181024112647'

    def up(self):
        """Run the migrations."""
        with self.schema.create('routing') as table:
            table.increments('id')
            table.primary('id')
            table.array('group_ids', 'integer')
            table.array('number_of_vehicles', 'integer')
            table.array('objective_value', 'float')
            table.integer('algorithm_id')
            table.foreign('algorithm_id').references('id').on('algorithms').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('routing')
