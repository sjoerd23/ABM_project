from mesa.space import MultiGrid
from mesa.agent import Agent
from typing import Tuple
from agent import Customer, Obstacle
import core


# define Coordinate object just like in Mesa's Grid file
Coordinate = Tuple[int, int]


class SuperMarketGrid(MultiGrid):
    """A MESA MultiGrid with extra options. Each cell contains a score value depending on how close customers are"""

    def __init__(self, width, height, avoid_radius, default_score=0, torus=False):
        super().__init__(width, height, torus)

        self.avoid_radius = avoid_radius
        self.default_score = default_score
        self.scores = {}

    def _set_score(self, agent, new_pos, score_formula):
        """Assigns a new score value to a grid position. Private function, scores should be handled internally"""
        neighbors = self.get_neighbors(
            new_pos, moore=False, include_center=True, radius=self.avoid_radius
        )
        safe_pos = self.get_safe_pos(neighbors, agent, new_pos)

        affected_cells = self.get_neighborhood(new_pos, moore=False, include_center=True, radius=self.avoid_radius)
        for cell in affected_cells:
            if cell not in safe_pos:
                score = score_formula(new_pos, cell)
                self.scores[cell] = score

    def get_score(self, *cells):
        """Returns the score value corresponding to the given position."""
        score = 0
        for cell in cells:
            if cell in self.scores:
                score += self.scores[cell]
            else:
                score += self.default_score
        return score

    def get_safe_pos(self, neighbors, agent, pos):
        safe_pos = []
        for neighbor in neighbors:
            if type(neighbor) is Obstacle:
                delta_pos = (neighbor.pos[0] - pos[0], neighbor.pos[1] - pos[1])
                if delta_pos in core.BARRIER_DICT:
                    delta_pos_list = core.BARRIER_DICT[delta_pos]
                    real_pos = list([(pos[0] + delta_pos[0], pos[1] + delta_pos[1]) for delta_pos in delta_pos_list])
                    safe_pos += real_pos

        return safe_pos

    def _add_agent_score(self, agent, new_pos):
        score_formula = lambda pos, cell: self.avoid_radius - core.get_distance(new_pos, cell, "manhattan") + self.get_score(cell)
        self._set_score(agent, new_pos, score_formula)

    def _remove_agent_score(self, agent, pos):
        score_formula = lambda pos, cell: -self.avoid_radius + core.get_distance(pos, cell, "manhattan") + self.get_score(cell)
        self._set_score(agent, pos, score_formula)

    def place_agent(self, agent: Agent, pos: Coordinate):
        super().place_agent(agent, pos)

        # update score
        if type(agent) is Customer:
            self._add_agent_score(agent, pos)

    def remove_agent(self, agent: Agent):
        pos = agent.pos
        super().remove_agent(agent)

        # update score
        if type(agent) is Customer:
            self._remove_agent_score(agent, pos)

    def move_agent(self, agent: Agent, new_pos: Coordinate):
        if type(agent) is Customer:
            self._remove_agent_score(agent, agent.pos)
            self._add_agent_score(agent, new_pos)
        super().move_agent(agent, new_pos)
