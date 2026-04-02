from experimentum.Storage.Migrations import Migration


class Partitioning(Migration):

    """Create the partitioning migration."""
    revision = '20190320141501'

    def up(self):
        """Run the migrations."""
        with self.schema.create('partitioning') as table:
            table.increments('id')
            table.primary('id')
            table.json('new_vehicles')
            table.float('incentives_time')
            table.float('grouping_time')
            table.integer('number_of_partitioned_vehicles')
            table.integer('number_of_new_created_vehicles')
            table.integer('algorithm_id')
            table.foreign('algorithm_id') \
                .references('id').on('algorithms') \
                .on_delete('cascade') \
                .on_update('cascade')

    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('partitioning')
