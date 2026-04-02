#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple Test Model
"""
from __future__ import print_function
import platform
from .model import Model
from .groups import Groups
from .vehicles import Vehicles


class TestCase(Model):
    """
    Simple Testcase Model
    """
    def __init__(self, experiment_id, logging=True):
        """
        Create a new testcase
        :param logging: Enable/Disable logging
        """
        super(TestCase, self).__init__(logging)
        self.experiment_id = experiment_id
        self.test_id = None

    def create(self, data):
        """
        Create a test case
        :param data: Test-Data object
        """
        # merge defaults and data
        defaults = {
            'experiment_id': self.experiment_id, 
            'machine': platform.processor()
        }
        defaults.update(data)

        # run query
        self.db.cursor.execute(
            """
            INSERT INTO Tests (
                experiment_id, vehicle_set_id, number_of_edges, number_of_vehicles, number_of_groups,
                enable_grouping, identify_group_by, distribution, database, longest_shortest_path,
                shortest_path_total, machine, db_user
            )
            VALUES (
                %(experiment_id)s, %(vehicle_set_id)s, %(number_of_edges)s, %(number_of_vehicles)s,
                %(number_of_groups)s, %(enable_grouping)s, %(identify_group_by)s, %(distribution)s,
                %(database)s, %(longest_shortest_path)s, %(shortest_path_total)s, %(machine)s,
                (SELECT current_user LIMIT 1)
            )
            RETURNING id;
            """,
            defaults
        )
        self.test_id = self.db.cursor.fetchone()[0]
        self.db.conn.commit()
        self._log("Created Test with ID '%s'" % self.test_id)

    def create_times(self, data):
        """
        Insert recored times for each test
        :param data: Test-Times data object
        """
        # merge defaults and data
        defaults = { 'test_id': self.test_id }
        defaults.update(data)

        # run query
        self.db.cursor.execute(
            """
            INSERT INTO Times (
                test_id, init_considered_set, init_total, creating_incentives, creating_groups,
                storing_routes, calc_group_savings, determine_disjunct_groups, routing,
                storing_incentives, storing_groups
            )
            VALUES (
                %(test_id)s, %(init_considered_set)s, %(init_total)s, %(creating_incentives)s,
                %(creating_groups)s, %(storing_routes)s, %(calc_group_savings)s,
                %(determine_disjunct_groups)s, %(routing)s, %(storing_incentives)s, %(storing_groups)s
            )
            """,
            defaults
        )

        self.db.conn.commit()
        self._log("Created Times for Test ID '%s'" % self.test_id)

    def create_vehicles(self, vehicle_data, incentive_data, slicing_data):
        """
        Insert vehicle data for each test
        :param vehicle_data: vehicles
        :param incentive_data: incentives
        :param slicing_data: slicings
        """
        vehicles = Vehicles(self.test_id, self.logging)

        # vehicle creation
        for vdata in vehicle_data:
            vid = vehicles.create_vehicle(vdata)

        # incentives creation
        for incentive in incentive_data:
            vehicles.create_incentives(incentive)

        # slicing creation
        for slicing in slicing_data:
            vehicles.create_slicing(slicing)

    def create_groups(self, group_set_data, group_data, routing_data):
        """
        Insert group data for each test
        :param group_set_data: group_sets
        :param group_data: groups
        :param routing_data: routings
        """
        groups = Groups(self.test_id, self.logging)

        # create group set
        group_set_id = groups.create_group_set(group_set_data)

        # create groups
        for data in group_data:
            data['group_set_id'] = group_set_id
            group_id = groups.create_group(data)
        
        # create routing
        for data in routing_data: 
            groups.create_routing(data)
