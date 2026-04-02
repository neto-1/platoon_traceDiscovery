#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from database import Experiment
import platform
import random


def main():

    """ Test Database models """
    # start experiment
    # pgdbname: platoon
    # pgname: admin
    # pgpass: dbklm983§
    # pghost: 139.174.101.107
    exp = Experiment(True)

    # simulate different test cases
    for i in range(1, 3):
        
        # simulate test data
        veh = [random.randint(1, 100), random.randint(1, 100)] # Neo4j vehicle id
        groups = [random.randint(1, 100), random.randint(1, 100)] # Neo4j vehicle id
        data = {
            'test': {
                'vehicle_set_id': i,                # TODO
                'number_of_edges': 100 * i,         # TODO
                'number_of_vehicles': 10 * i,       # TODO
                'number_of_groups': 30 * i,         # TODO
                'enable_grouping': True,            # TODO
                'identify_group_by': 'greedy',      # TODO
                'distribution': 'normal',           # TODO
                'database': 'saarland_simple',      # TODO
                'longest_shortest_path': 13.37 * i, # TODO
                'shortest_path_total': 12.34 * i,   # TODO
            },
            'group_set': {
                'calculated_number_of_groups': 10 * i,  # TODO
                'vehicles_in_groups': 20 * i,           # TODO
                'vehicles_not_in_groups': 30 * i,       # TODO
                'successfull_groups': 40 * i,           # TODO
                'unsuccessfull_groups': 50 * i,         # TODO
                'group_savings': 12.34 * i,             # TODO
                'parameter': { 'foo': 'bar' },          # TODO
            },
            'times': {
                'init_considered_set': 12.34 * i,           # TODO
                'init_total': 56.78 * i,                    # TODO
                'creating_incentives': 90.12 * i,           # TODO
                'creating_groups': 34.56 * i,               # TODO
                'storing_routes': 34.56 * i,                # TODO
                'calc_group_savings': 67.89 * i,            # TODO
                'determine_disjunct_groups': 12.34 * i,     # TODO
                'storing_incentives': 90.12 * i,            # TODO
                'storing_groups': 34.56 * i,                # TODO
                'routing': 90.12 * i                        # TODO
            },
            'slicing': [
                {
                    'vehicles': veh,                    # TODO
                    'parameter': [1, 2 * i, 3, 4 * i],  # TODO
                    'method': 'greedy',                 # TODO
                    'slices': 2                         # TODO
                }
            ],
            'vehicles': [
                {
                    'id': veh[0],
                    'shortest_path': [1, 2],            # TODO
                    'shortest_path_value': 12.34 * i,   # TODO
                    'platoon_path_value': 56.78 * i,    # TODO
                    'platoon_path': [3, 4]              # TODO
                },
                {
                    'id': veh[1],
                    'shortest_path': [1, 2],            # TODO
                    'shortest_path_value': 12.34 * i,   # TODO
                    'platoon_path_value': 56.78 * i,    # TODO
                    'platoon_path': [3, 4]              # TODO
                },
            ],
            'incentives': [{
                'vehicles': veh,                # TODO
                'incentives': [0, 1.2 * i, 3.4 * i], # TODO
                'criteria': { 'a': 100, 'b': [1,2,3], 'c': {'foo': 'bar'}, 'd': False } # TODO
            }],
            'groups': [
                {
                    'id': groups[0],                        # TODO
                    'vehicles': veh,                        # TODO
                    'parameter': {'alpha_cut': 1.2 * i },   # TODO
                    'groups_shortest_path_sum': 91.23 * i,  # TODO
                    'group_incentives': [1.1 * i, 2.2 * i]  # TODO
                },
                {
                    'id': groups[1],                        # TODO
                    'vehicles': veh,                        # TODO
                    'parameter': {'alpha_cut': 3.4 * i },   # TODO
                    'groups_shortest_path_sum': 91.23 * i,  # TODO
                    'group_incentives': [1.1 * i, 2.2 * i]  # TODO
                }
            ],
            'routing': [
                {
                    'group_id': groups[0],      # TODO
                    'savings': 12.34 * i,       # TODO
                    'shortest_path': 56.78 * i, # TODO
                    'algorithm': 'greedy',      # TODO
                    'parameter': None,          # TODO
                },
                {
                    'group_id': groups[1],          # TODO
                    'savings': 12.34,               # TODO
                    'shortest_path': 56.78,         # TODO
                    'algorithm': 'greedy',          # TODO
                    'parameter': { 'a': [1,2,3] }   # TODO
                },
            ]
        }

        test = exp.create_test(data['test'])
        test.create_vehicles(data['vehicles'], data['incentives'], data['slicing'])
        test.create_groups(data['group_set'], data['groups'], data['routing'])
        test.create_times(data['times'])

    # end experiment
    exp.end()

if __name__ == '__main__':
    main()
