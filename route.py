from core import get_distance
import numpy as np


class Position:
	"""Position object used by the A* algorithm. Stores necessary attributes for the position

    Args:
        pos (x, y): positon of grid cell
        g_score (int): score shortest path until current
		f_score (int): score current best guess

    Attributes:
        pos (x, y): positon of grid cell
        g_score (int): score shortest path until current
		f_score (int): score current best guess
		parent (Position): previous grid cell
    """
	def __init__(self, pos, g_score=np.inf, f_score=np.inf):
		self.pos = pos
		self.g_score = g_score
		self.f_score = f_score
		self.parent = None


class Route:
	"""Manages path of agent

    Args:
        model: model object this route is part of
		start (pos (x, y)): start coordinates
		goal (pos (x, y)): goal coordinates
		grid: grid of environment
		forbidden_type (list): what kind of agents are forbidden to step on
		forbidden_cells (list): cells that are to be avoided

    Attributes:
        model: model object this route is part of
		start (pos (x, y)): start coordinates
		goal (pos (x, y)): goal coordinates
		grid: grid of environment
		forbidden_type (list): what kind of agents are forbidden to step on
		forbidden_cells (list): cells that are to be avoided
		shortest (list): path between current positon and goal
		path_length (int): length of path

    """
	def __init__(self, model, start, goal, grid, forbidden_type=[], forbidden_cells=[]):
		self.model = model
		self.start = start
		self.goal = goal
		self.steps = []
		self.grid = grid
		self.forbidden_type = forbidden_type
		self.forbidden_cells = forbidden_cells
		self.shortest = self.find_shortest()
		if self.shortest:
			self.path_length = len(self.shortest)
		else:
			self.path_length = None

	def move_agent(self, agent):
		"""Moves the agent to the next step, updates the list and self.path_length

		Args:
			agent (Agent): the agent object to move

		"""
		self.model.grid.move_agent(agent, self.shortest[-1])
		self.shortest.pop()
		self.path_length -= 1

	def get_possible_neighborhood(self, pos, forbidden_cells=[]):
		"""Returns all the possible locations to walk to directly next to agent

		Args:
			pos (x, y): positon of agent on grid
			forbidden_cells (list): cells that are to be avoided

		Returns:
			possible (list): possible neighbouring cells to walk to

		"""
		possible = []
		candidates = self.grid.get_neighborhood(pos, False, radius=1)

		for candidate in candidates:

			# check if the cell position is in the forbidden location list
			if candidate in forbidden_cells:
				continue

			content_list = self.grid.get_cell_list_contents(candidate)
			valid = True
			for content in content_list:

				# check if the agent type is in the forbidden agent type list
				if type(content) in self.forbidden_type:
					valid = False
					continue
			if valid:
				possible.append(candidate)

		return possible

	def check_if_crowded(self, vision, agent_pos=None):
		"""Checks if there are people in the way during the next steps

		Args:
			vision (int): value of vision parameter (how far agent can look)

		Returns:
			score (int): score of other agents on the surrounding grid cells

		"""
		path_length = len(self.shortest)

		if path_length < vision:
			vision = path_length

		cells = self.shortest[-vision:]
		score = 0
		for cell in cells:
			correction = 0
			if agent_pos:
				distance = get_distance(agent_pos, cell)
				if distance <= self.model.AVOID_RADIUS:
					correction = self.model.AVOID_RADIUS + 1 - distance

			score += self.grid.get_score(cell) - correction

		return score

	def find_shortest(self):
		"""Find shortest route using manhattan metric """
		return self.a_star("manhattan")

	def a_star(self, distance_method):
		"""A* path finding algorithm.
		Based on pseudocode on Wikipedia: https://en.wikipedia.org/wiki/A*_search_algorithm

		Args:
			distance_method (string: ("chebyshev", "manhattan", "euclidean"), optional):
				distance metric

		"""
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
				queue = []
				while current.parent:
					queue.append(current.pos)
					current = current.parent

				return queue

			# we explored this location, so remove from the unexplored list
			unexplored.pop(current.pos)

			# check all the neighbours
			for neighbour_pos in self.get_possible_neighborhood(current.pos, self.forbidden_cells):
				# check if already exlored, if so retrieve stored data
				if neighbour_pos in explored:
					neighbour = explored[neighbour_pos]
				else:

					# not explored yet. Create object
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
