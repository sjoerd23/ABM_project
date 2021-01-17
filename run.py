import matplotlib.pyplot as plt
import numpy as np
import time
import model
from server import server

# set to true if you want to run the model through a server with visualisation. Run with: mesa runserver
# set to false if you don't want to run the server and like to analyze the data instead. Run with: python run.py
run_server = True

if run_server:
    server.launch()
else:

    # deprecated code, does not work for the moment. Maybe move thise analyzing outside the
    # vizualization to a Jupyter Notebook? Also nice for interactive purposes for possible users
    # (see grading scheme)
    width, height = 80, 80
    N_customers = 100
    n_steps = 200

    time_start = time.time()
    model = model.CovidSupermarketModel(N_customers, width, height)
    model.run_model(n_steps)
    time_end = time.time()

    print("Total simulation time: {:.2f}".format(time_end-time_start))
    print("Data processing")

    # collect data from simulation
    customers_seir = model.datacollector.get_agent_vars_dataframe()

    total_exposed = []
    total_susceptible = []
    for step in range(n_steps):
        step_seir = customers_seir.loc[step, ["seir_status"]].to_numpy()
        total_exposed.append(int(np.sum([1 for seir in step_seir if seir == Seir.EXPOSED])))
        total_susceptible.append(int(np.sum([1 for seir in step_seir if seir == Seir.SUSCEPTIBLE])))

    t_steps = [i for i in range(n_steps)]
    plt.figure()
    plt.plot(t_steps, total_exposed, label="Exposed")
    plt.plot(t_steps, total_susceptible, label="Susceptible")
    plt.xlabel("Time step [-]")
    plt.ylabel("Amount [-]")
    plt.legend()
    plt.show()
