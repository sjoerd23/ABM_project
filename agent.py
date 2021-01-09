from mesa import Model, Agent


class Customer(Agent):
    """Agent that describes a single customer

    Args:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of

    Attributes:

    """

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.pos = pos

    def move_keep_distance(self):
        """Moves the agent to a random new location on the grid while trying to keep distance to
        the other agents. If other agents occupies all surrounding cell, this agents will not move
        """
        # get surrounding cells and check if occupied
        neighbor_cells = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        possible_steps = [x for x in neighbor_cells if not self.model.is_occupied(x)]

        # randomly move to free spot if possible
        if possible_steps:
            new_cell = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_cell)
        else:
            # dont move, stand still
            self.model.grid.move_agent(self, self.pos)

            # force moving to a neighboring cell, even when already occupied by another agent
            # new_cell = self.random.choice(neighbor_cells)


    def random_move(self):
        """Moves the agent randomly to a new location on the grid"""
        steps = self.model.grid.get_neighborhood(self.pos, moore=True)
        step = self.random.choice(steps)
        self.model.grid.move_agent(self, step)

    def step(self):
        "Progress step in time"
        self.move_keep_distance()
