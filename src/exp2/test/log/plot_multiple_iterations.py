import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def main():
    plot()
    plot_simplex()


def plot():
    path_log_files = '/Users/dmitry/Documents/wd/platooning/src/exp2/test/log/store/grid30_200/'
    path_log_figure = '/Users/dmitry/Documents/wd/platooning/src/exp2/test/log/log_fig/'

    test_cases = [[{'grid30_200_cg': 'Column Generation'}, {'grid30_200_simplex': 'Best Bound'},
                   {'grid30_200_optimal': 'Optimal Solution'}]]

    marker = ['grid30_200_marker']
    path = 'log/log_fig/'

    for test_case in test_cases:
        concat_instances = []
        for case in test_case:
            for file_name, value in case.items():
                full_path = path_log_files + file_name + '.csv'
                df = pd.read_csv(full_path, index_col=None, header=0)
                df = df.loc[df['Objective'] >= 0]
                df['Type'] = value

                reduced_df = df[['Time', 'Objective', 'Type']]
                concat_instances.append(reduced_df)

        full_instance = pd.concat(concat_instances, axis=0, ignore_index=True)
        full_instance = full_instance.loc[full_instance['Time'] >= 0]
        full_instance = full_instance.loc[full_instance['Objective'] >= 210000000]

        # names_of_labels = {"Time": r'Time(s)'}
        # full_instance = full_instance.rename(columns=names_of_labels)

        sns.set_style("white")
        plt.figure(figsize=(10, 6))
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

        # plt.ticklabel_format(useOffset=False)
        # plt.ticklabel_format(style='plain')
        plt.yticks(np.arange(0, full_instance["Objective"].max() + 1e6, step=1000000))

        g = sns.lineplot(x="Time", y="Objective", hue="Type", markers=True, data=full_instance)

        file_name = 'grid30_200_marker'
        full_path = path_log_files + file_name + '.csv'
        markers_df = pd.read_csv(full_path, index_col=None, header=0)

        for row in markers_df.iterrows():
            row_data = row[1]
            objective = row_data['Objective']
            time = row_data['Time']
            description = row_data[2]
            color = row_data[4]
            label_x = row_data[5]
            label_y = row_data[6]
            side = row_data[7]

            plt.annotate(description, xy=(time, objective), xycoords='data',
                         xytext=(label_x, label_y), textcoords='offset points',
                         size=12, ha=side, va="center",
                         bbox=dict(boxstyle="round", alpha=0.2, fc=color),
                         arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.2, fc=color))

        plt.savefig(path_log_figure + 'grid30_200' + ".pdf")
        plt.clf()
        plt.close()


def plot_simplex():
    violet = '#9366bd'
    red = '#d62829'
    green = '#2da02d'
    orange = '#ff800f'
    blue = '#2077b4'

    colors = [orange, green]
    sns.set_palette(sns.color_palette(colors))

    path_log_files = '/Users/dmitry/Documents/wd/platooning/src/exp2/test/log/store/grid30_200/'
    path_log_figure = '/Users/dmitry/Documents/wd/platooning/src/exp2/test/log/log_fig/'

    test_cases = [[{'grid30_200_simplex': 'Simplex Solver'}, {'grid30_200_optimal': 'Optimal Solution'}]]

    marker = ['grid30_200_marker']
    path = 'log/log_fig/'

    for test_case in test_cases:
        concat_instances = []
        for case in test_case:
            for file_name, value in case.items():
                full_path = path_log_files + file_name + '.csv'
                df = pd.read_csv(full_path, index_col=None, header=0)
                df = df.loc[df['Objective'] >= 0]
                df['Type'] = value

                reduced_df = df[['Time', 'Objective', 'Type']]
                concat_instances.append(reduced_df)

        full_instance = pd.concat(concat_instances, axis=0, ignore_index=True)
        full_instance = full_instance.loc[full_instance['Time'] >= 0]
        full_instance = full_instance.loc[full_instance['Objective'] >= 210000000]

        # names_of_labels = {"Time": r'Time(s)'}
        # full_instance = full_instance.rename(columns=names_of_labels)

        sns.set_style("white")
        plt.figure(figsize=(10, 4))
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

        # plt.ticklabel_format(useOffset=False)
        # plt.ticklabel_format(style='plain')
        plt.yticks(np.arange(0, full_instance["Objective"].max() + 1e6, step=1000000))

        g = sns.lineplot(x="Time", y="Objective", hue="Type", markers=True, data=full_instance)

        file_name = 'grid30_200_simplex_marker'
        full_path = path_log_files + file_name + '.csv'
        markers_df = pd.read_csv(full_path, index_col=None, header=0)

        for row in markers_df.iterrows():
            row_data = row[1]
            objective = row_data['Objective']
            time = row_data['Time']
            description = row_data[2]
            color = row_data[4]
            label_x = row_data[5]
            label_y = row_data[6]
            side = row_data[7]

            plt.annotate(description, xy=(time, objective), xycoords='data',
                         xytext=(label_x, label_y), textcoords='offset points',
                         size=12, ha=side, va="center",
                         bbox=dict(boxstyle="round", alpha=0.2, fc=color),
                         arrowprops=dict(arrowstyle="wedge,tail_width=0.5", alpha=0.2, fc=color))

        plt.savefig(path_log_figure + 'grid30_200' + "_simplex.pdf")
        plt.clf()
        plt.close()


if __name__ == "__main__":
    main()
