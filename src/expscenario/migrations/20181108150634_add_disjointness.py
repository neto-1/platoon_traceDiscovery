from experimentum.Storage.Migrations import Migration


class AddDisjointness(Migration):

    """Create the add_disjointness migration."""
    revision = '20181108150634'

    def up(self):
        """Run the migrations."""
        with self.schema.create('disjointness') as table:
            table.increments('id')
            table.primary('id')
            # table.array('group_ids', 'integer')
            # table.array('number_of_vehicles', 'integer')
            # table.array('objective_value', 'float')
            table.float('distance_savings')
            table.float('shortest_path_distances')
            table.float('savings')
            table.integer('algorithm_id')
            table.foreign('algorithm_id').references('id').on('algorithms').on_delete('cascade').on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('disjointness')
