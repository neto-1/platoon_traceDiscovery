from experimentum.Storage.Migrations import Migration


class AddSelectedGroupColumn(Migration):

    """Create the add_selected_group_column migration."""
    revision = '20190531144807'

    def up(self):
        with self.schema.table('group_info') as table:
            table.boolean('selected')

    def down(self):
        with self.schema.table('group_info') as table:
            table.drop_column('selected')
