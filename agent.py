from mesa import Model, Agent
import route
import numpy
import random

EXIT = 99
SHELF_THRES = 100

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
        is_problematic_contact (bool): if agent is currently in avoid_radius of other agent

    """


    def __init__(self, unique_id, model, pos, vaccinated, avoid_radius, shop_len = 1):
        super().__init__(unique_id, model)

        self.avoid_radius = avoid_radius
        self.pos = pos
        self.vaccinated = vaccinated
        self.is_problematic_contact = False
        self.routefinder = None
        self.shop_cor_list = []

        # adds a maximum of 5 items to a shopping list
        shop_list = []

        #comment this out for easy routes directly to end

        while len(shop_list) < shop_len:
            shelf_list = list(self.model.coord_shelf)
            random_shop = random.choice(shelf_list)
            if random_shop != EXIT:
                shop_list.append(random_shop)

        # adds the
        shop_list.append(EXIT)
        shop_list.sort()

        # edit shoppinglist according to location agent was spawned in
        # 100 is the precise difference between the number used for a shelve, and the number used for an empty are near a shelve
        spawn_value = int(self.model.floorplan[self.pos[0]][self.pos[1]]) - SHELF_THRES

        # delete all items from shoplift that have a lower int, than spawn_value

        #needs improvement but for now I didn't want to loop and remove
        new_shop_list = []

        for value in shop_list:
            if spawn_value <= value:
                new_shop_list.append(value)

        # print("old list", shop_list)
        # print("spawn value", spawn_value)
        # print("new_list", new_shop_list)

        for item in new_shop_list:
            cor_list = list(self.model.coord_shelf.get(item))

            self.shop_cor_list.append(random.choice(cor_list))


        # every agent get's a shopping list.

        #


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
        if not self.routefinder:
            self.routefinder = route.Route(self.pos, self.shop_cor_list[0], self.model.grid, forbidden=[Obstacle])

        # print("print shoplist", self.shop_cor_list)
        # print("printshorest", self.routefinder.shortest)
        # check if route exists, if so move agent towards the goal
        if self.routefinder.shortest:
            self.model.grid.move_agent(self, self.routefinder.shortest[-1])
            self.routefinder.shortest.pop()

            # if checkpoint is reached remove checkpoint
            if len(self.routefinder.shortest) == 0:
                self.routefinder = None
                self.shop_cor_list.pop(0)

            if len(self.shop_cor_list) == 0:
                self.model.exit_list.append(self)
                print("exit list", self.model.exit_list)



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
