import glob

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def main():
    incentives_analysis()


def plot_grouping_time(df, file_name, scala, path):
    sns.set_style("white")
    plt.figure(figsize=(8, 5))
    df.reset_index(inplace=True)
    g = sns.lineplot(x="vehicle_set_size", y="incentive_time", markers=True, data=df, marker="o")
    # g = sns.lineplot(x="vehicle_set_size", y="time", hue=group_by,  markers=True, data = df, hue_order=order_labels, marker="o")
    g.set(xlabel='Number of Vehicles', ylabel='Time in Seconds')

    # plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)

    if scala is "log":
        plt.yscale('log')

    plt.savefig(path + file_name + ".pdf")
    plt.clf()
    plt.close()


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)

    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def incentives_analysis():
    path = 'data/grouping'
    all_files = glob.glob(path + "/*.csv")
    # all_files = ['data/grouping/grid20_grouping100_300.csv']

    # define a quantile for the analysis. here e.g. 10 would mean, you get the lower 10 percent and top 10 percent;
    percentage_quantile = 10
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    joined_frame = pd.concat(li, axis=0, ignore_index=True)
    joined_frame = joined_frame.sort_values(by=['vehicle_set_size'], ascending=[1])
    # print(joined_frame)

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also

        joined_frame = joined_frame.replace(["AlphaCut", "GreedyBronKerbosch", "CPPOptimal", "SGVNS"],
                                            [r'\aalphacut', r'\agreedycpp', r'\aoptcpp', r'\asgvnscpp'])

        joined_grouped = joined_frame.groupby(['vehicle_set_size'])
        incentives = joined_grouped.agg({'incentive_time': ["mean", "median", "std", percentile(percentage_quantile),
                                                            percentile(100 - percentage_quantile)]})
        latex = incentives.to_latex(index=True)
        print(latex)

        groups_vehicle_sets = joined_frame.groupby(['vehicle_set_size', 'grouping'])

        names_of_labels = {"AlphaCut": r'\aalphacut', "GreedyBronKerbosch": r'\agreedycpp', "CPPOptimal": r'\aoptcpp',
                           "SGVNS": r'\asgvnscpp', "SingleGroup": r'\exactsolverk'}

        groups_stats = groups_vehicle_sets.agg(
            {'grouping_time': ["mean", "median", "std", percentile(percentage_quantile),
                               percentile(100 - percentage_quantile)]})

        latex = groups_stats.to_latex(index=True, escape=False)
        print(latex)

        # plot_grouping_time(groups_vehicle_sets, "incentives", "lin", "fig/general/")


if __name__ == "__main__":
    main()
