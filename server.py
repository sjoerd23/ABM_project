from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

import model
from agent import Customer
from seir import Seir


def agent_portrayal(agent):
    portrayal = {}
    if type(agent) == Customer:
        portrayal = {"Shape": "circle",
                     "Color": "blue",
                     "Filled": "true",
                     "Layer": 0,
                     "r": 0.5,
                     "text": agent.unique_id,
                     "text_color": "white"}

        if agent.seir == Seir.SUSCEPTIBLE:
             portrayal["Color"] = "green"
        elif agent.seir == Seir.EXPOSED:
             portrayal["Color"] = "yellow"
        elif agent.seir == Seir.INFECTED:
             portrayal["Color"] = "red"
        elif agent.seir == Seir.RECOVERED:
             portrayal["Color"] = "black"

    return portrayal

# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
width, height = 50, 50
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)

# issue: all data start at (0, 0), eventhough at t=0, n_susceptibles > 0
chart = ChartModule(
    [{"Label": "n_susceptibles", "Color": "Blue"}, {"Label": "n_exposed", "Color": "Black"}],
    data_collector_name="datacollector"
)

# Create the server, and pass the grid and the graph
N_customers = 100
server = ModularServer(model.CovidModel,
                       [grid, chart],
                       "Indoor Covid model",
                       {"N_customers": N_customers, "width": width, "height": height})

server.port = 8521

# moved server.launch() to run.py. Gave some issues for me if I placed it here
