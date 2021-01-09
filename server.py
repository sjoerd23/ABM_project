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
                 "r": 0.5}
    return portrayal


# Create a grid of 20 by 20 cells, and display it as 500 by 500 pixels
grid = CanvasGrid(agent_portrayal, 20, 20, 500, 500)


# Create the server, and pass the grid and the graph
server = ModularServer(model.OurModel,
                       [grid],
                       "WolfSheep Model",
                       {})

server.port = 8521

server.launch()
