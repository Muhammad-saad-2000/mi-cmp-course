from dataclasses import dataclass
from copy import deepcopy
from typing import Iterable, List, Optional, Set, Tuple
from enum import Enum

from mathutils import Direction, Point
from game import Game
from helpers.utils import track_call_count
from helpers.mt19937 import RandomGenerator
from agents import Agent

# This file contains the definition for the Dungeon Crawler game
# In this problem, the agent can move Up, Down, Left, Right or stay idle
# and it has to get a key then reach the exit

# This enum represents all the possible tiles in a Dungeon map
class DungeonTile(str, Enum):
    EMPTY  = "."
    WALL   = "#"
    COIN   = "$"
    EXIT   = "E"
    PLAYER = "@"
    MONSTER = "M"
    DAGGER = "~"
    KEY = "K"

# Dungeon layout specifies the walkable locations and the exit location
@dataclass
class DungeonLayout:
    width: int
    height: int
    walkable: Set[Point]
    exit: Point

    def __deepcopy__(self, memo):
        return self

# The state of a player contains its position, whether it is alive or not and its inventory
@dataclass
class Player:
    @dataclass
    class Inventory:
        daggers: int
        coins: int
        keys: int

    position: Point
    alive: bool
    inventory: Inventory

# The state of a monster contains its position and whether it is alive or not
@dataclass
class Monster:
    position: Point
    alive: bool

# This will contain a reference to the dungeon layout and it will contain environment details that change across states such as:
#   The player location and the locations of the monsters, remaining coins, daggers, key, etc. 
@dataclass
class DungeonState:
    time: int
    turn: int
    layout: DungeonLayout
    player: Player
    coins: Set[Point]
    daggers: Set[Point]
    keys: Set[Point]
    monsters: List[Monster]

    # return the next turn (it ignore all the dead monsters)
    def next_turn(self) -> int:
        turn = self.turn
        while turn < len(self.monsters):
            if self.monsters[turn].alive:
                return turn+1
            turn += 1
        return 0
    
    # The score is 1 point for each coin, 10 points for each monster, -0.1 points for each passing second.
    def score(self) -> int:
        return self.player.inventory.coins + 10 * sum(not monster.alive for monster in self.monsters) - 0.1 * self.time

    # This operator will convert the state to a string containing the grid representation of the level at the current state
    def __str__(self) -> str:
        alive_monsters = {monster.position for monster in self.monsters if monster.alive}
        def position_to_str(position):
            if position not in self.layout.walkable:
                return DungeonTile.WALL
            if position == self.player.position:
                return DungeonTile.PLAYER
            if position in alive_monsters:
                return DungeonTile.MONSTER
            if position == self.layout.exit:
                return DungeonTile.EXIT
            if position in self.keys:
                return DungeonTile.KEY
            if position in self.coins:
                return DungeonTile.COIN
            if position in self.daggers:
                return DungeonTile.DAGGER
            return DungeonTile.EMPTY
        header = f"Inventory: {self.player.inventory.keys} Key(s), {self.player.inventory.daggers} Dagger(s), {self.player.inventory.coins} Coin(s)\n"
        return header + '\n'.join(''.join(position_to_str(Point(x, y)) for x in range(self.layout.width)) for y in range(self.layout.height))

# This is the implementation of the dungeon game
class DungeonGame(Game[DungeonState, Direction]):
    # The problem will contain the dungeon layout and the inital state
    layout: DungeonLayout
    initial_state: DungeonState

    def get_initial_state(self) -> DungeonState:
        return self.initial_state

    @property
    def agent_count(self) -> int:
        return 1 + len(self.initial_state.monsters)

    @track_call_count
    def is_terminal(self, state: DungeonState) -> Tuple[bool, Optional[List[float]]]:
        # if we have a key and we are at the exit, we win
        win = state.player.inventory.keys != 0 and state.player.position == self.layout.exit
        INFINITY = 1e8
        if win:
            value = INFINITY + state.score() # value = a very high number + the player score
            # We return the high value for the player and its negative to all the monsters 
            return True, [value, *(-value for _ in state.monsters)]
        else:
            # if we are not alive, we lose
            if not state.player.alive:
                # We return a very low value for the player and a very high value to all the monsters
                return True, [-INFINITY, *(INFINITY for _ in state.monsters)]
            else:
                return False, None

    def get_turn(self, state: DungeonState) -> int:
        return state.turn

    def get_actions(self, state: DungeonState) -> Iterable[Direction]:
        if state.turn == 0:
            # Find an return actions to be done by the player
            position_position = state.player.position
            positions = ((direction, position_position + direction.to_vector()) for direction in Direction)
            # prevent the player from getting into a wall
            return [direction for direction, position in positions if position in state.layout.walkable]
        else:
            # Find an return actions to be done by a monster
            index = state.turn - 1
            if not state.monsters[index].alive: return []
            monster_locations = {monster.position for i, monster in enumerate(state.monsters) if i != index and monster.alive} 
            monster_position = state.monsters[index].position
            positions = ((direction, monster_position + direction.to_vector()) for direction in Direction)
            # prevent the monster from getting into a wall or another monster
            return [direction for direction, position in positions if position in state.layout.walkable and position not in monster_locations]

    def get_successor(self, state: DungeonState, action: Direction) -> DungeonState:
        state = deepcopy(state)
        current_turn = state.turn
        if current_turn == 0:
            # This action is done by the player
            new_position = state.player.position + action.to_vector()
            state.player.position = new_position
            if new_position in state.coins:
                # If we walk over a coin, we take it
                state.coins.remove(new_position)
                state.player.inventory.coins += 1
            if new_position in state.daggers:
                # If we walk over a dagger, we take it
                state.daggers.remove(new_position)
                state.player.inventory.daggers += 1
            if new_position in state.keys:
                # If we walk over a dagger, we take it
                state.keys.remove(new_position)
                state.player.inventory.keys += 1
            # Find the monsters at the player position
            monsters_at_player = [monster for monster in state.monsters if monster.position == new_position and monster.alive]
            if monsters_at_player:
                if state.player.inventory.daggers < len(monsters_at_player):
                    # If we encounter a monster and we don't have a dagger, we die
                    state.player.inventory.daggers = 0
                    state.player.alive = False
                else:
                    # If we encounter a monster and we have a dagger, we kill it
                    state.player.inventory.daggers -= len(monsters_at_player)
                    for monster in monsters_at_player:
                        monster.alive = False
        else:
            # This action is done by a monster
            monster = state.monsters[current_turn - 1]
            new_position = monster.position + action.to_vector()
            monster.position = new_position
            if new_position == state.player.position:
                if state.player.inventory.daggers != 0:
                    # If we encounter a player and they have a dagger, we die
                    monster.alive = False
                    state.player.inventory.daggers -= 1
                else:
                    # If we encounter a player and they don't have a dagger, we eat them
                    state.player.alive = False
        # Advance the turn
        state.turn = state.next_turn()
        if state.turn == 0:
            # if the new turn is 0 (the player's turn), we advance the clock 
            state.time += 1
        return state

    # Read a dungeon problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'DungeonGame':
        walkable, coins, keys, daggers =  set(), set(), set(), set()
        monsters = list()
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
                    elif char == DungeonTile.KEY:
                        keys.add(Point(x, y))
                    elif char == DungeonTile.MONSTER:
                        monsters.append(Monster(Point(x, y), True))
                    elif char == DungeonTile.DAGGER:
                        daggers.add(Point(x, y))
                    elif char == DungeonTile.EXIT:
                        exit = Point(x, y)
        problem = DungeonGame()
        problem.layout = DungeonLayout(width, height, walkable, exit)
        player = Player(player, True, Player.Inventory(0, 0, 0))
        problem.initial_state = DungeonState(0, 0, problem.layout, player, coins, daggers, keys, monsters)
        return problem

    # Read a dungeon problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'DungeonGame':
        with open(path, 'r') as f:
            return DungeonGame.from_text(f.read())

# This agent will control a monster
class MonsterAgent(Agent):
    rng: RandomGenerator # The random generator used to select a direction
    current_direction: Direction # The current direction in which the monster moves
    steps: int # The number of steps walked by monsters since it last changed its direction

    def __init__(self, seed: int = None) -> None:
        self.rng = RandomGenerator(seed)
        self.current_direction = Direction.NONE
        self.steps = 0

    def __select_new_action(self, actions: Iterable[Direction]):
        # extract movement actions
        movement_actions = [action for action in actions if action != Direction.NONE]
        self.steps = 0 # reset the step counter
        if movement_actions:
            # if there are movement actions, select one of them
            self.current_direction = movement_actions[self.rng.int(0, len(movement_actions)-1)]
        else:
            # if there are no movement actions, stay idle
            self.current_direction = Direction.NONE

    def act(self, game: DungeonGame, state: DungeonState) -> Direction:
        actions = game.get_actions(state)
        if self.current_direction == Direction.NONE or \
            self.current_direction not in actions or \
            self.rng.float() > 2**(-self.steps / min(state.layout.width, state.layout.height)):
            # If the current action is NONE or it is unavailable or we have been using the same action for too long
                self.__select_new_action(actions)
        self.steps += 1 # increment the step counter
        return self.current_direction

##########################
# The Heuristic Function #
##########################

# Return the path length or a very large number if the path is None
def path_length(path) -> int:
    return 0xffffffff if path is None else len(path)-1

# Return the path between two points in the dungeom
# The result is cached inside the game object
def compute_path(game: DungeonGame, p1: Point, p2: Point) -> List[Point]:
    cache = game.cache()
    if p1 not in cache:
        from collections import deque
        path_map = {p1: [p1]}
        queue = deque([p1])
        while queue:
            parent = queue.popleft()
            path = path_map[parent]
            for direction in Direction:
                child = parent + direction.to_vector()
                if child in path_map or child not in game.layout.walkable:
                    continue
                path_map[child] = path + [child]
                queue.append(child)
        cache[p1] = path_map
    return cache[p1].get(p2, None)

# Finds the shortest path from a point to a path in the dungeon
def path_to_path(game: DungeonGame, p1: Point, path: List[Point]):
    if path is None: return None
    paths = [compute_path(game, p1, p2) for p2 in path]
    _, _, shortest = min((path_length(path), index, path) for index, path in enumerate(paths))
    return shortest

# Checks if monsters can reach the player while traversing the shortest path to a goal point
# Returns the number of monster that endanger the player and the length of the player's path
def path_safety(game: DungeonGame, state: DungeonState, goal: Point):
    path = compute_path(game, state.player.position, goal)
    length = path_length(path)
    # For each alive monster, find the shortest path from the the monster to the player's path
    monster_paths = [path_to_path(game, monster.position, path) for monster in state.monsters if monster.alive]
    # Find how long the monster will take to reach the player's path
    monster_path_lengths = [path_length(monster_path) for monster_path in monster_paths]
    # Find how it will take the player to get past the monster encounter position
    monster_encounter_distance = [path.index(monster_path[-1]) for monster_path in monster_paths]
    # Count dangerous monsters (the ones that can reach the player path before the player can outpace them)
    danger = sum(encounter >= distance for encounter, distance in zip(monster_encounter_distance, monster_path_lengths))
    return danger, length

# Returns a heuristic value for the dungeon game state
# Argument:
# - game: the game that is being played
# - state: the state to evaluate
# - agent: the agent for which we are evaluating the state. For example, if the value is high for the player, it should be low for the monster
# Returns the heuristic value of the state for the given agent 
def dungeon_heuristic(game: DungeonGame, state: DungeonState, agent: int) -> float:
    area = state.layout.width * state.layout.height

    value = state.score()
    INFINITY = int(1e8)
    if state.player.inventory.keys != 0 and state.player.position == state.layout.exit:
        # If the player won, return a very high value for the player (very low for the monsters)
        value += INFINITY
        return value if agent == 0 else -value
    if not state.player.alive:
        # If the player lost, return a very lowe value for the player (very high for the monsters)
        value = -INFINITY
        return value if agent == 0 else -value
    
    # Incentivize the player to collect a key
    value += area * min(1, state.player.inventory.keys)
    alive_monsters = [monster for monster in state.monsters if monster.alive]
    # Incentivize the player to kill monsters (voilence is always the anwser)
    value -= len(alive_monsters)
    # Incentivize the player to collect as many daggers as needed to kill the remaining monsters
    value += 10 * min(len(alive_monsters), state.player.inventory.daggers)

    # find the distance to the nearest monster
    if alive_monsters:
        nearest_monster = min(path_length(compute_path(game, state.player.position, monster.position)) for monster in alive_monsters)
    else:
        nearest_monster = area
    

    # Now we check the situation of the player and give them points accordingly
    if state.player.inventory.keys == 0:
        # Situation: Has no keys, must find key
        danger, distance = min(path_safety(game, state, key) for key in state.keys)
        if danger <= state.player.inventory.daggers:
            value += 2 * area # No danger bonus
            # Seek key
            value -= distance # distance to key penalty
        elif len(state.daggers) == 0:
            # There are no daggers to collect so seek key anyway
            value -= distance # distance penalty
            if nearest_monster < 2: value -= area * area # penalize being too near to a monster
        else:
            # Situation: seek dagger
            danger, distance = min(path_safety(game, state, dagger) for dagger in state.daggers)
            if danger <= 0: value += area  # No danger bonus
            elif nearest_monster < 2: value -= area * area # penalize being too near to a monster
            value -= distance # distance to dagger penalty
    else:
        # Situation: Has key, must reach exit
        value += 4 * area # Bonus for having the key
        danger, distance = path_safety(game, state, state.layout.exit)
        if danger <= state.player.inventory.daggers:
            value += 2 * area # No danger bonus
            # Seek exit
            value -= distance # distance to exit penalty
        elif len(state.daggers) == 0:
            # Seek exit anyway
            value -= distance # distance to exit penalty
            if nearest_monster < 2: value -= area * area # penalize being too near to a monster
        else:
            # Situation: seek dagger
            danger, distance = min(path_safety(game, state, dagger) for dagger in state.daggers)
            if danger <= 0: value += area  # No danger bonus
            elif nearest_monster < 2: value -= area * area # penalize being too near to a monster
            value -= distance # distance to dagger penalty

    # if the agent is a monster, return the negative of the value
    return value if agent == 0 else -value