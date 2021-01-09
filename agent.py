from mesa import Model, Agent

class Customer(Agent):
    """Agent that describes a single customer

    Args:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of

    Attributes:

    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def random_move(self):
        """Moves the agent randomly to a new location on the grid"""
        steps = self.model.grid.get_neighborhood(self.pos, moore=True)
        step = self.random.choice(steps)
        self.model.grid.move_agent(self, step)

    def step(self):
        "Progress step in time"
        self.random_move()
