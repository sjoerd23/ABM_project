from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from collections import defaultdict

import model
import core
from agent import Customer, Obstacle


class CanvasGrid2(CanvasGrid):
    """Overrides the default canvas grid to also handle empty cells"""
    def __init__(self, portrayal_method, grid_width, grid_height, canvas_width=500, canvas_height=500):
        super().__init__(portrayal_method, grid_width, grid_height, canvas_width, canvas_height)

    def render(self, model):
        grid_state = defaultdict(list)
        for x in range(model.grid.width):
            for y in range(model.grid.height):
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                score = model.grid.get_score((x, y))
                if not cell_objects:

                    portrayal = {"Shape": "square", "Color": "white", "Filled": "true", "Layer": 0,
                                 "r": 0.5, "text": "({0}, {1}) - {2}".format(x, y, score), "text_color": "black", "x": x, "y": y}
                    grid_state[portrayal["Layer"]].append(portrayal)
                for obj in cell_objects:
                    portrayal = self.portrayal_method(obj)
                    if portrayal:
                        portrayal["x"] = x
                        portrayal["y"] = y
                        grid_state[portrayal["Layer"]].append(portrayal)
        return grid_state


def agent_portrayal(agent):
    portrayal = {}
    if type(agent) == Customer:
        portrayal = {"Shape": "arrowHead",
                     "Filled": "true",
                     "color": "yellow",
                     "Layer":   0,
                     "heading_x": (-1, -1),
                     "heading_y": -1,
                     "scale": 0.5,
                     "text_color": "white"}

        if agent.vaccinated:
            portrayal["Color"] = "green"
        else:
            if agent.is_problematic_contact:
                portrayal["Color"] = "red"
            else:
                portrayal["Color"] = "blue"

    elif type(agent) == Obstacle:
        portrayal = {"Shape": "rect",
                     "Color": "black",
                     "Filled": "true",
                     "Layer": 0,
                     "w": 1,
                     "h": 1,
                     "text_color": "white"}
    return portrayal



#
#
# def agent_portrayal(agent):
#     portrayal = {}
#     if type(agent) == Customer:
#         portrayal = {"Shape": "circle",
#                      "Filled": "true",
#                      "color": "yellow",
#                      "Layer":   0,
#                      "r": 0.9,
#                      "text_color": "white"}
#         if agent.vaccinated:
#             portrayal["Color"] = "green"
#         else:
#             if agent.is_problematic_contact:
#                 portrayal["Color"] = "red"
#             else:
#                 portrayal["Color"] = "blue"
#
#     elif type(agent) == Obstacle:
#         portrayal = {"Shape": "rect",
#                      "Color": "black",
#                      "Filled": "true",
#                      "Layer": 0,
#                      "w": 1,
#                      "h": 1,
#                      "text_color": "white"}
#     return portrayal

# load supermarket floorplan for simulation
floorplan = core.load_floorplan("data/albert_excel_test.csv")
width = len(floorplan)
height = len(floorplan[0])

grid = CanvasGrid2(agent_portrayal, width, height, 800, 600)

# no chart for the moment. Just leaving it here, because then it will be easy to make a new chart
# for different variables
chart = ChartModule(
    [{"Label": "n_problematic_contacts", "Color": "Blue"}],
    data_collector_name="datacollector"
)

# Create the server, and pass the grid and the graph
customer_slider = UserSettableParameter(
    'slider', 'Number of customers', value=100, min_value=1, max_value=500, step=1
)
len_shoplist_slider = UserSettableParameter(
    'slider', 'Number of items on shopping list of customer', value=5, min_value=0, max_value=25,
    step=1
)
basic_compliance_slider = UserSettableParameter(
    'slider', 'Basic compliance of customers', value=0, min_value=0, max_value=1, step=0.01
)
vaccinated_slider = UserSettableParameter(
    'slider', 'Proportion of vaccinated customers', value=0, min_value=0, max_value=1, step=0.01
)
model_params = {
    "floorplan": floorplan,
    "width": width,
    "height": height,
    "N_customers": customer_slider,
    "vaccination_prop": vaccinated_slider,
    "len_shoplist": len_shoplist_slider,
    "basic_compliance": basic_compliance_slider
}

server = ModularServer(model.CovidSupermarketModel,
                       [grid, chart],
                       "Supermarket Covid Model",
                       model_params)

server.port = 8521

# moved server.launch() to run.py. Gave some issues for me if I placed it here
