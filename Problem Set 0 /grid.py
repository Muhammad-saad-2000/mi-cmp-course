from typing import Any, List, Tuple


class Grid:
    # Th following line defines the data type for the instance variable "__data"
    # This type hint means the "__data" is a list of lists containing any type of data 
    __data : List[List[Any]]

    def __init__(self, width: int, height: int) -> None:
        self.__data = [[None]*width for _ in range(height)]
    
    @property
    def width(self) -> int:
        return 0 if len(self.__data) == 0 else len(self.__data[0])
    
    @property
    def height(self) -> int:
        return len(self.__data)
    
    # The key used to access the grid is a tuple of two integers (x, y)
    def __getitem__(self, key: Tuple[int, int]) -> Any:
        x, y = key
        if 0 <= y < len(self.__data):
            row = self.__data[y]
            if 0 <= x < len(row):
                return row[x]
        return None
    
    # The key used to access the grid is a tuple of two integers (x, y)
    def __setitem__(self, key, value) -> None:
        x, y = key
        if 0 <= y < len(self.__data):
            row = self.__data[y]
            if 0 <= x < len(row):
                row[x] = value
    
    # This function is called whenever we convert the grid into a string
    # This is useful for printing
    def __str__(self) -> str:
        return '\n'.join(' '.join(str(cell) for cell in row) for row in self.__data)
    
    # This static method creates a grid from a list of lists
    @staticmethod
    def GridFromArray(array: List[List[Any]]) -> 'Grid':
        height = len(array)
        width = 0 if height == 0 else max(len(row) for row in array)
        grid = Grid(width, height)
        for y, row in enumerate(array):
            for x, cell in enumerate(row):
                grid[x, y] = cell
        return grid