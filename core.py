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
	(a1, a2) = start
	(b1, b2) = end

	if d == "chebyshev":
		return max([abs(a1 - b1), abs(a2 - b2)])
	elif d == "manhattan":
		return abs(a1 - b1) + abs(a2 - b2)
	elif d == "euclidean":
		return ((a1-b1)**2 + (a2 - b2)**2)**.5
	else:
		raise ValueError("Type {} is not a supported distance type, try chebyshev, manhattan or euclidean.".format(d))
