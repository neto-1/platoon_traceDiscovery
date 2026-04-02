import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
import subprocess
import os
import altair as alt
import numpy as np

from selenium import webdriver

routing_named_colors = ["blue", "amber", "green", "red", "dusty purple"]
grouping_named_colors = ["dusty purple", "amber", "blue", "green", "red"]

violet = '#9366bd'
red = '#d62829'
green = '#2da02d'
orange = '#ff800f'
blue = '#2077b4'

grouping_colors = [violet, orange, blue, green, red]
grouping_colors_aaai = [violet, red, blue, orange, green]
grouping_colors_us_aaai = [blue, orange, green]

routing_colors = [blue, orange, green, red, violet]
routing_colors_aaai = [blue, orange, red, violet]
routing_colors_us_aaai = [blue, orange, green, red, violet]

optimal_solver_name = "Exact Solver"
exact_cpp__name = "Exact CPP"

# Names of Approaches
best_pair_name = "Best Pair"
hub_heuristic_name = "Hub Heuristic"
group_select_name = "Group&Select"
ilp_solver = "ILP Solver"
cppr_ilp = "CPPR-ILP"
cppr_greedy = "CPPR-Greedy"
cppr = "CPPR"

def main():
    # plot_group_distribution()

    """ Penalty Parameters and others """
    # grouping_params_savings()
    # group_data_spon()
    # group_random_view()

    routing_data_view()
    # route_table()

    """ Grouping Views and Tables """
    # group_data_view()
    # group_table()

    """ Stacked Plots """
    #routing_grouping_view()
    """ Classic Plots """
    # group_route_view()
    """ Routing Grouping Incentives """
    #incentives_grouping_routing()


    # get_experiment_ids()
    # spontaneous_overview()


    # join_data_for_statistic_test()
    # run_group_statistic_test_r()


    #join_routing_data_for_statistic_test()
    #run_routing_statistic_test_r()


def plot_group_distribution():
    # x = [273749.214918477, 113343.32086553154, 320407.52351951157, 234744.7546340578, 217569.1930696178, 359131.4818084833, 70863.40552878333, 367154.00818265247, 161081.83703165298, 232291.15752284744, 351661.6056027835, 351184.4536133317, 251525.1758781418, 233272.27329367655, 323603.25070034433, 274832.68039388116, 240868.2436280111, 344950.8136444903, 375849.47607731505, 303913.9374146654, 299085.8711638535, 288638.3816414716, 387120.5293139468, 203101.1275392509, 185239.79755666223, 353445.31447405653, 149049.53341855286, 374531.8360623741, 235310.4144676709, 366655.58326113963, 100571.47988111053, 237296.91275211558, 94533.95693065609, 496654.46873512014, 333840.7684702843, 80606.04400197206, 205998.98341568225, 242445.39261460028, 266992.8481766115, 338148.1571174247, 282286.69249598973, 357029.44971537567, 272517.5614379456, 383134.81435717345, 264453.6810104533, 223782.64994373117, 311318.97510691267, 118898.5250189983, 294374.1213153831, 204742.90386658194, 197794.424860941, 198397.97830822194, 70089.01972559195, 186738.55379763345, 338956.854973866, 249142.5755673804, 291976.3334095805, 151155.6238948327, 125095.80167128738, 322183.9367526831, 68308.91862649772, 205644.89502782738, 172489.5652011001, 253133.1233438851, 257971.65281317692, 317249.39033479325, 185096.16320085025, 210332.73971393745, 228987.39777741514, 163809.33661591617, 276177.45914110943, 173929.01016046328, 336018.52234501636, 192667.66764119407, 221234.5376259511, 100057.91098528891, 305369.0959601464, 148279.62095218396, 258893.5947156832, 212295.29397533886, 78961.13687930017, 229645.67653916334, 331707.24268906756, 242827.38348576258, 274665.9490809516, 266329.9970906669, 154961.8483390066, 271284.69429260975, 168016.8017942151, 269845.98919384304, 373414.8875155163, 357064.74631834135, 353911.82508156315, 312155.06613509706, 215066.52558168725, 187036.7191257255, 122899.6250248862, 74937.82982615802, 238603.1646067129, 337528.22968487616]
    # x = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 4, 4, 3, 3, 3, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 3, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 3, 4, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 4, 4, 3, 3, 3, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 3, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 4, 4, 4, 5, 5, 4, 4, 4, 5, 5, 5, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 3, 3, 3, 4, 4, 3, 3, 3, 4, 4, 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3]
    # x = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    x = [2, 34, 11, 97, 5, 2, 3, 2, 16, 3, 4, 34, 11, 27, 14, 14, 7, 3, 6, 2] # greedy
    x = [2, 7, 7, 89, 9, 21, 4, 2, 31, 7, 6, 20, 43, 2, 11, 14, 7, 3, 3, 2, 2, 3] # sgvns
    ax = sns.distplot(x,kde = False, bins=20)

    s = 0

    for p in ax.patches:
        s += p.get_height()

    for p in ax.patches:
        ax.text(p.get_x() + p.get_width() / 2.,
                p.get_height(),
                '{}'.format(int(p.get_height())),
                fontsize=14,
                color='red',
                ha='center',
                va='bottom')

    plt.show()

def run_group_statistic_test_r():
    cwd = os.getcwd()
    subprocess.call(['Rscript', cwd+'/quad_test.r'], shell=False)

def run_routing_statistic_test_r():
    cwd = os.getcwd()
    subprocess.call(['Rscript', cwd+'/routing_quad_test.r'], shell=False)

def copy_grouping_fig_files_to_phd_latex():
    cwd = os.getcwd()
    subprocess.call(['sh',cwd+'/fig/grouping/copy_files.sh'])

def copy_grouping_random_fig_files_to_phd_latex():
    cwd = os.getcwd()
    subprocess.call(['sh',cwd+'/fig/grouping_random/copy_files.sh'])

def copy_grouping_routing_fig_files_to_phd_latex():
    cwd = os.getcwd()
    subprocess.call(['sh',cwd+'/fig/grouping_routing/copy_files.sh'])

def copy_routing_fig_files_to_phd_latex():
    cwd = os.getcwd()
    subprocess.call(['sh',cwd+'/fig/routing/copy_files.sh'])

def plot_distributed_savings(df, file_name, order_labels, grouping_labels, group_by, path):
    pass

def plot_grouping_savings(df, file_name, order_labels, grouping_labels, group_by, path, savings_value):
    # colors = ["#FF0B04", "#4374B3", "#3f6b3b", "#b09c27"]
    # Set your custom color palette
    # sns.palplot(sns.color_palette(flatui))

    print(file_name)

    # plt.figure(figsize=(10, 5))
    sns.set_style("whitegrid")
    #plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)
    # sns.despine()
    fig, ax = plt.subplots(figsize=(10, 4))
    bar_plot = sns.barplot(data=df, ax=ax, x="vehicle_set_size", y=savings_value, hue=group_by, linewidth=1, edgecolor=(0,0,0), hue_order=order_labels)
    bar_plot.set(xlabel='Number of Vehicles', ylabel='Percentage of Fuel Savings')

    def change_width(ax, new_value):
        for patch in ax.patches:
            current_width = patch.get_width()
            diff = current_width - new_value

            # we change the bar width
            patch.set_width(new_value)

            # we recenter the bar
            patch.set_x(patch.get_x() + diff * .5)

            bar_plot.annotate(format(patch.get_height(), '.2f'),
                              (patch.get_x() + patch.get_width() / 2.,
                               patch.get_height()), ha='center',
                              va='center',
                              xytext=(0, 12),
                              textcoords='offset points', rotation=45)

    change_width(ax, .14)
    h, l = ax.get_legend_handles_labels()
    # ax.legend(h, grouping_labels, title="Approaches")
    ax.legend(h, grouping_labels, title="Approaches")

    # plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)
    plt.savefig(path + file_name + "_sav.pdf")
    plt.clf()

def box_plot_grouping_savings(df, file_name, order_labels, grouping_labels, group_by, path):
    # colors = ["#FF0B04", "#4374B3", "#3f6b3b", "#b09c27"]
    # Set your custom color palette
    # sns.palplot(sns.color_palette(flatui))

    print(file_name)

    # plt.figure(figsize=(10, 5))
    sns.set_style("whitegrid")
    #plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)
    # sns.despine()
    fig, ax = plt.subplots(figsize=(10, 4))
    bar_plot = sns.boxplot(data=df, ax=ax, x="vehicle_set_size", y="opt_savings", hue=group_by, linewidth=1, hue_order=order_labels)
    bar_plot.set(xlabel='Number of Vehicles', ylabel='Percentage of Fuel Savings')

    def change_width(ax, new_value):
        for patch in ax.patches:
            current_width = patch.get_width()
            diff = current_width - new_value

            # we change the bar width
            patch.set_width(new_value)

            # we recenter the bar
            patch.set_x(patch.get_x() + diff * .5)

            bar_plot.annotate(format(patch.get_height(), '.2f'),
                              (patch.get_x() + patch.get_width() / 2.,
                               patch.get_height()), ha='center',
                              va='center',
                              xytext=(0, 12),
                              textcoords='offset points', rotation=45)

    change_width(ax, .14)
    h, l = ax.get_legend_handles_labels()
    # ax.legend(h, grouping_labels, title="Approaches")
    ax.legend(h, grouping_labels, title="Approaches")

    # plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)
    plt.savefig(path + file_name + "_sav.pdf")
    plt.clf()

def plot_grouping_time(df, file_name, order_labels, grouping_labels, scala, group_by, path, ticks_x = None):
    sns.set_style("white")
    plt.figure(figsize=(8, 5))
    g = sns.lineplot(x="vehicle_set_size", y="time", hue=group_by,  markers=True, data = df, hue_order=order_labels, marker="o")
    g.set(xlabel='Number of Vehicles', ylabel='Time in Seconds')


    """ Set ticks """
    if ticks_x is not None:
        g.set(xticks=ticks_x)


    plt.legend(title='Approaches', loc='upper left', labels=grouping_labels)

    if scala is "log":
        plt.yscale('log')

    plt.savefig(path + file_name + ".pdf")
    plt.clf()
    plt.close()

def group_time_make_table(df, file_name, order_labels, grouping_labels, scala, group_by, path):
    pass

def group_table():
    instances =[[ {"grid10_grouping10_50": ['lin'], "grid10_grouping100_300": ['log']} ], [ {"swe_grouping10_50": ['lin'], "swe_grouping100_300": ['log']} ],
                [ {"ber_grouping10_50": ['lin'], "ber_grouping100_300": ['log']} ],  [ {"bay_grouping10_50": ['lin'], "bay_grouping100_300": ['log']} ],
                [ {"grid20_grouping10_50": ['lin'], "grid20_grouping100_300": ['log']} ], [ {"grid30_grouping10_50": ['lin'], "grid30_grouping100_300": ['log']}],
                [ {"grid30_grouping10_50": ['lin'], "grid30_grouping100_300": ['log']}],  [ {"ger_grouping10_50": ['lin'], "ger_grouping100_300": ['log']}],
                [ {"us_grouping10_50": ['lin'], "us_grouping100_300": ['log']}] ]
    path = "data/grouping_savings/"



    for instance in instances:

        file_name_tex = ""
        concat_instances = []
        for local_instance in instance:
            for file_name, instance_params in local_instance.items():
                df = pd.read_csv(path + file_name + ".csv")
                concat_instances.append(df)

                file_name_tex = file_name_tex + file_name

        full_instance = pd.concat(concat_instances, axis=0, ignore_index=True)

        selected_data = full_instance[['vehicle_set_size', 'grouping', 'time']]
        sorted_data = selected_data.sort_values(by=['vehicle_set_size', 'grouping'], ascending=[1, 1])
        grouped = sorted_data.groupby(['grouping', 'vehicle_set_size'])

        keys_head = sorted_data.groupby(['grouping']).groups.keys()
        keys_rows = sorted_data.groupby(['vehicle_set_size']).groups.keys()

        table = pd.DataFrame(columns=list(keys_head), index=list(keys_rows))

        mean_label = 'mean $s$'
        overhead_label = r'overh. $\%$'

        columns_with_sd_av = pd.MultiIndex.from_product([list(keys_head), [mean_label, overhead_label]])
        table_with_sd = pd.DataFrame(columns=columns_with_sd_av, index=list(keys_rows))

        for problem, data in grouped:
            table.at[problem[1], problem[0]] = data['time'].mean()
            table_with_sd.loc[problem[1], problem[0]][mean_label] = data['time'].mean()
            table_with_sd.loc[problem[1], problem[0]][overhead_label] = -1

        for row in table_with_sd.iterrows():
            row_data = row[1]
            exact_value = row_data['SingleGroup'][mean_label]
            vehicle_size = row[0]
            for method, value in row_data.items():
                mean_value = table_with_sd.loc[vehicle_size, method[0]][mean_label]
                table_with_sd.loc[vehicle_size, method[0]][overhead_label] = (mean_value / (exact_value/100)) - 100


        table_with_sd = table_with_sd.drop(('SingleGroup', overhead_label), axis=1)

        order_of_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal',  'SGVNS', 'SingleGroup']
        table_with_sd = table_with_sd[order_of_labels]

        names_of_labels = {"AlphaCut": r'\aalphacut', "GreedyBronKerbosch": r'\agreedycpp', "CPPOptimal": r'\aoptcpp',  "SGVNS": r'\asgvnscpp', "SingleGroup": r'\exactsolverk'}


        table_with_sd = table_with_sd.rename(columns=names_of_labels)
        table_with_sd = table_with_sd.round(1)

        latex_output = table_with_sd.to_latex(escape=False)
        print(latex_output)

        f = open("/Users/dmitry/Documents/wd/phd/docs/thesis/Macros/evaluation/"+file_name_tex+".tex", "w")
        f.write(latex_output)
        f.close()


def route_table():
    order = ['BestPair', 'HubRouting',  'CG', 'ILP']
    labels = {"BestPair": r'\bestpairk', "HubRouting": r'\hubheuristick', "CG": r'\textit{Column Generation}',  "ILP": r'\exactsolverk'}

    order_no_bp = ['HubRouting',  'CG', 'ILP']
    labels_no_bp = {"HubRouting": r'\hubheuristick', "CG": r'\textit{Column Generation}',  "ILP": r'\exactsolverk'}

    order_no_bp_hh = ['CG', 'ILP']
    labels_no_bp_hh = {"CG": r'\textit{Column Generation}',  "ILP": r'\exactsolverk'}

    instances =[[ {"grid10_routing10_50": [order, labels], "grid10_routing100_300": [order, labels]} ],
                [ {"swe_routing10_50": [order, labels], "swe_routing100_300": [order, labels]} ],
                [ {"ber_routing10_50": [order, labels], "ber_routing100_300": [order, labels]}],
                [ {"bay_routing10_50": [order, labels], "bay_routing100_300": [order, labels]} ],
                [ {"grid20_routing10_50": [order, labels], "grid20_routing100_300": [order, labels]} ],
                [ {"grid30_routing10_50": [order_no_bp, labels_no_bp], "grid30_routing100_300": [order_no_bp, labels_no_bp]}],
                [ {"ger_routing10_50": [order_no_bp, labels_no_bp], "ger_routing100_300": [order_no_bp, labels_no_bp]}],
                [ {"us_routing10_50": [order_no_bp_hh, labels_no_bp_hh], "us_routing100_300": [order_no_bp_hh, labels_no_bp_hh]}] ]
    path = "data/routing_savings/"

    order_of_labels = None
    names_of_labels = None
    for instance in instances:
        file_name_tex = ""
        concat_instances = []
        for local_instance in instance:
            for file_name, instance_params in local_instance.items():
                df = pd.read_csv(path + file_name + ".csv")
                concat_instances.append(df)
                file_name_tex = file_name_tex + file_name

                order_of_labels = instance_params[0]
                names_of_labels = instance_params[1]


        full_instance = pd.concat(concat_instances, axis=0, ignore_index=True)

        selected_data = full_instance[['vehicle_set_size', 'routing', 'time']]
        sorted_data = selected_data.sort_values(by=['vehicle_set_size', 'routing'], ascending=[1, 1])
        grouped = sorted_data.groupby(['routing', 'vehicle_set_size'])

        keys_head = sorted_data.groupby(['routing']).groups.keys()
        keys_rows = sorted_data.groupby(['vehicle_set_size']).groups.keys()

        table = pd.DataFrame(columns=list(keys_head), index=list(keys_rows))

        mean_label = 'mean $s$'
        overhead_label = r'overh. $\%$'

        columns_with_sd_av = pd.MultiIndex.from_product([list(keys_head), [mean_label, overhead_label]])
        table_with_sd = pd.DataFrame(columns=columns_with_sd_av, index=list(keys_rows))

        for problem, data in grouped:
            table.at[problem[1], problem[0]] = data['time'].mean()
            table_with_sd.loc[problem[1], problem[0]][mean_label] = data['time'].mean()
            table_with_sd.loc[problem[1], problem[0]][overhead_label] = -1

        for row in table_with_sd.iterrows():
            row_data = row[1]
            exact_value = row_data['ILP'][mean_label]
            vehicle_size = row[0]
            for method, value in row_data.items():
                mean_value = table_with_sd.loc[vehicle_size, method[0]][mean_label]
                table_with_sd.loc[vehicle_size, method[0]][overhead_label] = (mean_value / (exact_value/100)) - 100

        table_with_sd = table_with_sd.drop(('ILP', overhead_label), axis=1)

        table_with_sd = table_with_sd[order_of_labels]
        table_with_sd = table_with_sd.rename(columns=names_of_labels)
        table_with_sd = table_with_sd.round(1)

        latex_output = table_with_sd.to_latex(escape=False)
        print(instance)
        print(latex_output)

        f = open("/Users/dmitry/Documents/wd/phd/docs/thesis/Macros/evaluation/routing/"+file_name_tex+".tex", "w")
        f.write(latex_output)
        f.close()



def group_data_view():
    # sns.set_palette(sns.xkcd_palette(grouping_named_colors))
    sns.set_palette(sns.color_palette(grouping_colors_aaai))

    ticks10_50 = [10, 20, 30, 50]
    ticks100_300 = [100, 200, 300]

    all_files_grouping = {  "grid10_grouping10_50": ['lin', ticks10_50], "grid10_grouping100_300": ['log', ticks100_300],
                            "grid20_grouping10_50": ['lin', ticks10_50], "grid20_grouping100_300": ['log', ticks100_300],
                            "grid30_grouping10_50": ['lin', ticks10_50], "grid30_grouping100_300": ['lin', ticks100_300],
                            "ber_grouping10_50": ['lin', ticks10_50], "ber_grouping100_300": ['log', ticks100_300],
                            "bay_grouping10_50": ['lin', ticks10_50], "bay_grouping100_300": ['log', ticks100_300],
                            "swe_grouping10_50": ['lin', ticks10_50], "swe_grouping100_300": ['log', ticks100_300],
                            "ger_grouping10_50": ['lin', ticks10_50], "ger_grouping100_300": ['lin', ticks100_300],
                            "us_grouping10_50": ['lin', ticks10_50], "us_grouping100_300": ['lin', ticks100_300]}

    grouping_order_labels = ['AlphaCut', 'SingleGroup', 'CPPOptimal','GreedyBronKerbosch', 'SGVNS']
    grouping_labels = [group_select_name,  ilp_solver, cppr_ilp, cppr_greedy, cppr]
    # grouping_labels = ['Alpha-Cut Grouping', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP', optimal_solver_name]

    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_savings_aaai/"+file_name+".csv")

        if file_name is "us_grouping100_300":
            sns.set_palette(sns.color_palette(grouping_colors_us_aaai))

            grouping_order_labels = ['CPPOptimal', 'GreedyBronKerbosch', 'SGVNS']
            # grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS']
            grouping_labels = [cppr_ilp, cppr_greedy, cppr]
            # grouping_labels = ['Alpha-Cut Grouping', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP']

        """ Plot grouping data - Savings """
        plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/aaai/", "opt_savings")

        """ Plot grouping data - Time """
        scala = params[0]
        ticks_x = params[1]
        plot_grouping_time(df, file_name, grouping_order_labels, grouping_labels, scala, "grouping", "fig/aaai/", ticks_x)

        """ Replace old figure for Phd latex document """
         # copy_grouping_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'grouping'])
        pd.options.display.max_columns = None
        print(grouped.agg({'time':["median", "std"], 'savings':["median"]}))

def group_random_view():
    # sns.set_palette(sns.xkcd_palette(grouping_named_colors))
    sns.set_palette(sns.color_palette(grouping_colors))

    all_files_grouping = {"ger_grouping_random10_50": ['lin'], "ger_grouping_random100_300": ['lin']}

    grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS', 'SingleGroup']
    grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP', 'Exact Solver']
    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_random/"+file_name+".csv")

        """ Plot grouping data - Savings """
        # plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/grouping_random/")

        box_plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/grouping_random/")

        """ Plot grouping data - Time """
        scala = params[0]
        plot_grouping_time(df, file_name, grouping_order_labels, grouping_labels, scala, "grouping", "fig/grouping_random/")

        """ Replace old figure for Phd latex document """
        copy_grouping_random_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'grouping'])
        pd.options.display.max_columns = None
        print(grouped.agg({'time':["median", "std"], 'savings':["median"]}))

def group_data_spon():
    all_files_grouping = {  "results": ['lin']}

    grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS', 'SingleGroup']
    grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP', 'Exact Solver']
    for file_name, params in all_files_grouping.items():


        df = pd.read_csv("/Users/dmitry/Documents/wd/platooning/src/expscenario/"+file_name+".csv")

        if file_name is "us_grouping100_300":
            grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS']
            grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP']

        """ Plot grouping data - Savings """
        plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/grouping/", "opt_savings")

        """ Plot grouping data - Time """
        scala = params[0]
        plot_grouping_time(df, file_name, grouping_order_labels, grouping_labels, scala, "grouping", "fig/grouping/")

        """ Replace old figure for Phd latex document """
        copy_grouping_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'grouping'])
        pd.options.display.max_columns = None
        print(grouped.agg({'time':["mean", "std"], 'savings':["median"]}))


def group_route_view():
    # sns.set_palette(sns.xkcd_palette(grouping_named_colors))
    sns.set_palette(sns.color_palette(grouping_colors))

    ticks100_2000 = [100, 200, 300, 500, 700, 1000, 1500, 2000]
    all_files_grouping = {  "us_grouping_routing100_300": ['lin', ticks100_2000]}

    grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS', 'SingleGroup']
    grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP', optimal_solver_name]
    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_routing/"+file_name+".csv")

        if file_name is "us_grouping_routing100_300":
            grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'SGVNS']
            grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', 'SGVNS CPP']

        """ Plot grouping data - Savings """
        plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/grouping_routing/", "opt_savings")

        """ Plot grouping data - Time """
        scala = params[0]
        ticks_x = params[1]
        plot_grouping_time(df, file_name, grouping_order_labels, grouping_labels, scala, "grouping", "fig/grouping_routing/", ticks_x)

        """ Replace old figure for Phd latex document """
        copy_grouping_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'grouping'])
        pd.options.display.max_columns = None

        resulting_df = grouped.agg({'time':["median", "std"], 'savings':["median"]})
        print(resulting_df)

        # time_df = resulting_df['time']['median']
        # print(time_df)

        # x = np.array([100, 200, 300, 500, 700, 1000, 1500, 2000])
        # y = np.array([318.312020, 729.868107, 1457.486627, 3387.657223, 5850.820626 , 12782.751485, 38082.194067, 75266.171271])
        # z = np.polyfit(x, y, 2)
        # print(z)

    # copy_grouping_routing_fig_files_to_phd_latex()

def routing_data_view():
    ticks10_50 = [10, 20, 30, 50]
    ticks100_300 = [100, 200, 300]
    ticks10_300 = [10, 20, 30, 50, 100, 200, 300]
    ticks10_100 = [10, 20, 30, 50, 100]

    all_files_routing = {"grid10_routing10_50": ['log', ticks10_50], "grid10_routing100_300": ['log', ticks100_300],
                         "grid20_routing10_50": ['log', ticks10_50], "grid20_routing100_300": ['log', ticks100_300],
                         "grid30_routing10_50": ['lin', ticks10_50], "grid30_routing100_300": ['lin', ticks100_300],
                         "ber_routing10_50": ['log', ticks10_50], "ber_routing100_300": ['log', ticks100_300],
                         "bay_routing10_50": ['log', ticks10_50], "bay_routing100_300": ['log', ticks100_300],
                         "swe_routing10_50": ['log', ticks10_50], "swe_routing100_300": ['log', ticks100_300],
                         "ger_routing10_50": ['log', ticks10_50], "ger_routing100_300": ['lin', ticks100_300],
                         "ger_routing10_300":['lin', ticks10_300],
                         "us_routing100_300": ['log', ticks100_300], "us_routing10_50": ['log', ticks10_50], "us_routing10_100": ['lin', ticks10_100]}


    for file_name, params in all_files_routing.items():
        df = pd.read_csv("data/routing_savings_aaai/"+file_name+".csv")


        source_number = '57'
        sns.set_palette(sns.color_palette(routing_colors_aaai))
        routing_order_labels = ['BestPair', 'HubRouting', 'ILP']


        # routing_order_labels = ['BestPair', 'HubRouting', 'CG', 'ILP']
        # routing_labels = ['Best Pair ['+ source_number +']', 'Hub Heuristic [' + source_number + ']', 'CG', 'Exact Solver']
        routing_labels = [best_pair_name, hub_heuristic_name, ilp_solver]

        if file_name is "us_routing10_100" or file_name is "us_routing100_300" or file_name is "ger_routing100_300":
            routing_order_labels = ['CG', 'ILP']
            routing_labels = ['CG', 'Exact Solver']
            sns.set_palette(sns.color_palette([green, red]))
            # sns.set_palette(sns.color_palette([green, red]))
        elif    file_name is "ger_routing10_50" or file_name is "swe_routing100_300" or \
                file_name is "grid20_routing100_300" or file_name is "bay_routing100_300" or \
                file_name is "grid30_routing10_50" or file_name is "grid30_routing100_300" or file_name is "ger_routing10_300":
            routing_order_labels = ['HubRouting', 'ILP']
            # routing_order_labels = ['HubRouting', 'CG', 'ILP']
            # routing_labels = ['Hub Heuristic [' + source_number + ']', 'CG', 'Exact Solver']

            routing_labels = [hub_heuristic_name, ilp_solver]
            # sns.set_palette(sns.color_palette([orange, green, red]))
            sns.set_palette(sns.color_palette([orange, red]))


        """ Plot grouping data """
        plot_grouping_savings(df, file_name, routing_order_labels, routing_labels, "routing", "fig/routing_aaai/", "opt_savings")

        scala = params[0]
        ticks_x = params[1]

        plot_grouping_time(df, file_name, routing_order_labels, routing_labels, scala, "routing", "fig/routing_aaai/", ticks_x)

        """ Replace old figure for Phd latex document """
        # copy_routing_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'routing'])
        pd.options.display.max_columns = None
        print(grouped.agg({'time':["mean", "std"], 'savings':["median"]}))

def get_experiment_ids():
    all_files = ['data/spontaneous/us_spontaneous10_50.csv']
    li = []
    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    joined_frame = pd.concat(li, axis=0, ignore_index=True)
    joined_frame = joined_frame.sort_values(by=['road_points', 'vehicle_set_size'], ascending=[1, 1])
    joined_grouped = joined_frame.groupby(['id'])

    print(joined_grouped.median().index.get_level_values(0).tolist())
    ids = joined_grouped.median().index.get_level_values(0).tolist()

    for exp_id in ids:
        print(exp_id)

def spontaneous_overview():
    filename = 'data/spontaneous/summary.csv'
    df = pd.read_csv(filename, index_col=None, header=0)
    #pd.set_option('display.max_columns', 30)
    # grouped = df.sort_values(by=['road_points', 'vehicle_set_size', 'grouping'], ascending=[1, 1, 1])
    grouped = df.groupby(['road_points', 'vehicle_set_size', 'grouping'])
    print(grouped.agg({'savings': ["mean"], 'opt_savings': ["mean"], 'spontaneous_platooning_savings': ["mean"]}))

    mean_group = grouped.agg({'savings': ["mean"], 'opt_savings': ["mean"], 'spontaneous_platooning_savings': ["mean"]})
    mean_group.to_csv('data/spontaneous/savings_result.csv')

def join_data_for_statistic_test():
    path = 'data/grouping_savings/'
    all_files = glob.glob(path + "/*.csv")

    # all_files = ['data/grouping/grid20_grouping100_300.csv']


    """ Test 1  """
    all_files = [path + 'grid10_grouping10_50.csv', path + 'grid10_grouping100_300.csv', path + 'grid20_grouping10_50.csv',
                path + 'grid20_grouping100_300.csv', path + 'ber_grouping10_50.csv', path + 'ber_grouping100_300.csv']

    """ Test 2 """
    #all_files = [path + 'bay_grouping10_50.csv', path + 'bay_grouping100_300.csv',
    #              path + 'swe_grouping10_50.csv', path + 'swe_grouping100_300.csv']


    """ Test 3 """
    #all_files = [   path + 'grid30_grouping10_50.csv', path + 'grid30_grouping100_300_stats.csv',
    #                 path + 'ger_grouping10_50.csv', path + 'ger_grouping100_300_stats.csv', path + 'us_grouping10_50_stats.csv']

    # all_files = [   path + 'grid10_grouping10_50.csv',  path + 'grid10_grouping100_300.csv',
    #                 path + 'ber_grouping10_50.csv', path + 'ber_grouping100_300.csv',
    #                 path + 'bay_grouping10_50.csv', path + 'bay_grouping100_300.csv',
    #                 path + 'swe_grouping10_50.csv', path + 'swe_grouping100_300.csv',
    #                 path + 'grid20_grouping10_50.csv', path + 'grid20_grouping100_300.csv',
    #                 path + 'grid30_grouping10_50.csv', path + 'grid30_grouping100_300.csv',
    #                 path + 'ger_grouping10_50.csv', path + 'ger_grouping100_300.csv', path + 'us_grouping10_50.csv']


    """ Routing Tests """

    path = 'data/routing_savings/'
    """ Test 1 """
    # all_files = [path + 'bay_routing10_50.csv', path + 'bay_routing100_300.csv',
    #               path + 'ber_routing10_50.csv', path + 'ber_routing100_300.csv']

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)



    joined_frame = pd.concat(li, axis=0, ignore_index=True)
    column_label_order = ['AlphaCut', 'GreedyBronKerbosch','CPPOptimal', 'SGVNS', 'SingleGroup']

    names_of_labels = {"AlphaCut": r'\aalphacut', "GreedyBronKerbosch": r'\agreedycpp', "CPPOptimal": r'\aoptcpp',
                       "SGVNS": r'\asgvnscpp', "SingleGroup": r'\exactsolverk'}


    joined_frame = joined_frame.sort_values(by=['road_points', 'vehicle_set_size'], ascending=[1, 1])
    joined_grouped = joined_frame.groupby(['road_points', 'vehicle_set_size'])

    data = pd.DataFrame([])
    pd.set_option('display.max_columns', 30)

    for name, problem in joined_grouped:
        print("Problem:", name)
        methods = problem.groupby(['grouping'])
        quade_df = pd.DataFrame(columns=list(methods.groups.keys()))
        for method_name, method in methods:
            quade_df[method_name] = pd.Series([thing[0] for thing in method[['time']].values])

        data = data.append(quade_df, sort=False)
        print(quade_df)

    data = data[column_label_order]
    data.rename(columns=names_of_labels,
                     inplace=True)
    data.to_csv('quade.csv', index=False)


def join_routing_data_for_statistic_test():
    path = 'data/routing_savings/'
    all_files = glob.glob(path + "/*.csv")

    # all_files = ['data/grouping/grid20_grouping100_300.csv']


    """ Test 1  """
    all_files = [   path + 'grid10_routing10_50.csv', path + 'grid10_routing100_300.csv',
                    path + 'grid20_routing10_50.csv', path + 'grid20_routing100_300.csv',
                    path + 'ber_routing10_50.csv', path + 'ber_routing100_300.csv',
                    path + 'bay_routing10_50.csv', path + 'bay_routing100_300.csv',
                    path + 'grid30_routing10_50.csv', path + 'grid30_routing100_300.csv',
                    path + 'swe_routing10_50.csv', path + 'swe_routing100_300.csv',
                    path + 'ger_routing10_300.csv'
                   ]

    #path + 'ger_routing10_50.csv', path + 'ger_routing100_300.csv'

    # """ Test 1  """
    # all_files = [   path + 'grid10_routing10_50.csv', path + 'grid10_routing100_300.csv',
    #                 path + 'grid20_routing10_50.csv', path + 'grid20_routing100_300.csv',
    #                 path + 'ber_routing10_50.csv', path + 'ber_routing100_300.csv'
    #                ]

    # """ Test 2  """
    # all_files = [   path + 'ger_routing10_300.csv', path + 'us_routing10_100.csv'
    #                ]

    # """ Test 2  """
    # all_files = [   path +"stats/" + 'bay_routing10_50_stats.csv', path  +"stats/" + 'bay_routing100_300_stats.csv',
    #                  path +"stats/" +  'swe_routing10_50_stats.csv', path +"stats/" + 'swe_routing100_300_stats.csv',
    #                 ]
    #
    #
    # """ Test 2  """
    # all_files = [   path +"stats/" + 'bay_routing10_50_stats.csv', path  +"stats/" + 'bay_routing100_300_stats.csv',
    #                 path +"stats/" +  'swe_routing10_50_stats.csv', path +"stats/" + 'swe_routing100_300_stats.csv',
    #                 path + 'grid10_routing10_50.csv', path +"stats/" + 'grid10_routing100_300_stats.csv',
    #                 path +"stats/" + 'grid20_routing10_50_stats.csv', path +"stats/" + 'grid20_routing100_300_stats.csv',
    #                 path +"stats/" + 'ber_routing10_50_stats.csv', path +"stats/" + 'ber_routing100_300_stats.csv'
    #                 ]
    #
    # """ Test 3  """
    # all_files = [   path +"stats/" + 'ger_routing10_300_stats.csv', path +"stats/" + 'us_routing10_100_stats.csv'
    #                 ]

    # """ Test 2  """
    # all_files = [   path +"stats/" + 'bay_routing10_50_stats.csv', path  +"stats/" + 'bay_routing100_300_stats.csv',
    #                  path +"stats/" +  'swe_routing10_50_stats.csv', path +"stats/" + 'swe_routing100_300_stats.csv'
    #                 ]

    """ Test 3  """
    # all_files = [
    #                  path + 'grid30_routing10_50.csv', path + 'grid30_routing100_300.csv',
    #                  path + 'ger_routing10_300.csv',
    #                  path + 'us_routing10_100.csv'
    #                 ]


    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    joined_frame = pd.concat(li, axis=0, ignore_index=True)
    joined_frame = joined_frame.sort_values(by=['road_points', 'vehicle_set_size'], ascending=[1, 1])
    joined_grouped = joined_frame.groupby(['road_points', 'vehicle_set_size'])

    data = pd.DataFrame([])
    pd.set_option('display.max_columns', 30)

    for name, problem in joined_grouped:
        print("Problem:", name)
        methods = problem.groupby(['routing'])
        quade_df = pd.DataFrame(columns=list(methods.groups.keys()))
        for method_name, method in methods:
            quade_df[method_name] = pd.Series([thing[0] for thing in method[['time']].values])

        data = data.append(quade_df, sort=False)
        print(quade_df)

    # data.rename(columns={'AlphaCut': 'alpha.cut',
    #                             'CPPOptimal': 'CPP Opt',
    #                             'GreedyBronKerbosch': 'CPP Greedy',
    #                             'SGVNS': 'SGVNS',
    #                             'SingleGroup': 'Optimal'},
    #                  inplace=True)
    data.to_csv('quade_routing.csv', index=False)


def grouping_params_savings():
    sns.set_palette(sns.color_palette(grouping_colors))

    # all_files_grouping = { "ger_spontaneous10_50": ['lin'], "us_spontaneous10_50": ['lin']}
    all_files_grouping = { "ger_grouping_params100_300": ['lin']}

    grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS', 'SingleGroup']
    grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP', optimal_solver_name]
    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_parameters/"+file_name+".csv")

        if file_name is "us_grouping100_300":
            grouping_order_labels = ['AlphaCut', 'GreedyBronKerbosch', 'CPPOptimal', 'SGVNS']
            grouping_labels = ['Alpha-Cut Grouping Method', 'Greedy CPP', exact_cpp__name, 'SGVNS CPP']

        """ Plot grouping data - Savings """
        # plot_grouping_savings(df, file_name, grouping_order_labels, grouping_labels, "grouping", "fig/spontaneous/")

        """ Plot grouping data - Time """
        # scala = params[0]
        # plot_grouping_time(df, file_name, grouping_order_labels, grouping_labels, scala, "grouping", "fig/spontaneous/")

        """ Replace old figure for Phd latex document """
        # copy_grouping_fig_files_to_phd_latex()

        grouped = df.groupby(['vehicle_set_size', 'penalty'])
        pd.options.display.max_columns = None
        print(grouped.agg({'time':["median"], 'opt_savings':["median"]}))

        print(grouped.agg({'time': ["median"], 'opt_savings': ["median"]}).to_latex())

def routing_grouping_view():
    all_files_grouping = {"us_grouping_routing100_300": ['lin'], "ger_grouping_routing100_300": ['lin']}
    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_routing/"+file_name+".csv")

        # range=[violet, red, green, orange, blue]
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('vehicle_set_size:N', title=None),
            y=alt.Y('mean(time):Q', axis=alt.Axis(grid=False, title=None)),
            column=alt.Column('routing:N', title=None),
            color=alt.Color('grouping:N', scale=alt.Scale(range=[violet, orange, green, red]))
        ).configure_view(
            strokeOpacity=0
        )

        chart.save('/Users/dmitry/Documents/wd/platooning/src/exp2/test/fig/grouping_routing/' + file_name +'.svg', scale_factor=2.0)


def incentives_grouping_routing():
    all_files_grouping = {"us_grouping_routing100_300": ['lin']}
    for file_name, params in all_files_grouping.items():
        df = pd.read_csv("data/grouping_routing/" + file_name + ".csv")

        print(df.head())

        df = df.loc[df['grouping'] != 'AlphaCut']
        df = df.replace('GreedyBronKerbosch', r'\agreedycpp')
        df = df.replace('SGVNS', r'\asgvnscpp')

        vehicle_set_size = r'\(\vvehiclesnumber\)'
        grouping = 'Grouping Alg.'
        incentive_time = r'Incentives Times (s)'
        grouping_time = r'Grouping Times (s)'
        routing_time = r'Routing Time (s)'
        time = r'Total Time (s)'


        names_of_labels = {"vehicle_set_size": vehicle_set_size, "incentive_time": incentive_time, "grouping_time": grouping_time,
                           "routing_time": routing_time, "time": time, "grouping": grouping}

        df.rename(columns=names_of_labels,
                    inplace=True)
        grouped = df.groupby([vehicle_set_size, grouping])
        table_with_sd = grouped.agg({incentive_time: ["mean"], grouping_time: ["mean"], routing_time: ["mean"], time: ["mean"]})



        print(table_with_sd)



        latex_output = table_with_sd.to_latex(escape=False)
        print(latex_output)

        # pivot_df = df.pivot(index='Year', columns='Month', values='Value')

        # df.loc[:, ['incentive_time', 'grouping_time', 'routing_time']].plot.bar(stacked=True, color=colors, figsize=(10, 7))

        # chart = alt.Chart(df).mark_area().encode(
        #     x="vehicle_set_size:T",
        #     y="time:Q",
        #     color={"incentive_time": "Origin", "grouping_time": "nominal", "routing_time": ""}
        # )
        #
        # chart.save('/Users/dmitry/Documents/wd/platooning/src/exp2/test/fig/grouping_routing/' + file_name + '_time.png',
        #            scale_factor=2.0)

if __name__ == "__main__":
    main()
