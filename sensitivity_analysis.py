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


# https://stackoverflow.com/questions/50786266/writing-dictionary-of-dataframes-to-file
def saver(dictex):
    for key, val in dictex.items():
        val.to_csv("results/data_{}.csv".format(str(key)))

    with open("results/keys.txt", "w") as f: #saving keys to file
        f.write(str(list(dictex.keys())))

# https://stackoverflow.com/questions/50786266/writing-dictionary-of-dataframes-to-file
def loader():
    """Reading data from keys"""
    with open("results/keys.txt", "r") as f:
        keys = eval(f.read())

    dictex = {}
    for key in keys:
        dictex[key] = pd.read_csv("results/data_{}.csv".format(str(key)))

    return dictex


def main():

    # load supermarket floorplan for simulation
    floorplan = core.load_floorplan("data/albert_excel_test.csv")
    width = len(floorplan)
    height = len(floorplan[0])

    problem = {
    "num_vars": 4,
    "names": ["N_customers", "vaccination_prop", "len_shoplist", "basic_compliance"],
    "bounds": [[25, 125], [0, 1], [0, 25], [0, 1]]
    }

    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 3
    distinct_samples = 3
    n_steps = 50

    # N_customers = 100
    # vaccination_prop = 0.0
    # len_shoplist = 1
    # basic_compliance = 0.2

    time_start = time.time()
    datas = {}

    for i, var in enumerate(problem["names"]):
        samples = np.linspace(*problem["bounds"][i], num=distinct_samples)

        if var == "N_customers" or var == "len_shoplist":
            samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)


        batch = BatchRunner(
            CovidSupermarketModel,
            fixed_parameters={"floorplan": floorplan, "width": width, "height": height},
            model_reporters = {"n_problematic_contacts": lambda m: m.n_problematic_contacts},
            max_steps=n_steps,
            iterations=replicates,
            variable_parameters={var: samples},
            display_progress=True
        )

        batch.run_all()

        datas[var] = batch.get_model_vars_dataframe()

    # save data
    saver(datas)

    print("Total simulation time: {:.2f}s".format(time.time()-time_start))

    # load data
    datas = loader()

    # analyze data
    for i in range(datas):
        data = datas[i].to_numpy().flatten()

        stat_data = data[0:]
        mean = np.mean(stat_data)
        stddev = (1.96 * np.std(stat_data, ddof=1)) / np.sqrt(n_steps)
        print("Problematic contacts: {:.2f}+-{:.2f}".format(mean, stddev))

        # plt.figure()
        # plt.title("Number of problematic contacts {} customers".format(N_customers))
        # plt.scatter([j for j in range(len(data))], data)
        # plt.xlabel("Time (steps)")
        # plt.ylabel("Number of problematic contacts")
        # plt.ylim(0, max(data)+1)
        # plt.show()

    return


if __name__ == "__main__":
    main()
