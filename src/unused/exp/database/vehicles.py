#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Vehicle Model
"""
from __future__ import print_function
from psycopg2.extras import Json
from .model import Model


class Vehicles(Model):
    """
    Simple Vehicle Model
    """
    def __init__(self, test_id, logging=True):
        """
        Create a new testcase
        :param logging: Enable/Disable logging
        """
        super(Vehicles, self).__init__(logging)
        self.test_id = test_id

    def create_slicing(self, data):
        """
        Create slicing for vehicles
        :param data: slicing data object
        :return: slicing id
        """
        self.db.cursor.execute(
            """
            INSERT INTO Slicing (test_id, method, slices, vehicles, parameter)
            VALUES (%(test_id)s, %(method)s, %(slices)s, %(vehicles)s, %(parameter)s)
            RETURNING id;
            """,
            self._merge(data, 'parameter')
        )

        slicing_id = self.db.cursor.fetchone()[0]
        self.db.conn.commit()
        self._log("Created Slicing with ID '%s' for Test ID '%s'" % (slicing_id, self.test_id))

        return slicing_id

    def create_incentives(self, data):
        """
        Create incentives for vehicles
        :param data: incentives data object
        :return: incentive id
        """
        data = self._merge(data, 'criteria')
        self.db.cursor.execute(
            """
            INSERT INTO Incentives (test_id, incentives, criteria, vehicles)
            VALUES (%(test_id)s, %(incentives)s, %(criteria)s, %(vehicles)s)
            RETURNING id;
            """,
            data
        )

        incentive_id = self.db.cursor.fetchone()[0]

        self.db.cursor.execute(
            """
            UPDATE Vehicles
            SET incentive_id = incentive_id || %(incentive_id)s
            WHERE test_id = %(test_id)s AND vehicle_id IN %(vehicles)s 
            """,
            {
                'incentive_id': incentive_id,
                'test_id': self.test_id,
                'vehicles': tuple(data['vehicles']) # Convert list to tuple (otherwise it won't work)
            }
        )

        self.db.conn.commit()
        self._log("Created Incentive with ID '%s' for Test ID '%s'" % (incentive_id, self.test_id))

        return incentive_id

    def create_vehicle(self, data):
        """
        Create a vehicle
        :param data: vehicles data object
        :return: returns created vehicle id
        """
        data = self._merge(data)
        data['incentive_id'] = data['incentive_id'] if 'incentive_id' in data else None

        self.db.cursor.execute(
            """
            INSERT INTO Vehicles (
                test_id, shortest_path, platoon_path, incentive_id,
                shortest_path_value, platoon_path_value, vehicle_id
            )
            VALUES (
                %(test_id)s, %(shortest_path)s, %(platoon_path)s, %(incentive_id)s,
                %(shortest_path_value)s, %(platoon_path_value)s, %(id)s
            )
            RETURNING id;
            """,
            data
        )

        vehicle_id = self.db.cursor.fetchone()[0]
        self.db.conn.commit()
        self._log("Created Vehicle with ID '%s' for Test ID '%s'" % (vehicle_id, self.test_id))

        return vehicle_id

    def _merge(self, data, json_param = None):
        """
        Merge data with default value of test id and transform json if needed
        :param data: Data Dictionary
        :param json_param: param name of json object
        :return: merged data object
        """
        if json_param and json_param in data:
            data[json_param] = Json(data[json_param])

        defaults = { 'test_id': self.test_id }        
        defaults.update(data)

        return defaults