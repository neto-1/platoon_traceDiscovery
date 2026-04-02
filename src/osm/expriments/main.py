import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt


def get_data_by_directory(path) -> pd.DataFrame:
    file_names = glob.glob(path + "/*.csv", recursive=True)
    files = []
    for file_name in file_names:
        file = pd.read_csv(file_name)
        files.append(file)
    full_instance = pd.concat(files, axis=0, ignore_index=True)
    return full_instance


def get_statistics(data: pd.DataFrame) -> pd.DataFrame:
    statistics = data.agg({'time': ["median", "mean", "std", "sum"]})
    return statistics

def main():
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1000)

    """ Germany """
    data_original_ger = get_data_by_directory('ger/original/')
    data_original_ger = data_original_ger.sort_values(by=['time'], ascending=[0])

    data_red_ger = get_data_by_directory('ger/reduced/')
    data_red_ger = data_red_ger.sort_values(by=['time'], ascending=[0])

    print(data_original_ger[['time', 'number_of_path_edges']])
    print(get_statistics(data_original_ger))

    """ Niedersachsen """
    data_original_nds = get_data_by_directory('nds/original/')
    data_original_nds = data_original_nds.sort_values(by=['time'], ascending=[0])

    data_red_nds = get_data_by_directory('nds/reduced/')
    data_red_nds = data_red_nds.sort_values(by=['time'], ascending=[0])

    """ Saarland """
    data_original_sl = get_data_by_directory('sl/original/')
    data_original_sl = data_original_sl.sort_values(by=['time'], ascending=[0])

    data_red_sl = get_data_by_directory('sl/reduced/')
    data_red_sl = data_red_sl.sort_values(by=['time'], ascending=[0])


    fig, axes = plt.subplots(3, 2, figsize=(15, 10))
    plot = sns.scatterplot(ax=axes[0, 1], x="number_of_path_edges", y="time", data=data_original_ger[['time', 'number_of_path_edges']])
    plot = sns.scatterplot(ax=axes[0, 0], x="number_of_path_edges", y="time", data=data_red_ger[['time', 'number_of_path_edges']])
    axes[0, 1].set_title("Germany")
    axes[0, 0].set_title("Germany Reduced")

    plot = sns.scatterplot(ax=axes[1, 1], x="number_of_path_edges", y="time", data=data_original_nds[['time', 'number_of_path_edges']])
    plot = sns.scatterplot(ax=axes[1, 0], x="number_of_path_edges", y="time", data=data_red_nds[['time', 'number_of_path_edges']])
    axes[1, 1].set_title("Niedersachsen")
    axes[1, 0].set_title("Niedersachsen Reduced")

    plot = sns.scatterplot(ax=axes[2, 1], x="number_of_path_edges", y="time", data=data_original_sl[['time', 'number_of_path_edges']])
    plot = sns.scatterplot(ax=axes[2, 0], x="number_of_path_edges", y="time", data=data_red_sl[['time', 'number_of_path_edges']])
    axes[2, 1].set_title("Saarland")
    axes[2, 0].set_title("Saarland Reduced")

    plt.show()


if __name__ == "__main__":
    main()
