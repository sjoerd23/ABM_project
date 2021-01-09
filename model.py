from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
import agent

class OurModel(Model):

	def __init__(self, N_customers=20, width=20, height=20):

		# init basic properties
		self.width = width
		self.height = height
		self.grid = MultiGrid(self.width, self.height, torus=False)

		# Start adding customers
		self.N_customers = 0
		for i in range(N_customers):
			self.new_customer(agent.Customer)

	"""Adds a new agent to a random location on the grid. Returns the created agent"""
	def new_customer(self, agent_object):
		self.N_customers += 1
		
		x = self.random.randint(0, self.width - 1)
		y = self.random.randint(0, self.height - 1)

		new_agent = agent_object(self.N_customers, self)
		self.grid.place_agent(new_agent, (x, y))

		return new_agent

