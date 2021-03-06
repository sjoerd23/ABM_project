import numpy as np
import time
import copy
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

import core
from agent import Customer, Obstacle
from space import SuperMarketGrid


class CovidSupermarketModel(Model):
    """Model of agents (Customers) in a supermarket

    Args:
        floorplan (2D list): grid with corresponding values of input map from supermarket
        width (int): width of grid
        height (int): height of grid
        N_customers (int <- min. 0): total number of customers
        vaccination_prop (float <- [0, 1]): proportion of customers that is vaccinated
        len_shoplist (int <- min. 0): amount of items to place on shopping list
        basic_compliance (float <- [0, 1]): basic level of compliance, higher is more compliant
        vision (int <- min. 3): amount of grid cells customer can see other customers

    Attributes:
        floorplan (2D list): grid with corresponding values of input map from supermarket
        width (int): width of grid
        height (int): height of grid
        N_customers (int <- min. 0): total number of customers
        vaccination_prop (float <- [0, 1]): proportion of customers that is vaccinated
        len_shoplist (int <- min. 0): amount of items to place on shopping list
        basic_compliance (float <- [0, 1]): basic level of compliance, higher is more compliant
        vision (int <- min. 3): amount of grid cells customer can see other customers
        agents_to_remove (list): agents that will be removed after a single simulation step
        datacollector: DataCollector object to collect data for analyzing simulation
        grid: grid of environment
        heatgrid: grid of environment for heat map
        n_problematic_contacts (int): number of contacts violating distant rules
        running (boolean): if true keeps the simulation running
        schedule: schedule for updating model to next time frame

    """
    description = "Supermarket Covid Model.\
    Agent color represents its status: vaccinated (green), problematic contact (red), else (blue).\
    "
    SHELF_THRESHOLD = 100   # special value for which there is difference between shelf and area
    AVOID_RADIUS = 3        # 3 corresponds to a distance keeping of 1.5 meter

    def __init__(
        self, floorplan, width, height, N_customers=100, vaccination_prop=0.2, len_shoplist=10,
        basic_compliance=0.2, vision=3
    ):
        super().__init__()

        # init basic properties
        self.floorplan = floorplan
        self.width = width
        self.height = height
        self.N_customers = N_customers
        self.vaccination_prop = vaccination_prop
        self.len_shoplist = len_shoplist
        self.basic_compliance = basic_compliance
        self.vision = vision

        self.agents_to_remove = []
        self.customers = []
        self.coord_shelf = {}
        self.coord_start_area = []
        self.exit_list = []

        self.schedule = RandomActivation(self)
        self.running = True     # needed to keep simulation running

        self.grid = SuperMarketGrid(self.width, self.height, self.AVOID_RADIUS)

        # add obstacles to grid
        for i in range(self.width):
            for j in range(self.height):
                if int(self.floorplan[i][j]) <= self.SHELF_THRESHOLD:
                    self.new_obstacle((i, j), self.floorplan[i][j])

        # adjacency matrix
        adjacency = [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if not (i == j == 0)]

        # get the coordinates of all the shelves,
        # and the coordinates of accesible spaces around them to a dict
        for i in range(self.width):
            for j in range(self.height):
                shelf_val = int(self.floorplan[i][j])
                if shelf_val < self.SHELF_THRESHOLD:
                    free_space = False
                    for cor in adjacency:
                        if int(self.floorplan[i + cor[0]][j + cor[1]]) > self.SHELF_THRESHOLD:
                            if shelf_val in self.coord_shelf.keys():
                                self.coord_shelf[shelf_val].add((i + cor[0], j + cor[1]))
                            else:
                                self.coord_shelf.update({shelf_val: {(i + cor[0], j + cor[1])}})

                            free_space = True
                    if not free_space:
                        print("Error unaccesible shelf cell! ", i, j, self.floorplan[i][j])

                if shelf_val == 101:
                    self.coord_start_area.append((i, j))

        # use heatgrid
        self.heatgrid = copy.deepcopy(self.grid)

        # start adding customers
        for _ in range(N_customers):
            self.add_customer(self.get_free_pos())

        # calculate initial amount of problematic contacts
        self.n_problematic_contacts = 0
        self.problematic_contacts()

        # datacollection
        self.datacollector = DataCollector(
            model_reporters={"n_problematic_contacts": "n_problematic_contacts"},
            agent_reporters={}
        )
        self.datacollector.collect(self)

    def is_occupied(self, pos):
        """Check if a cell or region around a cell is occupied (pos)

        Args:
            pos (x, y): positon of agent on grid

        Returns:
            Boolean: true if occupied, else false
        """
        cell = self.grid.get_cell_list_contents([pos])
        return len(cell) > 0

    def get_unoccupied(self, pos, radius, moore):
        """Returns the unoccupied cells in region around a cell

        Args:
            pos (x, y): positon of agent on grid
            radius (int): radius from center to get unoccupied cells
            moore (boolean): if true use moore neighborhood, else van Neumann

        Returns:
            list: list of unoccupied cells

        """
        neighborhood = self.grid.get_neighborhood(pos, moore, radius=radius)
        neighbors_pos = [x.pos for x in self.grid.get_neighbors(pos, moore, radius=radius)]

        return list([x for x in neighborhood if x not in neighbors_pos])

    def add_customer(self, pos):
        """Adds a new agent to a random location on the grid. Returns the created agent

        Args:
            pos (x, y): positon of agent on grid

        """
        # vaccinate this customer according to proportion vaccinated of population
        if self.vaccination_prop > self.random.random():
            vaccinated = True
        else:
            vaccinated = False

        new_agent = Customer(
            self.next_id(), self, pos, self.AVOID_RADIUS, self.basic_compliance, self.len_shoplist,
            self.random.random(), self.random.random(), vaccinated, vision=self.vision
        )
        self.grid.place_agent(new_agent, pos)
        self.schedule.add(new_agent)
        self.customers.append(new_agent)

    def get_entrance_pos(self):
        "Check if there is a free pos the agent can enter the store in when a place frees up"
        free_pos = []
        for pos in self.coord_start_area:
            if not self.is_occupied(pos):
                free_pos.append(pos)
        if free_pos:
            return self.random.choice(free_pos)

        return None

    def new_obstacle(self, pos, type_id):
        """Adds a new agent as obstacle to a random location on the grid

        Args:
            pos (x, y): positon of agent on grid
            type_id (int): shelf id for obstacle

        Returns:
            new_agent (Obstacle): newly created Obstacle object
        """
        new_agent = Obstacle(self.next_id(), type_id, self, pos)
        self.grid.place_agent(new_agent, pos)

        return new_agent

    def problematic_contacts(self):
        """Calculates the total amount of problematic contacts """

        # reset variables
        self.n_problematic_contacts = 0
        for customer in self.customers:
            customer.is_problematic_contact = False

        # count problematic contacts. If one of the agents is vaccinated, do not count as a contact
        for customer in self.customers:
            if not customer.vaccinated:
                neighbors = self.grid.get_neighbors(
                    customer.pos, moore=False, include_center=True, radius=self.AVOID_RADIUS
                )
                safe_pos = self.grid.get_safe_pos(neighbors, customer, customer.pos)

                for neighbor in neighbors:
                    if type(neighbor) is Customer:
                        if neighbor is not customer:
                            if neighbor.pos not in safe_pos:
                                if not neighbor.vaccinated:
                                    self.n_problematic_contacts += 1

                                    neighbor.is_problematic_contact = True

                                    if not self.heatgrid[neighbor.pos[0]][neighbor.pos[1]]:
                                        self.heatgrid[neighbor.pos[0]][neighbor.pos[1]] = 0.5
                                    else:
                                        self.heatgrid[neighbor.pos[0]][neighbor.pos[1]] += 0.5

        # divide by 2, because we count contacts double
        self.n_problematic_contacts = int(self.n_problematic_contacts / 2)

    def get_free_pos(self):
        """Find free position on grid. If there are none left, exit program

        Returns:
            pos (x, y): free positon on grid

        """
        if not self.grid.empties:
            print("Error! No empty cells found! Lower the amount of agents or enlarge the grid")
            exit(-1)
        x, y = self.random.choice(list(self.grid.empties))
        if not self.is_occupied((x, y)):
            return x, y

    def run_model(self, n_steps=200):
        """Run model for n_steps"""
        for i in range(n_steps):
            self.step()

    def step(self):
        """Progress simulation by one step """
        time_start = time.time()

        # let new agents enter if there are less agents than N_customers
        if len(self.customers) < self.N_customers:
            new_pos = self.get_entrance_pos()
            if new_pos:
                self.add_customer(new_pos)

        self.schedule.step()

        # remove agents from environment
        if self.agents_to_remove:
            for agent in self.agents_to_remove:
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                self.customers.remove(agent)
            self.agents_to_remove = []

        # calculate number of problematic contacts
        self.problematic_contacts()
        self.datacollector.collect(self)
