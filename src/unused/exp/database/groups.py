#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Group Model
"""
from __future__ import print_function
from .model import Model
from psycopg2.extras import Json


class Groups(Model):
    """
    Simple Group Model
    """
    def __init__(self, test_id, logging=True):
        """
        Create a new testcase
        :param logging: Enable/Disable logging
        """
        super(Groups, self).__init__(logging)
        self.test_id = test_id

    def create_group(self, data):
        """
        Create a group in a group set
        :param data: Group Data Object
        :return: returns group id
        """
        self.db.cursor.execute(
            """
            INSERT INTO Groups (
                id, test_id, group_set_id, parameter, vehicles,
                group_incentives, groups_shortest_path_sum
            )
            VALUES (
                %(id)s, %(test_id)s, %(group_set_id)s, %(parameter)s,
                %(vehicles)s, %(group_incentives)s, %(groups_shortest_path_sum)s
            )
            RETURNING id;
            """,
            self._merge(data, 'parameter')
        )
        
        group_id = self.db.cursor.fetchone()[0]
        self.db.conn.commit()
        self._log("Created Group '%s' and for Test ID '%s'" % (group_id, self.test_id))
        return group_id

    def create_group_set(self, data):
        """
        Create a group set
        :param data: Group Set Data Object
        :return: returns the group set id"
        """
        self.db.cursor.execute(
            """
            INSERT INTO Group_Sets (
                test_id, calculated_number_of_groups, vehicles_in_groups, vehicles_not_in_groups,
                successfull_groups, unsuccessfull_groups, group_savings, parameter
            )
            VALUES (
                %(test_id)s, %(calculated_number_of_groups)s, %(vehicles_in_groups)s,
                %(vehicles_not_in_groups)s, %(successfull_groups)s, %(unsuccessfull_groups)s,
                %(group_savings)s, %(parameter)s
            )
            RETURNING id;
            """,
            self._merge(data, 'parameter')
        )
        group_set_id = self.db.cursor.fetchone()[0]

        self.db.conn.commit()
        self._log("Created Group Set with ID '%s' for Test ID '%s'" % (group_set_id, self.test_id))

        return group_set_id

    # def create_groups_property(self, data):
    #     """
    #     Creates Groups Properties
    #     :param data: Group Properties Object
    #     """
    #     self.db.cursor.execute(
    #         """
    #         INSERT INTO Groups_Properties (test_id, algorithm, parameter)
    #         VALUES (%(test_id)s, %(algorithm)s, %(parameter)s)
    #         """,
    #         self._merge(data)
    #     )

    #     self.db.conn.commit()
    #     self._log("Created Group Properties for Test ID '%s'" % self.test_id)

    def create_routing(self, data):
        """
        Create routing for a group or test
        :param data: Group Properties Object
        """
        self.db.cursor.execute(
            """
            INSERT INTO Routing (test_id, group_id, savings, shortest_path, algorithm, parameter)
            VALUES (
                %(test_id)s, %(group_id)s, %(savings)s, %(shortest_path)s, %(algorithm)s, %(parameter)s
            )
            """,
            self._merge(data, 'parameter')
        )

        self.db.conn.commit()
        self._log(
            "Created Routing for Test ID '%s'" % self.test_id
        )

    def _merge(self, data, json_param = None):
        """
        Merge data with default value of test id and transform json if needed
        :param data: Data Dictionary
        :param json_param: param name of json object
        :return: merged data object
        """
        if json_param and json_param in data:
            data[json_param] = Json(data[json_param])

            # transform the key _degree_graph_ into object format if exists and rename to degree_graph
            # for key in data[json_param]:
            for key, val in data[json_param].items():
                if '_degree_graph_' in data[json_param][key]:
                    data[json_param][key]['degree_graph'] = { key: value for key, value in data[json_param][key]['_degree_graph_'] }
                    del data[json_param][key]['_degree_graph_']

        defaults = { 'test_id': self.test_id }
        defaults.update(data)

        return defaults
