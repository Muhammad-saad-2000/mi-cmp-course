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
    #COMMENT: Get the current agent (max or min)
    agent = game.get_turn(state)
    terminal, values = game.is_terminal(state)
    #COMMENT: In case of terminal state or max depth return the leaf value or heuristic value and None as action
    if terminal: return values[0], None
    if max_depth == 0: return heuristic(game, state, 0), None
    #COMMENT: If the current agent is the max agent
    if agent == 0:
        optimal_value = -math.inf
        optimal_action = None
        #COMMENT: For each action in the current state get the successor state and call minimax on the new state
        for action in game.get_actions(state):
            value, _ = minimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            #COMMENT: Update the optimal value and action in case of a bigger value found
            if value > optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action
    #COMMENT: If the current agent is the min agent
    if agent != 0:
        optimal_value = math.inf
        optimal_action = None
        #COMMENT: For each action in the current state get the successor state and call minimax on the new state
        for action in game.get_actions(state):
            value, _ = minimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            #COMMENT: Update the optimal value and action in case of a smaller value found
            if value < optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #COMMENT: define a funtion for recursive backtracking
    def alphabeta_backtrack(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        #COMMENT: Get the current agent (max or min)
        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)
        #COMMENT: In case of terminal state or max depth return the leaf value or heuristic value and None as action
        if terminal: return values[0], None
        if max_depth == 0: return heuristic(game, state, 0), None
        #COMMENT: If the current agent is the max agent
        if agent == 0:
            optimal_value = -math.inf
            optimal_action = None
            #COMMENT: For each action in the current state get the successor state and call alphabeta on the new state
            for action in game.get_actions(state):
                value, _ = alphabeta_backtrack(game, game.get_successor(state, action), heuristic, max_depth - 1, alpha, beta)
                if value > optimal_value:
                    optimal_value = value
                    optimal_action = action
                #COMMENT: Update the alpha value in case of a bigger value found (Because it is a max node)
                alpha = max(alpha, optimal_value)
                #COMMENT: Prune if the optimal value is bigger than beta
                if optimal_value >= beta:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action
        #COMMENT: If the current agent is the min agent
        if agent != 0:
            optimal_value = math.inf
            optimal_action = None
            #COMMENT: For each action in the current state get the successor state and call alphabeta on the new state
            for action in game.get_actions(state):
                value, _ = alphabeta_backtrack(game, game.get_successor(state, action), heuristic, max_depth - 1, alpha, beta)
                if value < optimal_value:
                    optimal_value = value
                    optimal_action = action
                #COMMENT: Update the beta value in case of a smaller value found (Because it is a min node)
                beta = min(beta, optimal_value)
                #COMMENT: Prune if the optimal value is smaller than alpha
                if optimal_value <= alpha:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action
    #COMMENT: Call the recursive backtracking function with the initial values
    return alphabeta_backtrack(game, state, heuristic, max_depth, -math.inf, math.inf)

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #COMMENT: define a funtion for recursive backtracking
    def alphabeta_with_move_ordering_backtrack(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int, alpha: float, beta: float) -> Tuple[float, A]:
        #COMMENT: Get the current agent (max or min)
        agent = game.get_turn(state)
        terminal, values = game.is_terminal(state)
        #COMMENT: In case of terminal state or max depth return the leaf value or heuristic value and None as action
        if terminal: return values[0], None
        if max_depth == 0: return heuristic(game, state, 0), None
        #COMMENT: Now we are going to sort the actions based on the heuristic value of the successor state
        actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
        actions_states.sort(key=lambda x: heuristic(game, x[1], agent), reverse=True)
        #COMMENT: If the current agent is the max agent
        if agent == 0:
            optimal_value = -math.inf
            optimal_action = None
            #COMMENT: loop over the ordered actions and states and call alphabeta on the new state
            for action, state in actions_states:
                value, _ = alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth - 1, alpha, beta)
                if value > optimal_value:
                    optimal_value = value
                    optimal_action = action 
                #COMMENT: Update the alpha value in case of a bigger value found (Because it is a max node)
                alpha = max(alpha, optimal_value)
                #COMMENT: Prune if the optimal value is bigger than beta
                if optimal_value >= beta:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action
        #COMMENT: If the current agent is the min agent
        if agent != 0:
            optimal_value = math.inf
            optimal_action = None
            #COMMENT: loop over the ordered actions and states and call alphabeta on the new state
            for action, state in actions_states:
                value, _ = alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth - 1, alpha, beta)
                if value < optimal_value:
                    optimal_value = value
                    optimal_action = action
                #COMMENT: Update the beta value in case of a smaller value found (Because it is a min node)
                beta = min(beta, optimal_value)
                #COMMENT: Prune if the optimal value is smaller than alpha
                if optimal_value <= alpha:
                    return optimal_value, optimal_action
            return optimal_value, optimal_action
    #COMMENT: Call the recursive backtracking function with the initial values
    return alphabeta_with_move_ordering_backtrack(game, state, heuristic, max_depth, -math.inf, math.inf)


# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    terminal, values = game.is_terminal(state)
    #COMMENT: In case of terminal state or max depth return the leaf value or heuristic value and None as action
    if terminal: return values[0], None
    if max_depth == 0: return heuristic(game, state, 0), None
    #COMMENT: If the current agent is the max agent
    if agent == 0:
        optimal_value = -math.inf
        optimal_action = None
        for action in game.get_actions(state):
            value, _ = expectimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            if value > optimal_value:
                optimal_value = value
                optimal_action = action
        return optimal_value, optimal_action
    #COMMENT: Now this is a chance node so we calculate here the expected value (assuming a uniform distribution)
    if agent != 0:
        optimal_value = 0
        optimal_action = None
        #COMMENT: Because all actions are equally likely we can just calculate the average value
        for action in game.get_actions(state):
            value, _ = expectimax(game, game.get_successor(state, action), heuristic, max_depth - 1)
            optimal_value += value
        optimal_value /= len(game.get_actions(state))
        return optimal_value, optimal_action

