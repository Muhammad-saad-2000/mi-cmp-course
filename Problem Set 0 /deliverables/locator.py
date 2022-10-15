from typing import Any, Set, Tuple
from grid import Grid
import utils

def locate(grid: Grid, item: Any) -> Set[Tuple[int,int]]:
    '''
    This function takes a 2D grid and an item
    It should return a list of (x, y) coordinates that specify the locations that contain the given item
    To know how to use the Grid class, see the file "grid.py"  
    '''
    item_locations = set()
    for y in range(grid.height):
        for x in range(grid.width):
            grid_item = grid[x, y]
            if grid_item == item:
                item_locations.add((x, y))
    return item_locations