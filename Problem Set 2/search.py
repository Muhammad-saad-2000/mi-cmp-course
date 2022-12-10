from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import math

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    terminal, values = game.is_terminal(state)

    if terminal: return values[0], None
    if max_depth == 0: return heuristic(game, state, 0), None

    if agent == 0:
        optimal_value = -math.inf
        optimal_action = None
        for action in game.get_actions(state):
            value, _ = minimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            if value > optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action

    if agent != 0:
        optimal_value = math.inf
        optimal_action = None
        for action in game.get_actions(state):
            value, _ = minimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            if value < optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    def alphabeta_backtrack(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)

        if terminal: return values[0], None
        if max_depth == 0: return heuristic(game, state, 0), None

        if agent == 0:
            optimal_value = -math.inf
            optimal_action = None
            for action in game.get_actions(state):
                value, _ = alphabeta_backtrack(game, game.get_successor(state, action), heuristic, max_depth - 1, alpha, beta)
                if value > optimal_value:
                    optimal_value = value
                    optimal_action = action
                alpha = max(alpha, optimal_value)
                if optimal_value >= beta:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action

        if agent != 0:
            optimal_value = math.inf
            optimal_action = None
            for action in game.get_actions(state):
                value, _ = alphabeta_backtrack(game, game.get_successor(state, action), heuristic, max_depth - 1, alpha, beta)
                if value < optimal_value:
                    optimal_value = value
                    optimal_action = action
                if optimal_value <= alpha:
                    return optimal_value, optimal_action
                beta = min(beta, optimal_value)
            return optimal_value, optimal_action
    
    return alphabeta_backtrack(game, state, heuristic, max_depth, -math.inf, math.inf)

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    def alphabeta_with_move_ordering_backtrack(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)

        if terminal: return values[0], None
        if max_depth == 0: return heuristic(game, state, 0), None

        actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
        actions_states.sort(key=lambda x: heuristic(game, x[1], agent), reverse=True)

        if agent == 0:
            optimal_value = -math.inf
            optimal_action = None
            for action, state in actions_states:
                value, _ = alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth - 1, alpha, beta)
                if value > optimal_value:
                    optimal_value = value
                    optimal_action = action 
                alpha = max(alpha, optimal_value)
                if optimal_value >= beta:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action

        if agent != 0:
            optimal_value = math.inf
            optimal_action = None
            for action, state in actions_states:
                value, _ = alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth - 1, alpha, beta)
                if value < optimal_value:
                    optimal_value = value
                    optimal_action = action
                if optimal_value <= alpha:
                    return optimal_value, optimal_action
                beta = min(beta, optimal_value)
            return optimal_value, optimal_action
    
    return alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth, -math.inf, math.inf)


# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    terminal, values = game.is_terminal(state)

    if terminal: return values[0], None
    if max_depth == 0: return heuristic(game, state, 0), None

    if agent == 0:
        optimal_value = -math.inf
        optimal_action = None
        for action in game.get_actions(state):
            value, _ = expectimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            if value > optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action

    if agent != 0:
        optimal_value = 0
        optimal_action = None
        for action in game.get_actions(state):
            value, _ = expectimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            optimal_value += value
        optimal_value /= len(game.get_actions(state))
        return optimal_value, optimal_action

