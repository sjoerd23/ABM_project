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



class CanvasHeatGrid(CanvasGrid):
    """Overrides the default canvas grid to also handle empty cells"""
    def __init__(self, portrayal_method, grid_width, grid_height, canvas_width=500, canvas_height=500):
        super().__init__(portrayal_method, grid_width, grid_height, canvas_width, canvas_height)

    def render(self, model):
        grid_state = defaultdict(list)

        high_cont_val = 0

        # determine what the maximum value of problematic contacts is which can be used for scaling the colours of a heatmap.
        for x in range(model.heatgrid.width):
            for y in range(model.heatgrid.height):
                if isinstance(model.heatgrid[x][y], float):
                    if model.heatgrid[x][y] > high_cont_val:
                        high_cont_val = model.heatgrid[x][y]

        for x in range(model.heatgrid.width):
            for y in range(model.heatgrid.height):
                if isinstance(model.heatgrid[x][y], float):

                    cell_color = color_gradient(high_cont_val, model.heatgrid[x][y])
                    print(cell_color, "cell color")
                    portrayal = {"Shape": "rect", "Color": cell_color, "Filled": "true", "Layer": 0,
                                 "w": 1, "h": 1, "text": model.heatgrid[x][y], "text_color": "black", "x": x, "y": y}
                    grid_state[portrayal["Layer"]].append(portrayal)
                else:
                    cell_objects = model.heatgrid.get_cell_list_contents([(x, y)])

                    if not cell_objects:

                        portrayal = {"Shape": "square", "Color": "white", "Filled": "true", "Layer": 0,
                                     "r": 0.5, "text": "({0}, {1}) - {2}".format(x, y, y), "text_color": "black", "x": x, "y": y}
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
        portrayal = {"Shape": "circle",
                     "Filled": "true",
                     "color": "yellow",
                     "Layer":   0,
                     "r": 0.9,
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




color_dict = {
    0.02: "#fef5f3",
    0.04: "#fdefeb",
    0.06: "#fde8e3",
    0.08	: "#fde2dc",
    0.10	: "#fcdcd4",
    0.12	: "#fcd6cc",
    0.14	: "#fbcfc4",
    0.16	: "#fbc9bd",
    0.18	: "#fbc3b5",
    0.20	: "#fabcad",
    0.22	: "#fab6a5",
    0.24	: "#f9b09e",
    0.26	: "#f9aa96",
    0.28	: "#f8a38e",
    0.30	: "#f89d87",
    0.32	: "#f8977f",
    0.34	: "#f79077",
    0.36	: "#f78a6f",
    0.38	: "#f68468",
    0.40	: "#f67e60",
    0.42	: "#f57758",
    0.44	: "#f57150",
    0.46	: "#f56b49",
    0.48	: "#f46441",
    0.50	: "#f45e39",
    0.52	: "#f35831",
    0.54	: "#f3522a",
    0.56	: "#f34b22",
    0.58	: "#f2451a",
    0.60	: "#f23f12",
    0.62	: "#ef390c",
    0.64	: "#e8380c",
    0.66	: "#e0360c",
    0.68	: "#d8340b",
    0.70	: "#d0320b",
    0.72	: "#c9300a",
    0.74	: "#c12e0a",
    0.76	: "#b92c0a",
    0.78	: "#b22b09",
    0.80	: "#aa2909",
    0.82	: "#a22708",
    0.84	: "#9a2508",
    0.86	: "#932307",
    0.88	: "#8b2107",
    0.90	: "#831f07",
    0.92	: "#7b1d06",
    0.94	: "#741c06",
    0.96	: "#6c1a05",
    0.98	: "#641805",
    1.00	: "#5c1605"
}

#

def color_gradient(high_cont_val, cell_val):
    frac_cont = cell_val / high_cont_val

    for i in range(1, 51):
        if i * 0.02 >= frac_cont:
            color_key = i * 0.02
            print(color_key, "color key")
            return color_dict.get(round(color_key, 2))



def heat_agent_portrayal(agent):
    portrayal = {}
    if type(agent) == Obstacle:
        portrayal = {"Shape": "rect",
                     "Color": "black",
                     "Filled": "true",
                     "Layer": 0,
                     "w": 1,
                     "h": 1,
                     "text_color": "white"}
    return portrayal
# load supermarket floorplan for simulation
floorplan = core.load_floorplan("data/albert_excel_test.csv")
width = len(floorplan)
height = len(floorplan[0])

grid = CanvasGrid2(agent_portrayal, width, height, 800, 600)
heatgrid = CanvasHeatGrid(heat_agent_portrayal, width, height, 800, 600)
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
                       [grid, heatgrid, chart],
                       "Supermarket Covid Model",
                       model_params)

server.port = 8521

# moved server.launch() to run.py. Gave some issues for me if I placed it here
