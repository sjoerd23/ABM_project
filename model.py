from mesa import Model
from mesa.space import MultiGrid

class OurModel(Model):

	def __init__(self, N_customers, width, height):
		self.N_customers = N_customers
		self.grid = MultiGrid(self.width, self.height, torus=False)

	def customer_leaves(self):
		return

	def customer_enters(self):
		return
