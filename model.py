from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import csv
import numpy as np
import time
import core

from agent import Customer, Obstacle
from space import SuperMarketGrid


def load_floorplan(map):
    """Load the floorplan of a supermarket layout specified in map"""
    grid = []
    with open(map, encoding='utf-8-sig', newline="") as file:
        reader = csv.reader(file)

        # create a list for each possible x value in the grid
        for row in reader:
            for item in row:
                grid.append([item])
            grid_len = len(grid)
            break
        for row in reader:
            for i in range(grid_len):
                grid[i].insert(0, row[i])
    return grid


class CovidSupermarketModel(Model):
    """Model of agents (Customers) in a store with obstacles

    Args:
        N_customers (int): total number of customers
        vaccination_prop (float between 0 and 1): proportion of customers that is vaccinated

    Attributes:
        datacollector: DataCollector object to collect data for analyzing simulation
        grid: grid of environment
        N_customers (int): total number of customers
        schedule: schedule for updating model to next time frame
        vaccination_prop (float between 0 and 1): proportion of customers that is vaccinated
        n_problematic_contacts (int): number of contacts violating distant rules
    """
    description = "Supermarket Covid Model.\
    Agent color represents its status: vaccinated (green), problematic contact (red), else (blue).\
    "

    def __init__(self, N_customers=100, vaccination_prop=0, avoid_radius=3):
        super().__init__()

        # init basic properties
        self.N_customers = N_customers
        self.vaccination_prop = vaccination_prop
        self.avoid_radius = avoid_radius

        self.schedule = RandomActivation(self)
        self.running = True     # needed to keep simulation running

        # start adding obstacles
        floorplan = load_floorplan("data/albert.csv")
        self.height = len(floorplan[0])
        self.width = len(floorplan)
        self.grid = SuperMarketGrid(self.width, self.height, self.avoid_radius)

        # start adding obstacles to grid
        for i in range(self.width):
            for j in range(self.height):
                if int(floorplan[i][j]) != 0:
                    self.new_obstacle((i, j), floorplan[i][j])

        # start adding customers
        self.customers = [self.new_customer() for _ in range(N_customers)]

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
        """Check if a cell or region around a cell is occupied (pos)"""
        cell = self.grid.get_cell_list_contents([pos])
        return len(cell) > 0

    def get_unoccupied(self, pos, radius, moore):
        """Returns the unoccupied cells in region around a cell"""
        neighborhood = self.grid.get_neighborhood(pos, moore, radius=radius)
        neighbors_pos = [x.pos for x in self.grid.get_neighbors(pos, moore, radius=radius)]
        return list([x for x in neighborhood if x not in neighbors_pos])

    def new_customer(self):
        """Adds a new agent to a random location on the grid. Returns the created agent"""

        # vaccinate this customer according to proportion vaccinated of population
        if self.vaccination_prop > self.random.random():
            vaccinated = True
        else:
            vaccinated = False

        pos = self.get_free_pos()
        new_agent = Customer(self.next_id(), self, pos, vaccinated, self.avoid_radius)
        self.grid.place_agent(new_agent, pos)
        self.schedule.add(new_agent)
        return new_agent

    # creates agent that serves as immovable obstacle
    def new_obstacle(self, pos, type_id):
        """Adds a new agent as obstacle to a random location on the grid. Returns the created 4
        agent
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
                safe_pos = []
                neighbors = self.grid.get_neighbors(
                    customer.pos, moore=False, include_center=True, radius=self.avoid_radius
                )
                for neighbor in neighbors:
                    if type(neighbor) is Obstacle:
                        delta_pos = (neighbor.pos[0] - customer.pos[0], neighbor.pos[1] - customer.pos[1])
                        if delta_pos in core.BARRIER_DICT:
                            delta_pos_list = core.BARRIER_DICT[delta_pos]
                            real_pos = list([(customer.pos[0] + delta_pos[0], customer.pos[1] + delta_pos[1]) for delta_pos in delta_pos_list])
                            safe_pos += real_pos

                for neighbor in neighbors:
                    if type(neighbor) is Customer:
                        if neighbor is not customer:
                            if neighbor.pos not in safe_pos:
                                if not neighbor.vaccinated:
                                    self.n_problematic_contacts += 1
                                    neighbor.is_problematic_contact = True
                            else:
                                print("Safe!")
                                print(neighbor.pos, safe_pos)

        # divide by 2, because we count contacts double
        self.n_problematic_contacts = int(self.n_problematic_contacts / 2)

    def get_free_pos(self):
        """Find free position on grid. If there are none left, exit program"""
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
        self.schedule.step()
        print("Total time: {:2f}s".format(time.time()-time_start))

        # calculate number of problematic contacts
        self.problematic_contacts()
        self.datacollector.collect(self)
