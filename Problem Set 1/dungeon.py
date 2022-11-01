from dataclasses import dataclass
from typing import FrozenSet, Iterable
from enum import Enum

from mathutils import Direction, Point
from problem import Problem
from helpers.utils import track_call_count

# This file contains the definition for the Dungeon Scavenger problem
# In this problem, the agent can move Up, Down, Left or Right
# and it has to collect all the coins then reach the exit

# This enum represents all the possible tiles in a Dungeon map
class DungeonTile(str, Enum):
    EMPTY  = "."
    WALL   = "#"
    COIN   = "$"
    EXIT   = "E"
    PLAYER = "@"

# For the dungeon state, we use dataclass to automatically implement:
#   the constructor and to make the class immutable
# We disable the automatic equality implementation since we don't need it;
# we only need the default equality which compares objects by pointers.
# The layout contains the problem details that are unchangeable across states such as:
#   The walkable area (locations without walls) and the exit location
@dataclass(eq=False, frozen=True)
class DungeonLayout:
    __slots__ = ("width", "height", "walkable", "exit")
    width: int
    height: int
    walkable: FrozenSet[Point]
    exit: Point

# For the dungeon state, we use dataclass with frozen=True to automatically implement:
#   the constructor, the == operator, the hash function and to make the class immutable
# Now it can be added to sets and used as keys in dictionaries
# This will contain a reference to the dungeon layout and it will contain environment details that change across states such as:
#   The player location and the locations of the remaining coins 
@dataclass(frozen=True)
class DungeonState:
    __slots__ = ("layout", "player", "remaining_coins")
    layout: DungeonLayout
    player: Point
    remaining_coins: FrozenSet[Point]

    # This operator will convert the state to a string containing the grid representation of the level at the current state
    def __str__(self) -> str:
        def position_to_str(position):
            if position not in self.layout.walkable:
                return DungeonTile.WALL
            if position == self.player:
                return DungeonTile.PLAYER
            if position == self.layout.exit:
                return DungeonTile.EXIT
            if position in self.remaining_coins:
                return DungeonTile.COIN
            return DungeonTile.EMPTY
        return '\n'.join(''.join(position_to_str(Point(x, y)) for x in range(self.layout.width)) for y in range(self.layout.height))

# This is a list of all the possible actions for the dungeon agent
AllDungeonActions = [
    Direction.RIGHT,
    Direction.UP,
    Direction.DOWN,
    Direction.LEFT
]

# This is the implementation of the dungeon problem
class DungeonProblem(Problem[DungeonState, Direction]):
    # The problem will contain the dungeon layout and the inital state
    layout: DungeonLayout
    initial_state: DungeonState

    def get_initial_state(self) -> DungeonState:
        return self.initial_state

    # We use @track_call_count to track the number of times this function was called to count the number of explored nodes
    @track_call_count
    def is_goal(self, state: DungeonState) -> bool:
        return len(state.remaining_coins) == 0 and state.player == self.layout.exit

    def get_actions(self, state: DungeonState) -> Iterable[Direction]:
        actions = []
        for direction in Direction:
            position = state.player + direction.to_vector()
            # Disallow walking into walls
            if position not in self.layout.walkable: continue
            actions.append(direction)
        return actions

    def get_successor(self, state: DungeonState, action: Direction) -> DungeonState:
        player = state.player + action.to_vector()
        remaining_coins = state.remaining_coins
        if player not in self.layout.walkable:
            # If we try to walk into a wall, the state does not change
            return state
        if player in remaining_coins:
            # If we walk over a coin, we take it
            remaining_coins -= {player}
        return DungeonState(state.layout, player, remaining_coins)

    def get_cost(self, state: DungeonState, action: Direction) -> float:
        # All actions have the same cost
        return 1

    # Read a dungeon problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'DungeonProblem':
        walkable, coins =  set(), set()
        player: Point = None
        exit: Point = None
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != DungeonTile.WALL:
                    walkable.add(Point(x, y))
                    if char == DungeonTile.PLAYER:
                        player = Point(x, y)
                    elif char == DungeonTile.COIN:
                        coins.add(Point(x, y))
                    elif char == DungeonTile.EXIT:
                        exit = Point(x, y)
        problem = DungeonProblem()
        problem.layout = DungeonLayout(width, height, frozenset(walkable), exit)
        problem.initial_state = DungeonState(problem.layout, player, frozenset(coins))
        return problem

    # Read a dungeon problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'DungeonProblem':
        with open(path, 'r') as f:
            return DungeonProblem.from_text(f.read())