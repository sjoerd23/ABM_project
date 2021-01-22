from core import get_distance
import numpy as np


class Position:
	def __init__(self, pos, g_score=np.inf, f_score=np.inf):
		self.pos = pos
		self.g_score = g_score
		self.f_score = f_score
		self.parent = None


class Route:

	def __init__(self, model, start, goal, grid, forbidden=[]):
		self.model = model
		self.start = start
		self.goal = goal
		self.steps = []
		self.grid = grid
		self.forbidden = forbidden
		self.shortest = self.find_shortest()
		self.path_length = len(self.shortest)

	def move_agent(self, agent):
		"""Moves the agent to the next step, updates the list and self.path_lenght"""
		self.model.grid.move_agent(agent, self.routefinder.shortest[-1])
		self.routefinder.shortest.pop()
		self.path_length -= 1

	def get_possible_neighborhood(self, pos):
		"""Returns all the possible locations to walk to."""
		possible = []
		candidates = self.grid.get_neighborhood(pos, False, radius=1)

		for candidate in candidates:
			content_list = self.grid.get_cell_list_contents(candidate)
			valid = True
			for content in content_list:
				if type(content) in self.forbidden:
					valid = False
					continue
			if valid:
				possible.append(candidate)

		return possible

	def check_if_crowded(self, vision, agent_pos=None):
		"""Checks if there are people in the way during the next x steps"""
		path_length = len(self.shortest)

		if path_length < vision:
			vision = path_length
		print("Hele route", self.shortest)
		cells = self.shortest[-vision:-1]
		print("Cells", cells)
		score = self.grid.get_score(cells)
		print(cells, score)
		# score is always 3 because agent own score
		return score != 3

	def find_shortest(self):
		print("Trying to find route from {} to {}".format(self.start, self.goal))
		return self.a_star("manhattan")

	def avoid(self, avoid_cells):
		# TODO implement function
		return None


	def a_star(self, distance_method):
		"""A* path finding algorithm.
		Based on pseudocode on Wikipedia: https://en.wikipedia.org/wiki/A*_search_algorithm"""
		start_object = Position(self.start, 0, get_distance(self.start, self.goal))
		explored = {self.start: start_object}
		unexplored = {self.start: start_object}

		# keep exploring until destination found or no tiles left to explore
		while unexplored:
			minimum = min(unexplored.values(), key=lambda x: x.f_score)
			current = self.model.random.choice([val for val in unexplored.values() if val.f_score == minimum.f_score])

			# check if we reached the destination
			if current.pos == self.goal:
				# found goal, reconstruct the most efficient route
				queue = [current.pos]
				while current.parent:
					current = current.parent
					queue.append(current.pos)
				return queue

			# we explored this location, so remove from the unexplored list
			unexplored.pop(current.pos)

			# check all the neighbours
			for neighbour_pos in self.get_possible_neighborhood(current.pos):
				if neighbour_pos in explored:
					neighbour = explored[neighbour_pos]
				else:
					explored[neighbour_pos] = Position(neighbour_pos)
					neighbour = explored[neighbour_pos]

				tentative_g_score = current.g_score + get_distance(current.pos, neighbour.pos, distance_method)
				if tentative_g_score < neighbour.g_score:
					# better score, save new calculated score
					neighbour.g_score = tentative_g_score
					neighbour.f_score = tentative_g_score + get_distance(neighbour.pos, self.goal, distance_method)
					neighbour.parent = current
					if neighbour.pos not in unexplored:
						unexplored[neighbour.pos] = neighbour
