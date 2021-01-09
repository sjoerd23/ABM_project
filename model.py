from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import agent


class CovidModel(Model):
    """Model of agents (Customers) in a store

    Args:
        N_customers (int): total number of customers
        width, height (int): dimensions of grid

    Attributes:
        grid: grid of environment
        schedule: schedule for updating model to next time frame
        N_customers (int): total number of customers

    """

    def __init__(self, N_customers=20, width=20, height=20):

        # init basic properties
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        self.running = True     # needed to keep simulation running

        # Start adding customers
        self.N_customers = 0
        for i in range(N_customers):
            self.new_customer(agent.Customer)

    def is_occupied(self, pos):
        """Check if a cell is occupied (pos)"""
        cell = self.grid.get_cell_list_contents([pos])
        return len(cell) > 0

    def new_customer(self, agent_object):
        """Adds a new agent to a random location on the grid. Returns the created agent"""
        self.N_customers += 1
        new_agent = agent_object(self.N_customers, self)

        # add agent to a cell
        x, y = self.get_free_pos()
        self.grid.place_agent(new_agent, (x, y))
        self.schedule.add(new_agent)

        return new_agent

    def get_free_pos(self):
        """Find free position on grid. If there are none left, exit program"""
        if not self.grid.empties:
            print("Error! No empty cells found!")
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
