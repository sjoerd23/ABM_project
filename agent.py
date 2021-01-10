from mesa import Model, Agent
from seir import Seir


class Customer(Agent):
    """Agent that describes a single customer

    Args:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of
        pos (x, y): positon of agent on grid
        seir (Enum Seir): Covid infection status according to SEIR model
        vaccinated (bool): if the customer is vaccinated or not

    Attributes:
        pos (x, y): positon of agent on grid
        radius (int): preffered distance in grid cells to other agents
        seir (Enum Seir): Covid infection status according to SEIR model
        vaccinated (bool): if the customer is vaccinated or not

    """

    def __init__(self, unique_id, model, pos, seir, vaccinated, radius=1):
        super().__init__(unique_id, model)
        self.pos = pos
        self.radius = radius
        self.seir = seir
        self.vaccinated = True

        # if vaccinated set self.seir to RECOVERED (i.e. assuem this agent can't get sick or transfer Covid)
        if vaccinated:
            # adjust total amount of EXPOSED (can be done more elegant perhaps in another way?)
            if self.seir == Seir.EXPOSED:
                self.model.n_exposed -= 1
            self.seir = Seir.RECOVERED

    def spread_covid(self):
        """Spread covid to neighbors if infected, or get infected if there are any infected
        neighbors.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=False, radius=1)
        if self.seir == Seir.INFECTED:
            for neighbor in neighbors:
                if neighbor.seir == Seir.SUSCEPTIBLE:
                    neighbor.seir = Seir.EXPOSED
                    self.model.n_exposed += 1
        elif self.seir == Seir.SUSCEPTIBLE:
            for neighbor in neighbors:
                if neighbor.seir == Seir.INFECTED:
                    self.seir = Seir.EXPOSED
                    self.model.n_exposed += 1
                    return

    def move_keep_distance(self, moore=False):
        """Moves the agent to a random new location on the grid while trying to keep distance to
        the other agents. If other agents occupies all surrounding cell, this agents will not move
        """
        # get surrounding unoccupied cells in a radius
        unoccupied_cells = self.model.get_unoccupied(self.pos, self.radius, moore)

        # randomly move to free spot if possible, else don't move
        if unoccupied_cells:
            new_cell = self.random.choice(unoccupied_cells)
            self.model.grid.move_agent(self, new_cell)

    def random_move(self, moore=False):
        """Moves the agent randomly to a new location on the grid"""
        steps = self.model.grid.get_neighborhood(self.pos, moore)
        step = self.random.choice(steps)
        self.model.grid.move_agent(self, step)

    def step(self):
        """Progress step in time. First move. Then check neighbors if any are infected -> infect
        """
        self.move_keep_distance()
        self.spread_covid()
