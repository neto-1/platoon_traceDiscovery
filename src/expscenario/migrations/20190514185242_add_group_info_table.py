from experimentum.Storage.Migrations import Migration


class AddGroupInfoTable(Migration):

    """Create the add_group_info_table migration."""
    revision = '20190514185242'

    def up(self):
        """Run the migrations."""
        with self.schema.create('group_info') as table:
            table.increments('id')
            table.primary('id')
            table.integer('grouping_id')
            table.foreign('grouping_id').references('id').on('grouping').on_delete('cascade').on_update('cascade')
            table.integer("group_id_neo")
            table.float("incentives_avg")
            table.float("angle_incentives_avg")
            table.float("median_incentives_avg")
            table.float("hull_incentives_avg")
            table.integer("group_edges")
            table.integer("group_nodes")
            table.integer("number_of_vehicles")
            table.array("group_polygon_coords", 'float')
            table.float("group_polygon_area")
            table.array("group_polygon_non_convex_coords", 'float')
            table.float("group_polygon_non_convex_area")


    def down(self):
        """Revert the migrations."""
        self.schema.drop_if_exists('group_info')
