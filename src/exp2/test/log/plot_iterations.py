import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def main():
    plot()


def plot():
    # read_log_files = ['log/ilp_routing/iter20_31132_18-12-2019_14-34-59_255384.csv']

    # path_log_files = 'log/ilp_grouping/'
    path_log_files = 'log/store/grid30_200/'

    read_log_files = ['grid30_200_cg']
    path = 'log/log_fig/'

    for filename in read_log_files:
        df = pd.read_csv(path_log_files + filename + '.csv', index_col=None, header=0)
        print(df)
        # df = df.loc[df['obj'] >= 0]

        sns.set_style("white")
        plt.figure(figsize=(8, 5))
        g = sns.lineplot(x="overall_time", y="obj", markers=True, data=df)

        plt.savefig(path + filename + ".pdf")
        plt.clf()
        plt.close()


if __name__ == "__main__":
    main()
