from mesa import Model, Agent

class Customer(Agent):

  def __init__(self, unique_id, model):
    super().__init__(unique_id, model)
