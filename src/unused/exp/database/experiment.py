#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Experiment Model
"""
from __future__ import print_function
from .model import Model
from .testcase import TestCase


class Experiment(Model):
    """
    Simple Experiment Model
    """
    def __init__(self, logging=True):
        """
        Init database connection
        :param logging: Enable/Disable logging
        """
        super(Experiment, self).__init__(logging)
        self.experiment_id = None

        self.start()

    def start(self):
        """
        Start an experiment
        :return: returns the experiment id
        """
        self.db.cursor.execute("""
            INSERT INTO Experiments (db_user, started_at)
            VALUES((SELECT current_user LIMIT 1), now())
            RETURNING id;
        """)

        self.experiment_id = self.db.cursor.fetchone()[0]
        self.db.conn.commit()

        self._log("Created Experiment with ID '%s'" % self.experiment_id)

        return self.experiment_id

    def end(self):
        """ End an experiment and dump database to file """
        self.db.cursor.execute(
            "UPDATE Experiments SET finished_at = now() WHERE id = %s",
            (self.experiment_id,)
        )
        self.db.conn.commit()
        self._log("Finished Experiment with ID '%s'" % self.experiment_id)

    def create_test(self, data):
        """
        Create a testcase
        :return Testcase: returns the created testcase 
        """
        test = TestCase(self.experiment_id, self.logging)
        test.create(data)

        return test
    