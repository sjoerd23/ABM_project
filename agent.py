from mesa import Model, Agent

class Customer(Agent):

    def __init__(self, unique_id, model):
        self.grid = MultiGrid(self.width, self.height, torus=True)
        super().__init__(unique_id, model)
