from dungeon import DungeonProblem, DungeonState
from mathutils import Direction, Point, euclidean_distance, manhattan_distance
from helpers import utils
from dataclasses import dataclass
# This heuristic returns the distance between the player and the exit as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: DungeonProblem, state: DungeonState):
    return euclidean_distance(state.player, problem.layout.exit)

def strong_heuristic(problem: DungeonProblem, state: DungeonState) -> float:
    #COMMENT: (How I thought about the problem)
    #First thing first, Manhattan distance is the best distace metric to be use for this problem.
    #Getting an addmissible heuristic is super easy, the problem is for it to be consistent is a whole other story.
    #The best intuitive realaxed version is the one that has no walls.
    #The most important observation for consistency is that the one step cost is always 1.
    #Thus the huristic has to change by at most 1 for every step.
    #Thus if you are summing multiple distances the sum of the distances can only increase by 1 for every step.
    #Thus if one increases the other has to stay the same.
    #Given all the consistant heuristics that esstimtes the distance between the player and the exit using one coin, only one could be used at a time (otherwise the sum would increase by more than 1).
    #The best one coin heuristic is coin that creates the maximum distance between the player and the exit.
    #All that applies to one coin also applies to multiple coins.
    #The coins location and the exit are fixed so the best pathes between them could be precomputed.
    #ALL of the upove could be generalized to any number of coins.

    #COMMENT: (On my solution)
    # I used the Manhattan distance as the distance metric.
    # The distances between the coin_1 to coin_2 to exit are precomputed and ordered.
    # The true path cost is always less that the max of the above as the above assumes no walls.
    # The main calculation that is done on every state is the distance between the player and the coin_1,
    # then max distance between coin_1, coin_2 and exit is done through the precomputed distances.
    # The max of player to  coin_1 to coin_2 to exit is returned.
    # note that the (player to coin_1 to coin_2 to exit) is different than (player to cloin_2 to coin_1 to exit) for fixed coins.
    # thus min of those two is returned.
    # if only one coin is left the distance (player to coin_1 to exit) is returned.
    # if no coins are left the distance (player to exit) is returned.
    #NOTE: I know that this could be easily genralized to any number of coins but I've got enough from this assignment.

    source = state.player
    target = problem.layout.exit
    #COMMENT: (The one time calculations)
    if not problem.cache():
        for coin_1 in state.remaining_coins:
            problem.cache()[coin_1]=[]
            for coin_2 in state.remaining_coins-{coin_1}:
                    problem.cache()[coin_1].append(coin_2)
            problem.cache()[coin_1].sort(key=lambda x: manhattan_distance(coin_1, x)+manhattan_distance(x, target))
            problem.cache()[coin_1].reverse()
    
    data_size = len(state.remaining_coins)
    max_path_cost = 0
    #COMMENT: Picking the longest 2 coins path
    if data_size > 1:
        for coin_1 in state.remaining_coins:
            for coin_2 in problem.cache()[coin_1]:
                if coin_2 in state.remaining_coins:
                    break
            path_cost_1 = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, target)
            path_cost_2 = manhattan_distance(source, coin_2) + manhattan_distance(coin_2, coin_1) + manhattan_distance(coin_1, target)
            path_cost = min(path_cost_1, path_cost_2)
            if path_cost > max_path_cost:
                max_path_cost = path_cost
    #COMMENT: Picking the only 1 coins path if only 1 coin is left
    else:
        for coin in state.remaining_coins:
            path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
            if path_cost > max_path_cost:
                max_path_cost = path_cost
    #COMMENT: Picking the path to the exit if no coins are left
    if max_path_cost == 0:
        max_path_cost = manhattan_distance(source, target)
    return max_path_cost


