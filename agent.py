from mesa import Model, Agent


class Customer(Agent):
    """Agent that describes a single customer

    Args:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of
        pos (x, y): positon of agent on grid
        vaccinated (bool): if the customer is vaccinated or not

    Attributes:
        pos (x, y): positon of agent on grid
        vaccinated (bool): if the customer is vaccinated or not

    """
    def __init__(self, unique_id, model, pos, vaccinated, avoid_radius):
        super().__init__(unique_id, model)

        self.avoid_radius = avoid_radius
        self.pos = pos
        self.vaccinated = True

    def move_keep_distance(self, moore=False):
        """Moves the agent to a random new location on the grid while trying to keep distance to
        the other agents. If other agents occupies all surrounding cell, this agents will not move
        """
        # get surrounding unoccupied cells in a radius
        unoccupied_cells = self.model.get_unoccupied(self.pos, 1, moore)

        # find possible cells to step to where no other customer is close
        possible_cells = []
        for cell in unoccupied_cells:
            score = self.model.grid.get_score(cell)

            # each agent creates a score of 2 around itself
            if score <= 2:
                possible_cells.append(cell)

        if possible_cells:
            new_cell = self.random.choice(possible_cells)
            self.model.grid.move_agent(self, new_cell)
        elif unoccupied_cells:
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


class Obstacle(Agent):
    """
    Agent that describes inaccesible area or shop shelf in supermarket

    Args:
        unique_id (int): a unique identifier for this agent
        type_id (int): id to identify type of shelf (products on shelf)
        model: model object this agent is part of
        pos (x, y): positon of agent on grid

    Attributes:
        pos (x, y): positon of agent on grid
        type_id (int): id to identify type of shelf (products on shelf)
    """
    def __init__(self, unique_id, type_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos
        self.type_id = type_id
