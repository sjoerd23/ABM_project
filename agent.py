from mesa import Model, Agent

import route


class Customer(Agent):
    """Agent that describes a single customer

    Args:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of
        pos (x, y): positon of agent on grid
        avoid_radius (int): radius in grid units in which customers try to avoid each other
        basic_compliance (float <- [0, 1]): basic level of compliance, higher is more compliant
        len_shoplist (int <- min. 0): amount of items to place on shopping list
        patience (float <- [0, 1]): patience of agent, higher is more patient
        personal_compliance (float <- [0, 1]): personal level compliance, higher is more compliant
        vaccinated (bool): if the customer is vaccinated or not
        vision (int <- min. 3): amount of grid cells customer can see other customers

    Attributes:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of
        pos (x, y): positon of agent on grid
        is_problematic_contact (bool): if agent is currently in avoid_radius of other agent
        avoid_radius (int): radius in grid units in which customers try to avoid each other
        basic_compliance (float <- [0, 1]): basic level of compliance, higher is more compliant
        len_shoplist (int <- min. 0): amount of items to place on shopping list
        patience (float <- [0, 1]): patience of agent, higher is more patient
        patience_0 (float <- [0, 1]): patience of agent on t=0, higher is more patient
        personal_compliance (float <- [0, 1]): personal level compliance, higher is more compliant
        vaccinated (bool): if the customer is vaccinated or not
        vision (int <- min. 3): amount of grid cells customer can see other customers

    """
    EXIT = 99   # grid cell value of exit of supermarket grid

    def __init__(
        self, unique_id, model, pos, avoid_radius, basic_compliance, len_shoplist, patience,
        personal_compliance, vaccinated, vision=3
    ):
        super().__init__(unique_id, model)

        self.is_problematic_contact = False
        self.avoid_radius = avoid_radius
        self.basic_compliance = basic_compliance
        self.patience = patience
        self.patience_0 = patience  # patience op t=0
        self.personal_compliance = personal_compliance
        self.pos = pos
        self.routefinder = None
        self.shop_cor_list = []
        self.vision = vision
        self.vaccinated = vaccinated

        # adds a maximum of len_shoplist items to a shopping list
        shop_list = []
        while len(shop_list) < len_shoplist:
            shelf_list = list(self.model.coord_shelf)
            random_shop = self.random.choice(shelf_list)
            if random_shop != self.EXIT:
                shop_list.append(random_shop)

        shop_list.sort()

        # edit shoppinglist according to location ag ent was spawned in
        # 100 is the precise difference between the number used for a shelve,
        # and the number used for an empty are near a shelve
        spawn_value = int(self.model.floorplan[self.pos[0]][self.pos[1]]) \
            - self.model.SHELF_THRESHOLD

        # delete all items from shoplift that have a lower int, than spawn_value
        new_shop_list = []
        for value in shop_list:
            if spawn_value <= value:
                new_shop_list.append(value)

        for item in new_shop_list:
            cor_list = list(self.model.coord_shelf.get(item))
            self.shop_cor_list.append(self.random.choice(cor_list))

        # do a random permutation of the shopping list
        self.permute_shopping_list(max(1, int(len_shoplist/4)))

        # add the exit at the end to make sure that the exit is visited last
        exit_list = list(self.model.coord_shelf.get(self.EXIT))
        self.shop_cor_list.append(self.random.choice(exit_list))

    def get_path_multiplier(self):
        """Calculates multiplier for alternative path B

        Returns:
            total_multiplier (float <- [0, 2]): multiplier to path B cost

        """
        total_multiplier = (1 - self.patience) \
                         + (1 - self.basic_compliance) \
                         + (1 - self.personal_compliance)
        if self.vaccinated:
            total_multiplier += 1

        return total_multiplier / 2

    def permute_shopping_list(self, n_permutations):
        """Permutes the shopping list of the customer

        Args:
            n_permutations (int): number of permutations of the shopping list

        """
        if len(self.shop_cor_list) > 1:
            for i in range(n_permutations):
                index1 = self.shop_cor_list.index(self.random.choice(self.shop_cor_list))
                index2 = self.shop_cor_list.index(self.random.choice(self.shop_cor_list))
                self.shop_cor_list[index1], self.shop_cor_list[index2] = \
                    self.shop_cor_list[index2], self.shop_cor_list[index1]

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
        """Progress step in time """
        if not self.routefinder:
            self.routefinder = route.Route(
                self.model, self.pos, self.shop_cor_list[0], self.model.grid,
                forbidden_type=[Obstacle]
            )

        # check if route exists, if so move agent towards the goal
        if self.routefinder.shortest:

            # check if there are people in the way
            crowded = self.routefinder.check_if_crowded(self.vision, self.pos)
            if not crowded:

                # our path is free! move the agent to the next step
                self.routefinder.move_agent(self)

            else:

                # our path is crowded, check if goal is within vision
                if self.routefinder.path_length < self.vision:
                    if self.patience <= 0 or self.is_problematic_contact:
                        self.routefinder.move_agent(self)
                        self.patience = self.patience_0 * 0.9
                        self.patience_0 = self.patience
                    else:
                        self.patience -= 0.1
                        if self.patience < 0:
                            self.patience = 0
                else:

                    # still far away from goal
                    forbidden_cells = self.model.grid.get_forbidden_cells(self.pos, self.vision)
                    alternative_route = route.Route(
                        self.model, self.pos, self.shop_cor_list[0], self.model.grid,
                        forbidden_type=[Obstacle], forbidden_cells=forbidden_cells
                    )

                    # check if a alternative route was found
                    if alternative_route.shortest:
                        alternative_score = alternative_route.path_length \
                            * self.get_path_multiplier()
                        current_score = self.routefinder.path_length + crowded

                        if alternative_score < current_score:
                            self.routefinder = alternative_route
                            self.patience *= 0.95

                    self.routefinder.move_agent(self)

            # if checkpoint is reached remove checkpoint
            if self.routefinder.path_length == 0:
                self.routefinder = None
                self.shop_cor_list.pop(0)

            # exit point reached, remove agent
            if len(self.shop_cor_list) == 0:
                self.model.agents_to_remove.append(self)

        else:

            # if no route is found to next item on shopping list, remove item from list and try
            # to find a route to a next item in the next call to this step() function
            self.routefinder = None
            self.shop_cor_list.pop(0)

            # exit point reached, remove agent
            if len(self.shop_cor_list) == 0:
                self.model.agents_to_remove.append(self)


class Obstacle(Agent):
    """
    Agent that describes inaccesible area or shop shelf in supermarket

    Args:
        unique_id (int): a unique identifier for this agent
        type_id (int): id to identify type of shelf (products on shelf)
        model: model object this agent is part of
        pos (x, y): positon of agent on grid

    Attributes:
        unique_id (int): a unique identifier for this agent
        model: model object this agent is part of
        pos (x, y): positon of agent on grid
        type_id (int): id to identify type of shelf (products on shelf)

    """
    def __init__(self, unique_id, type_id, model, pos):
        super().__init__(unique_id, model)

        self.pos = pos
        self.type_id = type_id
