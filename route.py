import numpy as np


def get_distance(start, end, d="manhattan"):
	(a1, a2) = start
	(b1, b2) = end

	if d is "chebyshev":
		return max([abs(a1 - b1), abs(a2 - b2)])  # Chebyshev distance
	elif d is "manhattan":
		return abs(a1 - b1) + abs(a2 - b2)
	elif d is "euclidean":
		return ((a1-b1)**2 + (a2 - b2)**2)**.5
	else:
		raise ValueError("Type {} is not a supported distance type, try chebyshev, manhattan or euclidean.".format(d))


class Position:
	def __init__(self, pos, g_score=np.inf, f_score=np.inf):
		self.pos = pos
		self.g_score = g_score
		self.f_score = f_score
		self.parent = None


class Route:

	def __init__(self, start, goal, grid, forbidden=[]):
		self.start = start
		self.goal = goal
		self.steps = []
		self.grid = grid
		self.forbidden = forbidden

		print("Trying to find route from {} to {}".format(self.start, self.goal))
		self.shortest = self.find_shortest()

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

	def find_shortest(self):
		self.a_star()

	def find_safest(self):
		self.a_start()

	def a_star(self, distance_method):
		"""A* path finding algorithm.
		Based on pseudocode on Wikipedia: https://en.wikipedia.org/wiki/A*_search_algorithm"""
		start_object = Position(self.start, 0, get_distance(self.start, self.goal))
		explored = {self.start: start_object}
		unexplored = {self.start: start_object}

		# keep exploring until destination found or no tiles left to explore
		while unexplored:
			current = min(unexplored.values(), key=lambda x: x.f_score)
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

				tentative_g_score = current.g_score + get_distance(current.pos, neighbour.pos)
				if tentative_g_score < neighbour.g_score:
					# better score, save new calculated score
					neighbour.g_score = tentative_g_score
					neighbour.f_score = tentative_g_score + get_distance(neighbour.pos, self.goal)
					neighbour.parent = current
					if neighbour.pos not in unexplored:
						unexplored[neighbour.pos] = neighbour
