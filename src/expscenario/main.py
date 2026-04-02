# -*- coding: utf-8 -*-
from __future__ import print_function
from experimentum.Experiments import App
import os, sys, csv
from datetime import datetime
import pandas as pd
from typing import List, Dict
sys.path.insert(0, os.path.abspath('/Users/dmitry/Documents/wd/platooning/src/exp2'))
# sys.path.insert(0, os.path.abspath('/home/db-admin/platooning/src/exp2'))

class Platooning(App):

    """Main Entry Point of the Framework.

    Args:
        config_path (str): Defaults to '.'. Path to config files
    """
    config_path = 'config'

    def register_commands(self):
        """Register Custom Commands.

        Returns:
            dict: { Name of command : Command Handler }
        """


        from experimentum.Commands import command
        from termcolor import colored

        @command(
            'Return savings by experiment ids.',
            arguments={
                'path': {
                    'type': str, 'action': 'store', 'help': 'Path to the list with experiment ids.'
                }
            },
            help='Display results for all experiments'
        )
        def get_savings(app, args):
            df = pd.read_csv(args.path, index_col=None, header=0)
            experiment_repository = app.repositories.get('ExperimentRepository')
            experiment_objects = experiment_repository.all()

            experiments = []
            for experiment in experiment_objects:
                if experiment.id in df['id'].values:
                    experiments.append(experiment)

            Platooning.retrieve_experiments(experiments, app)


        @command(
            'Displays between one and ten lorem ipsum sentences.',
            arguments={
                'experiments_since': {
                    'type': str, 'action': 'store', 'help': 'Retrieve experiments after entered date in following format 01-10-2019.'
                }
            },
            help='Display results for all experiments'
        )
        def experiment_date(app, args):
            """ Test Actions for data querying """
            experiment_repository = app.repositories.get('ExperimentRepository')
            experiments = experiment_repository.get(where=['start', '>', args.experiments_since])
            Platooning.retrieve_experiments(experiments, app)

        @command(
            'Displays between one and ten lorem ipsum sentences.',
            arguments={
                'experiment_id': {
                    'type': str, 'action': 'store', 'help': 'Retrieve experiments after entered date in following format 01-10-2019.'
                }
            },
            help='Display results for all experiments'
        )
        def experiment_id(app, args):
            """ Test Actions for data querying """
            experiment_repository = app.repositories.get('ExperimentRepository')
            experiments = experiment_repository.get(where=['id', args.experiment_id])
            Platooning.retrieve_experiments(experiments, app)
        return {
            'results_date': experiment_date,
            'results_id': experiment_id,
            'results_csv_ids': get_savings
        }

    @staticmethod
    def build_csv_from_results(results:List[Dict], file_name: str):
        if len(results) > 0:
            keys = list(results[0].keys())
            with open(file_name, 'w') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)
            output_file.close()
        else:
            print(" No results are available!")

    @staticmethod
    def retrieve_experiments(experiments, app):
        test_case_repository = app.repositories.get('TestCaseRepository')
        test_result_repository = app.repositories.get('TestResultRepository')
        algorithms_repository = app.repositories.get('AlgorithmsRepository')
        incentives_repository = app.repositories.get('IncentivesRepository')
        disjointness_repository = app.repositories.get('DisjointnessRepository')
        grouping_repository = app.repositories.get('GroupingRepository')
        group_info_repository = app.repositories.get('GroupInfoRepository')
        routing_repository = app.repositories.get('RoutingRepository')

        print("* Retrieved the data from repositories.")

        results = []
        for experiment in experiments:
            test_cases = test_case_repository.get(where=['experiment_id', experiment.id])
            print("*-* Experiment started at:", experiment.start)
            for test_case in test_cases:
                test_results = test_result_repository.get(where=['test_id', test_case.id])

                for test_result in test_results:
                    test_case_info = {}

                    test_case_info["id"] = experiment.id
                    test_case_info["id_ts"] = test_case.id

                    # test_case_info["test_case_id"] = test_case.id
                    test_case_info["edges"] = test_case.number_of_edges
                    test_case_info["road_points"] = test_case.number_of_road_points

                    # test_case_info["test_result_id"] = test_result.id
                    test_case_info["vehicle_set_size"] = test_result.vehicle_set_size
                    test_case_info["vehicle_set_type"] = test_result.vehicle_set_type
                    # test_case_info["shortest_path_savings"] = test_result.shortest_path_savings

                    test_case_time = 0
                    algorithms = algorithms_repository.get(where=['test_result_id', test_result.id])

                    test_case_info["incentive_time"] = 0
                    test_case_info["incentive_parameter"] = ""

                    for algorithm in algorithms:
                        test_case_time = algorithm.calculation_time + test_case_time
                        incentives = incentives_repository.get(where=['algorithm_id', algorithm.id])

                        for incentive in incentives:
                            # test_case_info["incentive_method"] = algorithm.method
                            test_case_info["incentive_time"] = algorithm.calculation_time + test_case_info[
                                "incentive_time"]

                            if algorithm.method == "AngleIncentive":
                                test_case_info["incentive_parameter"] = "AI" + str(incentive.weight_factor)
                            if algorithm.method == "MedianIncentive":
                                test_case_info["incentive_parameter"] = test_case_info[
                                                                            "incentive_parameter"] + " MI" + str(
                                    incentive.weight_factor)
                            if algorithm.method == "HullIncentive":
                                test_case_info["incentive_parameter"] = test_case_info[
                                                                            "incentive_parameter"] + " HI" + str(
                                    incentive.weight_factor)

                        grouping = grouping_repository.get(where=['algorithm_id', algorithm.id])
                        for group in grouping:
                            test_case_info["grouping"] = algorithm.method
                            test_case_info["group_size"] = group.number
                            # test_case_info["size_per_group"] = [group_inf.number_of_vehicles for group_inf in group_info_repository.get(where=['grouping_id', group.id])]
                            test_case_info["grouping_time"] = algorithm.calculation_time
                            test_case_info["penalty"] = algorithm.parameters["penalty_factor"]
                            # test_case_info["penalty_value"] = -1 * (test_result.vehicle_set_size * test_result.vehicle_set_size * algorithm.parameters["penalty_factor"]) / 50
                            test_case_info["threshold"] = algorithm.parameters["incentive_threshold"]

                            if algorithm.method == "SingleGroup":
                                test_case_time = test_case_time - test_case_info["incentive_time"]

                        disjointness = disjointness_repository.get(where=['algorithm_id', algorithm.id])
                        for dis in disjointness:
                            # test_case_info["distance_savings"] = dis.distance_savings * 100
                            test_case_info["savings"] = dis.savings
                            test_case_info["opt_savings"] = dis.optimized_savings
                            test_case_info["spontaneous_platooning_savings"] = 100 * (dis.shortest_path_distances - test_result.shortest_path_savings) / dis.shortest_path_distances
                            # test_case_info["dif_savings"] = test_case_info["savings"] - (test_case_info["spontaneous_platooning_savings"] / (test_case_info["savings"] / 100))

                            # test_case_info["distance_savings"] = dis.distance_savings
                            # test_case_info["shortest_path_distances"] = dis.shortest_path_distances

                        routing = routing_repository.get(where=['algorithm_id', algorithm.id])
                        for route in routing:
                            test_case_info["routing"] = algorithm.method
                            test_case_info["routing_time"] = algorithm.calculation_time

                    test_case_info["time"] = test_case_time
                    test_case_info["start_at"] = experiment.start.strftime("%b %d %Y %H:%M:%S")

                    results.append(test_case_info)

        print("* Extracted the data from repository objects.")

        Platooning.build_csv_from_results(results, 'results.csv')

if __name__ == '__main__':
    app = Platooning('platooning', __file__)
    app.run()
