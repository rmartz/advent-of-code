from enum import Enum
from collections import namedtuple
from itertools import islice

# Hexagonal tiles can be expressed with x,y coordinates, e.g:
#       _______________________
#       |  0, -1   |  1, -1   |
#  _____|__________|__________|______
#  |  -1, 0   |   0, 0   |    1, 0  |
#  |__________|__________|__________|____
#       |   0, 1   |   1, 1   |   2, 1  |
#       |__________|__________|_________|
#            |    0, 2   |  1, 2   |
#            |___________|_________|

# Note that the offset for a direction from a tile depends on the tile's coordinates
# e.g., NE for 0,0 is 1,-1 (offset of 1, -1), but NE for 1,1 is 1,0 (offset of 0, -1)


class Direction(Enum):
    East = "e"
    West = "w"
    Northeast = "ne"
    Northwest = "nw"
    Southeast = "se"
    Southwest = "sw"


Vector = namedtuple("Vector", ["x", "y"])


def add_vectors(a: Vector, b: Vector) -> Vector:
    return Vector(x=a.x + b.x, y=a.y + b.y)


NEIGHBOR_OFFSETS = {
    Direction.East: lambda odd_row: Vector(x=1, y=0),
    Direction.West: lambda odd_row: Vector(x=-1, y=0),
    Direction.Northeast: lambda odd_row: Vector(x=(1 - odd_row), y=-1),
    Direction.Northwest: lambda odd_row: Vector(x=-odd_row, y=-1),
    Direction.Southeast: lambda odd_row: Vector(x=(1 - odd_row), y=1),
    Direction.Southwest: lambda odd_row: Vector(x=-odd_row, y=1),
}


def find_neighbor(tile, direction):
    odd_row = tile.y % 2

    offset_lambda = NEIGHBOR_OFFSETS[direction]
    return add_vectors(tile, offset_lambda(odd_row))


assert find_neighbor(Vector(x=0, y=0), Direction.East) == Vector(x=1, y=0)
assert find_neighbor(Vector(x=0, y=0), Direction.West) == Vector(x=-1, y=0)
assert find_neighbor(Vector(x=0, y=0), Direction.Northeast) == Vector(x=1, y=-1)
assert find_neighbor(Vector(x=0, y=0), Direction.Northwest) == Vector(x=0, y=-1)
assert find_neighbor(Vector(x=0, y=0), Direction.Southeast) == Vector(x=1, y=1)
assert find_neighbor(Vector(x=0, y=0), Direction.Southwest) == Vector(x=0, y=1)

assert find_neighbor(Vector(x=1, y=1), Direction.East) == Vector(x=2, y=1)
assert find_neighbor(Vector(x=1, y=1), Direction.West) == Vector(x=0, y=1)
assert find_neighbor(Vector(x=1, y=1), Direction.Northeast) == Vector(x=1, y=0)
assert find_neighbor(Vector(x=1, y=1), Direction.Northwest) == Vector(x=0, y=0)
assert find_neighbor(Vector(x=1, y=1), Direction.Southeast) == Vector(x=1, y=2)
assert find_neighbor(Vector(x=1, y=1), Direction.Southwest) == Vector(x=0, y=2)


def path_to_directions(path):
    prev = ""
    for c in path:
        if c in ["e", "w"]:
            yield Direction(prev + c)
            prev = ""
        else:
            prev = c


def directions_to_coords(directions):
    tile = Vector(x=0, y=0)
    for direction in directions:
        tile = find_neighbor(tile, direction)
    return tile


def active_values(flips):
    grid = set()
    for val in flips:
        grid ^= set([val])
    return grid


def get_neighbor_cells(grid, cell):
    for direction in Direction:
        yield find_neighbor(cell, direction)


def get_active_neighbor_count(grid, cell):
    return sum(1 for neighbor in get_neighbor_cells(grid, cell) if neighbor in grid)


def get_active_cells(grid):
    return grid


def get_accessible_inactive_cells(grid):
    def accessible_cells():
        for cell in grid:
            yield from get_neighbor_cells(grid, cell)

    return set(accessible_cells()) - grid


def get_changes(grid):
    for cell in get_active_cells(grid):
        active_neighbors = get_active_neighbor_count(grid, cell)
        if active_neighbors == 0 or active_neighbors > 2:
            yield cell

    for cell in get_accessible_inactive_cells(grid):
        active_neighbors = get_active_neighbor_count(grid, cell)
        if active_neighbors == 2:
            yield cell


def apply_changes(grid, changes):
    # Use symmetric difference assignment to invert the cells' status
    return grid ^ set(changes)


def step_simulation(grid):
    changes = get_changes(grid)
    return apply_changes(grid, changes)


def run_simulation(grid):
    while True:
        yield grid
        grid = step_simulation(grid)


def load_grid(lines):
    lines = (line.strip() for line in fp)
    line_directions = (path_to_directions(path) for path in lines)
    tiles = (directions_to_coords(directions) for directions in line_directions)
    return active_values(tiles)


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    v = next(islice(iterable, n, None), default)
    return v


with open("./data.txt", "r") as fp:
    grid = load_grid(fp)

result = nth(run_simulation(grid), 100)
print(len(get_active_cells(result)))
