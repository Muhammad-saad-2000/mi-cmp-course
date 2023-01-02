from typing import Any, Dict, Tuple
from agents import Agent
from base_rl import RLAgent
from grid import GridEnv
from mathutils import Direction, Point

# Type Definitions for utilities, q-values, policies and weights
UtilityMap = Dict[Point, float]
QMap = Dict[Direction, UtilityMap]
Policy = Dict[Point, Direction]
WeightMap = Dict[Direction, Dict[str, float]]

# Formats data as a grid
def format_grid(strings: Dict[Point, str], size: Tuple[int, int], default: str = ''):
    w, h = size
    max_str_w = max((len(v) for v in strings.values()), default=0)
    rows = ['|'.join(strings.get(Point(x,y), default).rjust(max_str_w) for x in range(w)) for y in range(h)]
    separator = '\n' + ('-' * (w*(1+max_str_w)-1)) + '\n'
    return separator.join(rows)

# Formats data as a sequence of grids
def format_grids(strings: Dict[str, Dict[Point, str]], size: Tuple[int, int], default: str = ''):
    return '\n\n'.join(f'{key}:\n{format_grid(value, size, default)}' for key, value in strings.items())

# Some data used for formatting
ACTIONS = [Direction.LEFT, Direction.RIGHT, Direction.DOWN, Direction.UP]
ACTION_TO_STR = {
    Direction.LEFT: 'L',
    Direction.RIGHT: 'R',
    Direction.DOWN: 'D',
    Direction.UP: 'U'
}

# Extracts a policy from an agent and returns it as a dictionary
def extract_policy(env: GridEnv, agent: Agent[Point, Direction]):
    states = env.mdp.walkable - env.mdp.terminals
    return {state:agent.act(env, state) for state in states}

# formats a policy as a grid
def format_policy(policy: Policy, size: Tuple[int, int]):
    policy = {state:ACTION_TO_STR.get(action, '') for state, action in policy.items()}
    return format_grid(policy, size, '-')

# Extracts utilities from an agent and returns it as a dictionary
def extract_utilities(env: GridEnv, agent: Any):
    states = env.mdp.walkable - env.mdp.terminals
    return {state:agent.utilities.get(state, 0) for state in states}
    
# formats utilities as a grid
def format_utilities(utilities: UtilityMap, size: Tuple[int, int]):
    utilities = {state:"{:4.4f}".format(utility) for state, utility in utilities.items()}
    return format_grid(utilities, size)

# Extracts q-values from an agent and returns it as a dictionary
def extract_q_values(env: GridEnv, agent: Any):
    states = env.mdp.walkable - env.mdp.terminals
    return {action: {state:agent.compute_q(env, state, action) for state in states} for action in ACTIONS}

# formats q-values as a sequence of grids
def format_q_values(q_values: QMap, size: Tuple[int, int]):
    qs = {f"Action: {ACTION_TO_STR.get(action, str(action))}": {state:"{:4.4f}".format(q) for state, q in qs.items()} for action, qs in q_values.items()}
    return format_grids(qs, size)

# formats weights as a sequence of functions
def format_weights(weights: WeightMap):
    return '\n\n'.join(f"Q(State, {ACTION_TO_STR.get(action, str(action))}) = " + ' + '.join(f"{weight}*{feature}" for feature, weight in weight_set.items()) for action, weight_set in weights.items())