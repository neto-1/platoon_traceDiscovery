from experimentum.Storage import AbstractRepository
from repositories.GroupInfoRepository import GroupInfoRepository

class GroupingRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'grouping'
    # __relationships__ = {
    # }
    __relationships__ = {
        'group_info': [GroupInfoRepository]
    }

    def __init__(self, number):
        """Set attributes."""
        self.number = number