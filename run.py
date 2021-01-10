import matplotlib.pyplot as plt
import numpy as np
import model
from server import server
from seir import Seir

run_server = True

if run_server:
    server.launch()
else:
    width, height = 20, 20
    N_customers = 50
    n_steps = 100

    model = model.CovidModel(N_customers, width, height)
    model.run_model(n_steps)

    # collect data from simulation
    customers_seir = model.datacollector.get_agent_vars_dataframe()

    total_exposed = []
    for step in range(n_steps):
        step_seir = customers_seir.loc[step, ["seir_status"]].to_numpy()
        total_exposed.append(int(np.sum([1 for seir in step_seir if seir == Seir.EXPOSED])))

    plt.figure()
    plt.plot([i for i in range(n_steps)], total_exposed)
    plt.show()
