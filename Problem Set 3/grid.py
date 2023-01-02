from typing import Dict, List, Optional, Set, Tuple
from mdp import MarkovDecisionProcess
from environment import Environment
from mathutils import Point, Direction
from helpers.mt19937 import RandomGenerator
import json

# The grid markov decision process similar to the one described in the course book
class GridMDP(MarkovDecisionProcess[Point, Direction]):
    
    size: Tuple[int, int] # The size of the map (width, height)
    walkable: Set[Point] # A set of positions where the player can stand
    terminals: Set[Point] # A set of positions where the episode would end when the player reaches it
    rewards: Dict[Point, float] # The reward of each position
    noise: float # The action noise, aka the probability of steering left or right of the intended direction

    def __init__(self, 
            size: Tuple[int, int], 
            walkable: Set[Point], 
            terminals: Set[Point], 
            rewards: Dict[Point, float],
            noise: float) -> None:
        super().__init__()
        self.size = size
        self.walkable = walkable
        self.terminals = terminals
        self.rewards = rewards
        self.noise = noise

    # Returns all possible states (where there is no walls)
    def get_states(self) -> List[Point]:
        return list(sorted(self.walkable))

    # Returns whether a state is terminal or not
    def is_terminal(self, state: Point) -> bool:
        return state in self.terminals
    
    # Returns the reward function R(s,a,s')
    # for this MDP, we consider R(s,a,s') to be the reward for going to the state s'
    def get_reward(self, state: Point, action: Direction, next_state: Point) -> float:
        return self.rewards.get(next_state, 0)
    
    # Returns a list of all the actions we can take from the given state
    def get_actions(self, state: Point) -> List[Dict]:
        return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
    
    # Given a state and an actions, returns a dictionary of possible next states and their probabilities {s': P(s'|s,a)}
    # each key is a possible next state and its conrresponding value is the probability of reaching it P(s'|s,a) 
    def get_successor(self, state: Point, action: Direction) -> Dict[Point, float]:
        noisy_actions = [
            (action, 1 - self.noise),
            (action.rotate(1), 0.5 * self.noise),
            (action.rotate(3), 0.5 * self.noise)
        ]
        states = {}
        for direction, prob in noisy_actions:
            next_state = state + direction.to_vector()
            if next_state not in self.walkable: next_state = state
            if next_state in states: states[next_state] += prob
            else: states[next_state] = prob
        return states
    
    def parse_state(self, string: str) -> Point:
        x, y = eval(string)
        return Point(x, y)
    
    def format_state(self, state: Point) -> str:
        return str(state)
    
    def parse_action(self, string: str) -> Direction:
        return {
            'R': Direction.RIGHT,
            'U': Direction.UP,
            'L': Direction.LEFT,
            'D': Direction.DOWN,
            '.': Direction.NONE,
        }[string.upper()]
    
    def format_action(self, action: Direction) -> str:
        return {
            Direction.RIGHT: 'R' ,
            Direction.UP: 'U',
            Direction.LEFT: 'L',
            Direction.DOWN: 'D',
            Direction.NONE: '.',
        }[action]

    # converts a state into a string (for printing)
    # if state is None, prints the grid without the player
    def to_display_str(self, state: Optional[Point] = None) -> str:
        def cell_to_str(p: Point):
            if p in self.walkable:
                tile = 'T' if p in self.terminals else '.'
                if p == state: tile += '@'
                return (tile, f'({self.rewards[p]})')
            else:
                return None
        w, h = self.size
        cells = [[cell_to_str(Point(i, j)) for i in range(w)] for j in range(h)]
        cell_str_width = 1 + max(max(0 if cell is None else (len(cell[0]) + len(cell[1])) for cell in row) for row in cells)
        cells = [[(("#"*cell_str_width) if cell is None else (cell[0] + (' ' * (cell_str_width - len(cell[0]) - len(cell[1]))) + cell[1])) for cell in row] for row in cells]
        separator = '\n' + ('-' * (w*(cell_str_width+3))) + '\n'
        return separator.join('|'.join(f' {cell} ' for cell in row) for row in cells)
    
    # Converts the MDP into a string for display
    def __str__(self) -> str:
        return f'{self.to_display_str()}\nNoise: {self.noise}'

    # Read a Grid MDP from a json file
    @staticmethod
    def from_file(path: str) -> 'GridMDP':
        data = json.load(open(path, 'r'))
        grid = data["grid"]
        noise = float(data.get("noise", 0))
        width, height = len(grid[0]), len(grid)
        walkable, terminals = set(), set()
        rewards = {}
        for j, row in enumerate(grid):
            for i, (tile, reward) in enumerate(row):
                if tile == '#': continue
                point = Point(i, j)
                walkable.add(point)
                rewards[point] = reward
                if tile == 'T': terminals.add(point)
        return GridMDP((width, height), walkable, terminals, rewards, noise)

##############################################
######### Grid Environment ###################
##############################################

# This class wraps the grid MDP as an environment which will be used for RL
class GridEnv(Environment[Point, Direction]):
    
    rng: RandomGenerator # A random generator which will be used to sample states from the MDP
    mdp: GridMDP # The wrapped Grid MDP. The enviroment will behave based on this MDP
    inital_state: Optional[Point] # The initia state (initial position of the player).
                                  # If None, the player position will be randomly sampled from all possible location on each reset
    current_state: Point # The current state (position) of the player

    def __init__(self, mdp: GridMDP, inital_state: Optional[Point] = None) -> None:
        super().__init__()
        self.rng = RandomGenerator()
        self.mdp = mdp
        self.initial_state = inital_state

    # resets the environment and returns the current state
    def reset(self, seed: Optional[int] = None) -> Point:
        self.rng.seed(seed) # Seed the Random Generator
        if self.initial_state is None: # If initial state is None, we randomly sampler a state to be the initial current state 
            states = [state for state in self.mdp.get_states() if not self.mdp.is_terminal(state)]
            self.current_state = states[self.rng.int(0, len(states)-1)]
        else:
            self.current_state = self.initial_state
        return self.current_state
    
    # returns a list of a possible actions from the current state
    def actions(self) -> List[Direction]:
        return self.mdp.get_actions(self.current_state)
    
    # Updates the current state using the given action
    def step(self, action: Direction) -> Tuple[Point, float, bool, Dict]:
        next_states, probabilities = zip(*self.mdp.get_successor(self.current_state, action).items())
        # since we may have more than one possible next state, we use a random generator to sample the next state
        next_state = next_states[self.rng.sample(probabilities)]
        reward = self.mdp.get_reward(self.current_state, action, next_state)
        self.current_state = next_state
        return (
            self.current_state, # return the new current state
            reward, # return the reward collected during this transition
            self.mdp.is_terminal(self.current_state),  # returns whether the new current state is a terminal state or not
            {} # We have no debugging info to return, so we return an empty dictionary
        )
    
    # Prints the current state on the console
    def render(self):
        print(self.mdp.to_display_str(self.current_state))

    # Creates an environment from a file
    @staticmethod
    def from_file(path: str, inital_state: Optional[Point] = None) -> 'GridEnv':
        return GridEnv(GridMDP.from_file(path), inital_state)
    
    def parse_state(self, string: str) -> Point:
        return self.mdp.parse_state(string)
    
    def format_state(self, state: Point) -> str:
        return self.mdp.format_state(state)
    
    def parse_action(self, string: str) -> Direction:
        return self.mdp.parse_action(string)
    
    def format_action(self, action: Direction) -> str:
        return self.mdp.format_action(action)