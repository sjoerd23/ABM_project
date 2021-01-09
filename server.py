from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule

import agent
import model

def agent_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Color": "blue",
                 "Filled": "true",
                 "Layer": 0,
                 "r": 0.5,
                 "text": agent.unique_id,
                 "text_color": "white"}

    return portrayal


# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
width, height = 20, 20
grid = CanvasGrid(agent_portrayal, width, height, 500, 500)


# Create the server, and pass the grid and the graph
N_customers = 150
server = ModularServer(model.CovidModel,
                       [grid],
                       "Indoor Covid model",
                       {"N_customers": N_customers, "width": width, "height": height})

server.port = 8521

# moved server.launch() to run.py. Gave some issues for me if I placed it here
