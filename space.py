from mesa.space import MultiGrid
from mesa.agent import Agent
from typing import Tuple

# define Coordinate object just like in Mesa's Grid file
Coordinate = Tuple[int, int]



class SuperMarketGrid(MultiGrid):
	"""A MESA MultiGrid with extra options. Each cell contains a score value depending on how close customers are"""

	def __init__(self, width, height, avoid_radius, default_score=0, torus=False):
		self.avoid_radius = avoid_radius
		self.default_score = default_score
		super().__init__(width, height, torus)
		self.scores = {}


	def set_score(self, pos, score):
		"""Assigns a new score value to a grid position. Private function, scores should be handled internally"""
		self.scores[pos] = score

	def get_score(self, pos):
		"""Returns the score value corresponding to the given position."""
		if pos in self.scores:
			return int(self.scores[pos])
		else:
			return int(self.default_score)

	@classmethod
	def get_distance(cls, pos1, pos2):
		"""Returns the Manhattan distance"""
		(a, b) = pos1
		(c, d) = pos2
		return abs(a - c) + abs(b - d)

	def place_agent(self, agent: Agent, pos: Coordinate):
		super().place_agent(agent, pos)

		# update score
		affected_cells = self.get_neighborhood(pos, moore=False, include_center=True, radius=self.avoid_radius)
		for cell in affected_cells:
			score = self.avoid_radius - self.get_distance(pos, cell) + self.get_score(cell)
			self.set_score(cell, score)

	def remove_agent(self, agent: Agent):
		pos = agent.pos
		super().remove_egent(agent)

		# update score
		affected_cells = self.get_neighborhood(pos, moore=False, include_center=True, radius = self.avoid_radius)
		for cell in affected_cells:
			score = self.get_score(pos) - self.avoid_radius + self.get_distance(pos, cell)
			self.set_score(cell, score)
