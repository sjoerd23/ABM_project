import time
import csv
import numpy as np
import SALib
from SALib.sample import saltelli
from SALib.analyze import sobol
import pandas as pd

from model import CovidSupermarketModel
import core


def saver(dictex):
    """Save dictionary of pandas dataframes. Based on code from stackoverflow:
    https://stackoverflow.com/questions/50786266/writing-dictionary-of-dataframes-to-file.

    Args:
        dictex (dict): dict of pandas dataframes

    """
    for key, val in dictex.items():
        val.to_csv("results/data_{}.csv".format(str(key)))

    with open("results/keys_{}.txt".format(str(key)), "w") as f: #saving keys to file
        f.write(str(list(dictex.keys())))


def generate_samples(problem, var_name, distinct_samples):
    """Generate samples for var_name for given problem

    Args:
        problem (dict): dict of parameters of the model and their bounds
        var_name (string): name of parameter to vary for OFAT SA
        distinct_samples (int): number of distinct samples per parameter for OFAT SA

    Returns:
        samples (np array): array of maximal distinct_samples parameter values

    """
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
    "bounds": [[10, 150], [0, 1], [0, 20], [0, 1], [3, 7]]
    }

    # Set the repetitions, the amount of steps, and the amount of distinct values per variable
    replicates = 20
    distinct_samples = 20
    n_steps = 500

    time_start = time.time()

    # perform OFAT for each variable in problem
    for var_name in problem["names"]:

        samples = generate_samples(problem, var_name=var_name, distinct_samples=distinct_samples)

        for sample in samples:
            print("\nCalculating sample {} = {} out of \n{}".format(var_name, sample, samples))
            datas = {}
            for replicate in range(replicates):

                # run appropriate model with correct variable parameter
                # default values for the other parameters are specified in model.py in the
                # __init__ declaration of CovidSupermarketModel
                if var_name == "N_customers":
                    model = CovidSupermarketModel(floorplan, width, height, N_customers=sample)
                elif var_name == "vaccination_prop":
                    model = CovidSupermarketModel(floorplan, width, height, vaccination_prop=sample)
                elif var_name == "len_shoplist":
                    model = CovidSupermarketModel(floorplan, width, height, len_shoplist=sample)
                elif var_name == "basic_compliance":
                    model = CovidSupermarketModel(floorplan, width, height, basic_compliance=sample)
                elif var_name == "vision":
                    model = CovidSupermarketModel(floorplan, width, height, vision=sample)
                else:
                    raise ValueError("ERROR! Wrong variable name selected!")

                model.run_model(n_steps)

                datas["{}_{}_{}".format(var_name, sample, replicate)] = model.datacollector.get_model_vars_dataframe()

            # save data
            saver(datas)

    print("\nTotal simulation time: {:.2f}s".format(time.time()-time_start))

    return


if __name__ == "__main__":
    main()
