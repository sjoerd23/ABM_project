import csv


# this dictionary containts the relative coordinates to a customer where if at the key value a
# object is placed, at those values the agent can't have problematic contacts
BARRIER_DICT = {
	(0, 1): [(0, 2), (0, 3), (-1, 2), (1, 2)],
	(1, 1): [(1, 2), (2, 1)],
	(1, 0): [(2, 1), (2, -1), (2, 0), (3, 0)],
	(1, -1): [(2, -1), (1, -2)],
	(0, -1): [(0, -2), (0, -3), (1, -2), (-1, -2)],
	(-1, -1): [(-1, -2), (-2, -1)],
	(-1, 0): [(-2, 1), (-2, -1), (-2, 0), (-3, 0)],
	(-1, 1): [(-2, 1), (-1, 2)],
	(0, 2): [(0, 3)],
	(0, -2): [(0, -3)],
	(2, 0): [(3, 0)],
	(-2, 0): [(-3, 0)]
}


def get_distance(start, end, d="manhattan"):
	"""Calculate distance between start and end using metric d

	Args:
		start (x, y): position on grid
		end (x, y): second position on grid
		d (string: ("chebyshev", "manhattan", "euclidean"), optional): distance metric

	Returns:
		distance (float): distance between start and end using metric d

	Raises:
		ValueError: if metric d is not supported
		
	"""
	(a1, a2) = start
	(b1, b2) = end

	if d == "chebyshev":
		return max([abs(a1 - b1), abs(a2 - b2)])
	elif d == "manhattan":
		return abs(a1 - b1) + abs(a2 - b2)
	elif d == "euclidean":
		return ((a1-b1)**2 + (a2 - b2)**2)**.5
	else:
		raise ValueError(
			"Type {} is not a supported distance type, try chebyshev, manhattan or euclidean."\
			.format(d)
		)


def load_floorplan(map):
    """Load the floorplan of a supermarket layout specified in map"""
    grid = []
    with open(map, encoding='utf-8-sig', newline="") as file:
        reader = csv.reader(file)

        # create a list for each possible x value in the grid
        for row in reader:
            for item in row:
                grid.append([item])
            grid_len = len(grid)
            break
        for row in reader:
            for i in range(grid_len):
                grid[i].insert(0, row[i])
    return grid
