from experimentum.Storage import AbstractRepository
import json

class IncentivesRepository(AbstractRepository.implementation):

    """Repository for the testcases table data."""
    __table__ = 'incentives'
    # __relationships__ = {
    # }

    def __init__(self, weight_factor):
        """Set attributes."""
        self.weight_factor = weight_factor