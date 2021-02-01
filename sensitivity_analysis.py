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
def saver(dictex, var_name):
    for key, val in dictex.items():
        val.to_csv("results/data_{}.csv".format(str(key)))

    with open("results/keys_{}.txt".format(str(key)), "w") as f: #saving keys to file
        f.write(str(list(dictex.keys())))

# https://stackoverflow.com/questions/50786266/writing-dictionary-of-dataframes-to-file
def loader(var_name):
    """Reading data from keys"""
    with open("results/keys_{}.txt".format(var_name), "r") as f:
        keys = eval(f.read())

    dictex = {}
    for key in keys:
        dictex[key] = pd.read_csv("results/data_{}.csv".format(str(key)))

    return dictex


def analyze_datas(var_name, n_steps):

    # load data
    datas = loader(var_name)

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

def generate_samples(problem, var_name, distinct_samples):

    for i, var in enumerate(problem["names"]):
        if var_name == var:
            samples = np.linspace(*problem["bounds"][i], num=distinct_samples)

            if var == "N_customers" or var == "len_shoplist" or var == "vision":
                samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)

            return samples

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
    replicates = 20
    distinct_samples = 20
    n_steps = 500

    time_start = time.time()

    var_name = "vision"

    samples = generate_samples(problem, var_name=var_name, distinct_samples=distinct_samples)

    for sample in samples:
        print("\nCalculating sample {} = {} out of \n{}".format(var_name, sample, samples))
        datas = {}
        for replicate in range(replicates):
            if var_name == "N_customers":
                model = CovidSupermarketModel(floorplan, width, height, N_customers=sample)
            elif var_name == "vaccination_prop":
                model = CovidSupermarketModel(floorplan, width, height, vaccination_prop=sample)
            elif var_name == "len_shoplist":
                model = CovidSupermarketModel(floorplan, width, height, len_shoplist=sample)
            elif var_name == "basic_compliance":
                model = CovidSupermarketModel(floorplan, width, height, basic_compliance=sample)
            elif var_name == "vision":
                # vision
                model = CovidSupermarketModel(floorplan, width, height, vision=sample)

            model.run_model(n_steps)

            datas["{}_{}_{}".format(var_name, sample, replicate)] = model.datacollector.get_model_vars_dataframe()

        # save data
        saver(datas, var_name)

    print("\nTotal simulation time: {:.2f}s".format(time.time()-time_start))

    return


if __name__ == "__main__":
    main()
