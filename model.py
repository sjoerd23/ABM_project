from mesa import Model
from mesa.space import MultiGrid
import agent

class OurModel(Model):

	def __init__(self, N_customers, width, height):

		# init basic properties
		self.width = width
		self.height = height
		self.grid = MultiGrid(self.width, self.height, torus=False)

		# Start adding customers
		self.N_customers = 0
		for i in range(N_customers):
			self.new_customer()

	"""Adds a new agent to a random location on the grid. Returns the created agent"""
	def new_customer(self, agent_object):
		self.N_customers += 1
		x = round(self.model.random.random() * self.width)
		y = round(self.model.random.random() * self.height)

		new_agent = agent_object(self.N_customers, self)
		self.grid.place_agent(new_agent, (x, y))

		return new_agent
