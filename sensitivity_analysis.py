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


def analyze_datas():

    # load data
    datas = loader()

    # analyze data
    for key, value in datas.items():
        data = value.to_numpy().flatten()
        print(data)
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

def main():

    # load supermarket floorplan for simulation
    floorplan = core.load_floorplan("data/albert_excel_test.csv")
    width = len(floorplan)
    height = len(floorplan[0])

    problem = {
    "num_vars": 5,
    "names": ["N_customers", "vaccination_prop", "len_shoplist", "basic_compliance", "vision"],
    "bounds": [[10, 125], [0, 1], [0, 20], [0, 1], [3, 7]]
    }

    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 15
    distinct_samples = 20
    n_steps = 500

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

        for sample in samples:
            for replicate in range(replicates):
                if var == "N_customers":
                    model = CovidSupermarketModel(floorplan, width, height, N_customers=sample)
                # elif var == "len_shoplist":
                #     model = CovidSupermarketModel(floorplan, width, height, len_shoplist=sample)
                elif var == "basic_compliance":
                    model = CovidSupermarketModel(floorplan, width, height, basic_compliance=sample)

                model.run_model(n_steps)

                datas["{}_{}_{}".format(var, sample, replicate)] = model.datacollector.get_model_vars_dataframe()

    # save data
    saver(datas)

    print("Total simulation time: {:.2f}s".format(time.time()-time_start))

    analyze_datas()

    return


if __name__ == "__main__":
    main()
