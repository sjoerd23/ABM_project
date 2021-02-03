from mesa.space import MultiGrid
from mesa.agent import Agent
from typing import Tuple
from agent import Customer, Obstacle
import core


class SuperMarketGrid(MultiGrid):
    """A MESA MultiGrid with extra options. Each cell contains a score value depending on how
    close customers are to that particular cell

    Args:
        width (int): width of grid
        height (int): height of grid
        avoid_radius (int): radius in grid units in which customers try to avoid each other
        default_score (int): default score of grid cell
        torus (boolean): if grid wraps around on edges

    Attributes:
        width (int): width of grid
        height (int): height of grid
        torus (boolean): if grid wraps around on edges
        avoid_radius (int): radius in grid units in which customers try to avoid each other
        default_score (int): default score of grid cell
        scores (dict {pos: score}): dict of grid cell score per pos

    """

    def __init__(self, width, height, avoid_radius, default_score=0, torus=False):
        super().__init__(width, height, torus)

        self.avoid_radius = avoid_radius
        self.default_score = default_score
        self.scores = {}

    def set_score(self, pos, score):
        """Assigns a new score value to a grid position

        Args:
            pos (x, y): positon of agent on grid
            score (int): score of gridd cell

        """
        self.scores[pos] = score

    def _set_score(self, agent, new_pos, score_formula):
        """Assigns a new score value to a grid position. Private function, scores should be
        handled internally

        Args:
            agent (Customer): customer object to set score for
            new_pos (x, y): new positon of agent on grid
            score_formula (lambda function): how to calculate score

        """
        neighbors = self.get_neighbors(
            new_pos, moore=False, include_center=True, radius=self.avoid_radius
        )
        safe_pos = self.get_safe_pos(neighbors, agent, new_pos)

        affected_cells = self.get_neighborhood(new_pos, moore=False, include_center=True,
                                               radius=self.avoid_radius)
        for cell in affected_cells:
            if cell not in safe_pos:
                score = score_formula(new_pos, cell)
                self.scores[cell] = score

    def get_score(self, cells):
        """Returns the score value corresponding to the given position(s)

        Args
            cells (list of pos tuples or pos tuple): (list of) cell(s) to retrieve the score from

        Returns:
            score (int): total score of cells

        """
        if type(cells) is tuple:
            cells = [cells]

        score = 0
        for cell in cells:
            if cell in self.scores:
                score += self.scores[cell]
            else:
                score += self.default_score
        return score

    def get_forbidden_cells(self, pos, radius, threshold=0, agent_on_location=True):
        """Returns all the cells with a crowded score higher than the given threshold value

        Args:
            pos (x, y): positon of agent on grid
            radius (int): radius from agent

        """
        forbidden = []
        cells = self.get_neighborhood(pos, moore=False, include_center=True, radius=radius)
        for cell in cells:
            # correct for the agent's own crowded score if there is a agent on the given location
            correction = 0
            if agent_on_location:
                distance = core.get_distance(pos, cell)
                if distance <= self.avoid_radius:
                    correction = self.avoid_radius + 1 - distance
            if self.get_score(cell) > threshold + correction:
                forbidden.append(cell)

        return forbidden

    def _add_agent_score(self, agent, new_pos):
        """Internal function: updates the crowdedness scores when agent is moving to a new cell

        Args:
            agent (Customer): customer object to add score for
            new_pos (x, y): new positon of agent on grid

        """
        score_formula = lambda pos, cell: self.avoid_radius - (
                core.get_distance(new_pos, cell, "manhattan") - 1) + self.get_score(cell)
        self._set_score(agent, new_pos, score_formula)

    def _remove_agent_score(self, agent, pos):
        """Internal function: updates the crowdedness scores when agent is moving to a new cell

        Args:
            agent (Customer): customer object to remove score for
            pos (x, y): current position of agent on grid

        """
        score_formula = lambda pos, cell: -self.avoid_radius + (
                core.get_distance(pos, cell, "manhattan") - 1) + self.get_score(cell)
        self._set_score(agent, pos, score_formula)

    def place_agent(self, agent, pos):
        """Places the agent on a given position in the grid and updates the crowdedness score

        Args:
            agent (Customer): customer object to place
            pos (x, y): position of agent on grid

        """
        super().place_agent(agent, pos)

        # update score
        if type(agent) is Customer:
            self._add_agent_score(agent, pos)

    def remove_agent(self, agent):
        """Removes an agent from the grid and updates the crowdedness score

        Args:
            agent (Customer): customer object to remove

        """
        pos = agent.pos
        super().remove_agent(agent)

        # update score
        if type(agent) is Customer:
            self._remove_agent_score(agent, pos)

    def get_safe_pos(self, neighbors, agent, pos):
        """Returns positions without any obstacles

        Args:
            neighbors (list): neighbors of agent
            agent (Customer): customer object to get safe position for
            pos (x, y): position of agent on grid

        """
        safe_pos = []
        for neighbor in neighbors:
            if type(neighbor) is Obstacle:
                delta_pos = (neighbor.pos[0] - pos[0], neighbor.pos[1] - pos[1])
                if delta_pos in core.BARRIER_DICT:
                    delta_pos_list = core.BARRIER_DICT[delta_pos]
                    real_pos = list([(pos[0] + delta_pos[0], pos[1]
                                      + delta_pos[1]) for delta_pos in delta_pos_list])
                    safe_pos += real_pos

        return safe_pos

    def move_agent(self, agent, new_pos):
        """Moves the agent and updates the crowdedness scores

        Args:
            agent (Customer): customer object to move
            new_pos (x, y): new position of agent on grid

        """
        if type(agent) is Customer:
            self._remove_agent_score(agent, agent.pos)
            self._add_agent_score(agent, new_pos)
        super().move_agent(agent, new_pos)
