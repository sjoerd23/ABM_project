from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from space import *
import csv
import agent

from seir import Seir


class CovidModel(Model):
    """Model of agents (Customers) in a store with obstacles

    Args:
        N_customers (int): total number of customers
        width, height (int): dimensions of grid
        vaccination_prop (float between 0 and 1): proportion of customers that is vaccinated

    Attributes:
        datacollector: DataCollector object to collect data for analyzing simulation
        grid: grid of environment
        N_customers (int): total number of customers
        n_exposed (int): amount of customers EXPOSED
        n_susceptibles (int): amount of customers SUSCEPTIBLE
        schedule: schedule for updating model to next time frame
        vaccination_prop (float between 0 and 1): proportion of customers that is vaccinated

    """
    def __init__(self, N_customers=2, width=60, height=80, vaccination_prop=0, avoid_radius=3):
        super().__init__()

        # init basic properties
        self.N_customers = N_customers
        self.vaccination_prop = vaccination_prop
        self.avoid_radius = avoid_radius

        self.n_exposed = 0
        self.n_susceptibles = 0
        self.schedule = RandomActivation(self)
        self.running = True     # needed to keep simulation running

        # start adding obstacles
        grid = []
        with open("data/albert.csv", encoding='utf-8-sig', newline="") as file:
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

        self.height = len(grid[0])
        self.width = len(grid)
        self.grid = SuperMarketGrid(self.width, self.height, self.avoid_radius)

        # start adding obstacles
        counter = 0
        for i in range(self.width):
            for j in range(self.height):
                if int(grid[i][j]) != 0:
                    counter += 1
                    self.new_obstacle((i, j), grid[i][j])

        # start adding customers
        for i in range(N_customers):
            self.new_customer()

        # datacollection
        self.datacollector = DataCollector(
            model_reporters={"n_exposed": "n_exposed", "n_susceptibles": "n_susceptibles"},
            agent_reporters={"seir_status": "seir"}
        )

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
        pos = self.get_free_pos()

        # select random seir status for customer
        seir = self.random.choice([Seir.SUSCEPTIBLE, Seir.INFECTED, Seir.RECOVERED])
        if seir == Seir.EXPOSED:
            self.n_exposed += 1
        elif seir == Seir.SUSCEPTIBLE:
            self.n_susceptibles += 1

        # vaccinate this customer according to proportion vaccinated of population
        if self.vaccination_prop > self.random.random():
            vaccinated = True
        else:
            vaccinated = False

        new_agent = agent.Customer(self.next_id(), self, pos, seir, vaccinated)

        # add agent to a cell
        self.grid.place_agent(new_agent, pos)
        self.schedule.add(new_agent)
        return new_agent

    # creates agent that serves as immovable obstacle
    def new_obstacle(self, pos, type_id):
        """Adds a new agent as obstacle to a random location on the grid. Returns the created 4
        agent
        """
        new_agent = agent.Obstacle(self.next_id(), type_id, self, pos)

        # add agent to a cell
        self.grid.place_agent(new_agent, pos)

        return new_agent

    def get_free_pos(self):
        """Find free position on grid. If there are none left, exit program"""
        if not self.grid.empties:
            print("Error! No empty cells found! Lower the amount of agents or enlarge the grid")
            exit(-1)
        x, y = self.random.choice(list(self.grid.empties))
        if not self.is_occupied((x, y)):
            return (x, y)

    def run_model(self, n_steps=200):
        """Run model for n_steps"""
        for i in range(n_steps):
            self.step()

    def step(self):
        """Progress simulation by one step """
        self.schedule.step()
        self.datacollector.collect(self)
