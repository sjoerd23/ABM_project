import time
import csv
import numpy as np
import matplotlib.pyplot as plt
import SALib
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd
from mesa.batchrunner import BatchRunner

from model import CovidSupermarketModel
import core


def plot_index(s, params, i, title=""):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {"S#": dict, "S#_conf": dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """
    indices = s["S" + i]
    errors = s["S" + i + "_conf"]
    plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle="None", marker="o")
    plt.axvline(0, c="k")


def generate_samples(problem, distinct_samples, sample_index):

    params = saltelli.sample(problem, distinct_samples, calc_second_order=False)

    len_params = len(params)
    print(len_params)
    params_array = [params[i * int(len_params/5) : (i+1) * int(len_params/5)] for i in range(5)]


    return params_array[sample_index]


def main():

    # load supermarket floorplan for simulation
    floorplan = core.load_floorplan("data/albert_excel_test.csv")
    width = len(floorplan)
    height = len(floorplan[0])

    problem = {
        "num_vars": 5,
        "names": ["N_customers", "vaccination_prop", "len_shoplist", "basic_compliance", "vision"],
        "bounds": [[10, 150], [0, 1], [0, 20], [0, 1], [3, 7]]
    }

    # Set the amount of steps, and the amount of distinct values per variable
    distinct_samples = 500   # 500
    n_steps = 500       # 500

    #### SET SAMPLE INDEX ####
    sample_index = 0

    # make sure a correct index is given
    print("\nWARNING! MAKE SURE TO SELECT THE APPROPIATE sample_index!!!\n")
    assert sample_index >= 0 and sample_index < 5

    print("Using sample_index {}".format(sample_index))
    print("Using {} distinct samples in total\n".format(distinct_samples))

    params = generate_samples(problem, distinct_samples, sample_index)

    print("Estimated time: {:.2f} hours".format(len(params)*2/60))
    print("Estimated time per computer (5): {:.2f} hours\n".format((len(params)*2/60)/5))

    data = pd.DataFrame(
        index=range(len(params)),
        columns=[
            "N_customers", "vaccination_prop", "len_shoplist", "basic_compliance", "vision", "run",
            "n_problematic_contacts", "n_problematic_contacts_mean",
            "n_problematic_contacts_mean_100"
        ]
    )

    time_start = time.time()

    count = 0
    for i, vals in enumerate(params):

        # change parameters that should be integers i.e. index 0, 2, 4
        vals = list(vals)
        vals[0] = int(vals[0])
        vals[2] = int(vals[2])
        vals[4] = int(vals[4])

        print("Progress: {:.2%}".format(float(i)/len(params)))
        print("Calculating sample {}".format(vals))

        model = CovidSupermarketModel(
            floorplan, width, height, vals[0], vals[1], vals[2], vals[3], vals[4]
        )
        model.run_model(n_steps)

        data_run = model.datacollector.get_model_vars_dataframe()
        data_run_n_problematic_contacts = data_run.iloc[-1]
        data_run_n_problematic_contacts_mean = np.mean(data_run["n_problematic_contacts"])
        data_run_n_problematic_contacts_mean_100 = np.mean(data_run["n_problematic_contacts"][100:])

        data.iloc[count, 5] = count
        data.iloc[count, 6] = int(data_run_n_problematic_contacts)
        data.iloc[count, 7] = float(data_run_n_problematic_contacts_mean)
        data.iloc[count, 8] = float(data_run_n_problematic_contacts_mean_100)
        data.iloc[count, 0:5] = vals

        # save dataframe each iteration to prevent losing data. If all goes well, then only the last
        # saved dataframe should be used for analysis
        data.to_csv("results/Sobol/data_{}_{}.csv".format(params[0], count))
        count += 1

    # This is just for analyzing. Comment when doing the actual runs
    # # Unnamed column is the original index column of the original dataframe
    # data_analyze = pd.DataFrame(
    #     index=range(0),
    #     columns=[
    #         "N_customers", "vaccination_prop", "len_shoplist", "basic_compliance", "vision", "run",
    #         "n_problematic_contacts", "n_problematic_contacts_mean",
    #         "n_problematic_contacts_mean_100"
    #     ]
    # )
    # datas = []
    # for i in range(5):
    #     data_params = generate_samples(problem, distinct_samples, i)
    #     data_count = len(data_params) - 1
    #     datas.append(pd.read_csv("results/Sobol/data_{}_{}.csv".format(data_params[0], data_count)))
    #
    # data = pd.concat([data_analyze, datas[0], datas[1], datas[2], datas[3], datas[4]], ignore_index=True, sort=False)
    #
    # Si_problematic_contacts = sobol.analyze(problem, data["n_problematic_contacts"].values, calc_second_order=False, print_to_console=True)
    #
    # plot_index(Si_problematic_contacts, problem["names"], "1", "First order sensitivity")
    #
    # # Total order
    # plot_index(Si_problematic_contacts, problem["names"], "T", "Total order sensitivity")
    #
    # plt.show()

    print("\nTotal simulation time: {:.2f}s".format(time.time()-time_start))

    return


if __name__ == "__main__":
    main()