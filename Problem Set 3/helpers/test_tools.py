from typing import Any, Callable, Dict, List, Optional, Tuple
from base_rl import RLAgent
from grid import GridEnv, GridMDP
from helpers.rl_utils import ACTION_TO_STR, ACTIONS, Policy, QMap, UtilityMap, WeightMap, extract_policy, extract_q_values, extract_utilities, format_grid, format_policy, format_q_values, format_utilities, format_weights

from mathutils import Direction, Point
from .utils import Result, load_function

# Checks if two floating point numbers are almost equal
def approx_eq(output, expected):
    if output == expected: return True
    return abs(output - expected)/(abs(output) + abs(expected)) < 1e-6

def match_policy(policy: Policy, patterns: Dict[Any, str]) -> bool:
    return all(ACTION_TO_STR[action] in patterns.get(state, "") for state, action in policy.items())

def match_utilities(utilities: UtilityMap, expected: UtilityMap) -> bool:
    return all(approx_eq(utility, expected.get(state, 0)) for state, utility in utilities.items())

def match_q_values(q_values: QMap, expected: QMap) -> bool:
    for action, utilities in q_values.items():
        expected_utilities = expected.get(ACTION_TO_STR[action], {})
        for state, utility in utilities.items():
            corresponding = expected_utilities.get(state, 0)
            if not approx_eq(utility, corresponding):
                return False
    return True

def match_weights(weights: WeightMap, expected: WeightMap) -> bool:
    for action, weight_set in weights.items():
        expected_weight_set = expected.get(ACTION_TO_STR[action], {})
        for feature, weight in weight_set.items():
            corresponding = expected_weight_set.get(feature, 0)
            if not approx_eq(weight, corresponding):
                return False
    return True

def format_policy_patterns(patterns: Dict[Any, str], size: Tuple[int, int]) -> str:
    return format_grid({key:' or '.join(value) for key, value in patterns.items()}, size)

def side_by_side(s1: str, s2: str) -> str:
    lines1 = s1.splitlines()
    lines2 = s2.splitlines()
    max_width = max((len(l) for l in lines1), default=0)
    return '\n'.join(l1.ljust(max_width) + '    |    ' + l2 for l1, l2 in zip(lines1, lines2))


#############################################
## TEST CASE: RUNNERS & COMPARATORS #########
#############################################

# Train a value iteration agent on grid MDP 
def run_value_iteration(env: GridEnv, discount_factor: float, iterations: int, noise: float = None, tolerance: float = 0) -> Tuple[UtilityMap, Policy, int]:
    if noise is not None: # If noise is not none, we override the default value supplied with the environment
        env.mdp.noise = noise
    # Create and train the Value Iteration agent
    cls = load_function("value_iteration.ValueIterationAgent")
    agent = cls(env.mdp, discount_factor)
    iterations = agent.train(iterations, tolerance)
    # Reset the environment since we need to do that before requesting actions from the agent
    env.reset()
    return extract_utilities(env, agent), extract_policy(env, agent), iterations

# Train a policy iteration agent on grid MDP 
def run_policy_iteration(env: GridEnv, discount_factor: float, iterations: int, noise: float = None) -> Tuple[UtilityMap, Policy, int]:
    if noise is not None: # If noise is not none, we override the default value supplied with the environment
        env.mdp.noise = noise
    # Create and train the Value Iteration agent
    cls = load_function("policy_iteration.PolicyIterationAgent")
    agent = cls(env.mdp, discount_factor)
    iterations = agent.train(iterations)
    # Reset the environment since we need to do that before requesting actions from the agent
    env.reset()
    return extract_utilities(env, agent), extract_policy(env, agent), iterations

# Compare a testcase result with the expected output based on the utility and the policy
def compare_utility_policy_results(
    output: Tuple[UtilityMap, Policy, int],
    expected_utility: UtilityMap,
    expected_policy: Policy,
    level_path: str,
    iteration_test: Optional[str] = None) -> Result:

    utility, policy, iterations = output
    
    # Check if thew result contains a wrong type
    type_mismatch = None
    for state, value in utility.items():
        if not (isinstance(value, float) or isinstance(value, int)):
            type_mismatch = f"Wrong utility type. Expected a number, but for the state {state}, the utility {value} is a {type(value)}."
            break
        action = policy.get(state)
        if action is not None and not isinstance(action, Direction):
            type_mismatch = f"Wrong action type. Expected a Direction, but for the state {state}, the action {action} is a {type(action)}."
            break

    if type_mismatch is None:
        # Check if the result is one of the expected values
        # If yes, return a success result
        utilities_match = match_utilities(utility, expected_utility)
        policy_match = match_policy(policy, expected_policy)
        iteration_match = (iteration_test is None) or (eval("lambda value: " + iteration_test)(iterations))
        if utilities_match and policy_match and iteration_match:
            return Result(True, 1, "")
    
    mdp = GridMDP.from_file(level_path)

    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    message  = f"Grid:{nl}{mdp}{nl}"
    if type_mismatch is None:
        utility_side_to_side = side_by_side(format_utilities(expected_utility, mdp.size), format_utilities(utility, mdp.size))
        message += f"Utility: Expected vs Your Anwser{nl}{utility_side_to_side}{nl}{nl}"
        policy_side_to_side = side_by_side(format_policy_patterns(expected_policy, mdp.size), format_policy(policy, mdp.size))
        message += f"Policy: Expected vs Your Answer{nl}{policy_side_to_side}{nl}{nl}"
        if not utilities_match: message += "DIAGNOSIS: Utilities do not match the expected output\n"
        if not policy_match: message += "DIAGNOSIS: Policy do not match the expected output\n"
        if not iteration_match: message += f'DIAGNOSIS: The number of iterations done by the agent (value={iterations}) does no satisfy the condition "{iteration_test}"' + "\n"
    else:
        message += f"DIAGNOSIS: {type_mismatch}\n"

    return Result(False, 0, message)

# Train a value iteration agent on grid MDP with options returned from another function (these functions are found in 'options.py')
def run_value_iteration_with_options(env: GridEnv, options_fn: Callable[[],Dict[str, int]]) -> Tuple[UtilityMap, Policy]:
    # Get the options and setup the environment with the new noise and living reward
    options = options_fn()
    
    env.mdp.noise = options["noise"]
    discount_factor = options["discount_factor"]
    living_reward = options["living_reward"]

    for state in env.mdp.walkable - env.mdp.terminals:
        env.mdp.rewards[state] = living_reward
    # Create and train the Value Iteration agent
    cls = load_function("value_iteration.ValueIterationAgent")
    agent = cls(env.mdp, discount_factor)
    agent.train(100)
    # Reset the environment since we need to do that before requesting actions from the agent
    env.reset()
    return extract_utilities(env, agent), extract_policy(env, agent)

# Compare a testcase result with the expected output based on the policy only
def compare_policy_only_results(
    output: Tuple[UtilityMap, Policy],
    expected_policy: Policy,
    level_path: str) -> Result:

    # Check if the result is one of the expected values
    # If yes, return a success result
    utility, policy = output
    policy_match = match_policy(policy, expected_policy)
    if policy_match:
        return Result(True, 1, "")
    
    mdp = GridMDP.from_file(level_path)

    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    message  = f"Grid:{nl}{mdp.to_display_str()}{nl}"
    policy_side_to_side = side_by_side(format_policy_patterns(expected_policy, mdp.size), format_policy(policy, mdp.size))
    message += f"Policy: Expected vs Your Answer{nl}{policy_side_to_side}{nl}{nl}"
    
    message += f"The Utilities computed based on your options:{nl}{format_utilities(utility, mdp.size)}{nl}{nl}"
    
    if not policy_match: message += "DIAGNOSIS: Policy do not match the expected output\n"

    return Result(False, 0, message)

# Train a reinforcement learning (Q-Learning or SARSA) agent on a grid environment 
def run_rl_agent(
        agent: Any, 
        training_loop: Callable, 
        env: GridEnv, 
        iterations: int, 
        step_limit: int,
        seed: int, 
        noise: float = None) -> Tuple[QMap, Policy]:
    if noise is not None:
        env.mdp.noise = noise
    training_loop(env, agent, iterations, step_limit, seed)
    return extract_q_values(env, agent), extract_policy(env, agent)

# Compare a testcase result with the expected output based on the q-values and the policy
def compare_q_policy_results(
    output: Tuple[QMap, Policy],
    expected_q_values: QMap,
    expected_policy: Policy,
    level_path: str) -> Result:

    # Check if the result is one of the expected values
    # If yes, return a success result
    q_values, policy = output
    q_values_match = match_q_values(q_values, expected_q_values)
    policy_match = match_policy(policy, expected_policy)
    if q_values_match and policy_match:
        return Result(True, 1, "")
    
    mdp = GridMDP.from_file(level_path)

    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    message  = f"Grid:{nl}{mdp}{nl}"
    q_values_side_to_side = side_by_side(format_q_values(expected_q_values, mdp.size), format_q_values(q_values, mdp.size))
    message += f"Q-Values: Expected vs Your Anwser{nl}{q_values_side_to_side}{nl}{nl}"
    policy_side_to_side = side_by_side(format_policy_patterns(expected_policy, mdp.size), format_policy(policy, mdp.size))
    message += f"Policy: Expected vs Your Answer{nl}{policy_side_to_side}{nl}{nl}"
    if not q_values_match: message += "DIAGNOSIS: Q-Values do not match the expected output\n"
    if not policy_match: message += "DIAGNOSIS: Policy do not match the expected output\n"

    return Result(False, 0, message)

# Train an approximate reinforcement learning (Q-Learning) agent on a grid environment 
def run_approx_rl_agent(
        agent: RLAgent, 
        training_loop: Callable, 
        env: GridEnv, 
        iterations: int, 
        step_limit: int,
        seed: int, 
        noise: float = None) -> Tuple[WeightMap, Policy]:
    if noise is not None:
        env.mdp.noise = noise
    training_loop(env, agent, iterations, step_limit, seed)
    return agent.weights, extract_policy(env, agent)

# Compare a testcase result with the expected output based on the learned weights and the policy
def compare_weights_policy_results(
    output: Tuple[WeightMap, Policy],
    expected_weights: WeightMap,
    expected_policy: Policy,
    level_path: str) -> Result:

    # Check if the result is one of the expected values
    # If yes, return a success result
    weights, policy = output
    weights_match = match_weights(weights, expected_weights)
    policy_match = match_policy(policy, expected_policy)
    if weights_match and policy_match:
        return Result(True, 1, "")
    
    mdp = GridMDP.from_file(level_path)

    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    message  = f"Grid:{nl}{mdp}{nl}"
    message += f"Expected:{nl}{format_weights(expected_weights)}{nl}{nl}"
    message += f"Got:{nl}{format_weights(weights)}{nl}{nl}"
    policy_side_to_side = side_by_side(format_policy_patterns(expected_policy, mdp.size), format_policy(policy, mdp.size))
    message += f"Policy: Expected vs Your Answer{nl}{policy_side_to_side}{nl}{nl}"
    if not weights_match: message += "DIAGNOSIS: Weights do not match the expected output\n"
    if not policy_match: message += "DIAGNOSIS: Policy do not match the expected output\n"

    return Result(False, 0, message)