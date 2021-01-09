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

    def new_customer(self, agent_object):
        """Adds a new agent to a random location on the grid. Returns the created agent"""
        self.N_customers += 1

        new_agent = agent_object(self.N_customers, self)

        # add agent to a cell
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        self.grid.place_agent(new_agent, (x, y))
        self.schedule.add(new_agent)

        return new_agent

    def run_model(self, n_steps=200):
        """Run model for n_steps"""
        for i in range(n_steps):
            self.step()

    def step(self):
        """Progress simulation by one step """
        self.schedule.step()
