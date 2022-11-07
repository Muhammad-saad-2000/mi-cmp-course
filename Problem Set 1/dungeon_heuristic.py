from dungeon import DungeonProblem, DungeonState
from mathutils import Direction, Point, euclidean_distance, manhattan_distance
from helpers import utils
from dataclasses import dataclass
# This heuristic returns the distance between the player and the exit as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: DungeonProblem, state: DungeonState):
    return euclidean_distance(state.player, problem.layout.exit)

#TODO: Import any modules and write any functions you want to use

def strong_heuristic(problem: DungeonProblem, state: DungeonState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.is_goal" HERE.
    # Calling it here will mess up the tracking of the explored nodes count
    # which is considered the number of is_goal calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    #Solution1:
    #return manhattan_distance(state.player, problem.layout.exit)
    #Solution2:
    # state_cost = None
    # for coin_point in state.remaining_coins:
    #     distance = manhattan_distance(state.player, coin_point)
    #     if state_cost is None or distance > state_cost:
    #         state_cost = distance
    # distance = manhattan_distance(state.player, problem.layout.exit)
    # if state_cost is None or distance > state_cost:
    #     state_cost = distance
    # return state_cost
    #Solution3:
    # source = state.player
    # target = problem.layout.exit
    # max_path_cost=None
    # for coin in state.remaining_coins:
    #     path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #     if max_path_cost is None or path_cost > max_path_cost:
    #         max_path_cost = path_cost
    # if max_path_cost is None:
    #     max_path_cost = manhattan_distance(source, target)
    # return max_path_cost
    #Solution4:
    # source = state.player
    # target = problem.layout.exit
    # min_path_cost=None
    # data_size = len(state.remaining_coins)
    # if data_size > 1:
    #     for coin_1 in state.remaining_coins:
    #         for coin_2 in state.remaining_coins - {coin_1}:
    #             path_cost = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, target)
    #             if min_path_cost is None or path_cost < min_path_cost:
    #                 min_path_cost = path_cost
    # elif data_size > 0:
    #     for coin in state.remaining_coins:
    #         path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #         if min_path_cost is None or path_cost < min_path_cost:
    #             min_path_cost = path_cost
    #         if min_path_cost is None:
    #             min_path_cost = manhattan_distance(source, target)
    # if min_path_cost is None:
    #     min_path_cost = manhattan_distance(source, target)
    # return min_path_cost
    #Solution5:avg
    # source = state.player
    # target = problem.layout.exit
    # avg_path_cost=0
    # data_size = len(state.remaining_coins)
    # for coin in state.remaining_coins:
    #     path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #     avg_path_cost += path_cost
    # avg_path_cost += manhattan_distance(source, target)
    # return int(avg_path_cost / (data_size + 1))
    #Solution6:
    # source = state.player
    # target = problem.layout.exit
    # max_path_cost = 0
    # data_size = len(state.remaining_coins)

    # if data_size > 1:
    #     for coin_1 in state.remaining_coins:
    #         for coin_2 in state.remaining_coins - {coin_1}:
    #             path_cost_1 = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, target)
    #             path_cost_2 = manhattan_distance(source, coin_2) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_1, target)
    #             path_cost = min(path_cost_1, path_cost_2)
    #             if path_cost > max_path_cost:
    #                 max_path_cost = path_cost
    # else:
    #     for coin in state.remaining_coins:
    #         path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #         if path_cost > max_path_cost:
    #             max_path_cost = path_cost

    # if max_path_cost == 0:
    #     max_path_cost = manhattan_distance(source, target)
    # return max_path_cost
    #Solution7:
    # source = state.player
    # target = problem.layout.exit
    # max_path_cost = 0
    # data_size = len(state.remaining_coins)

    # if data_size > 2:
    #     for coin_1 in state.remaining_coins:
    #         for coin_2 in state.remaining_coins - {coin_1}:
    #             for coin_3 in state.remaining_coins - {coin_1, coin_2}:
    #                 path_cost_1 = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, coin_3) + manhattan_distance(coin_3, target)
    #                 path_cost_2 = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_3) + manhattan_distance(coin_3, coin_2) + manhattan_distance(coin_2, target)
    #                 path_cost_3 = manhattan_distance(source, coin_2) + manhattan_distance(coin_2, coin_1) + manhattan_distance(coin_1, coin_3) + manhattan_distance(coin_3, target)
    #                 path_cost_4 = manhattan_distance(source, coin_2) + manhattan_distance(coin_2, coin_3) + manhattan_distance(coin_3, coin_1) + manhattan_distance(coin_1, target)
    #                 path_cost_5 = manhattan_distance(source, coin_3) + manhattan_distance(coin_3, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, target)
    #                 path_cost_6 = manhattan_distance(source, coin_3) + manhattan_distance(coin_3, coin_2) + manhattan_distance(coin_2, coin_1) + manhattan_distance(coin_1, target)
    #                 path_cost = min(path_cost_1, path_cost_2, path_cost_3, path_cost_4, path_cost_5, path_cost_6)
    #                 if path_cost > max_path_cost:
    #                     max_path_cost = path_cost
    # elif data_size > 1:
    #     for coin_1 in state.remaining_coins:
    #         for coin_2 in state.remaining_coins - {coin_1}:
    #             path_cost_1 = manhattan_distance(source, coin_1) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_2, target)
    #             path_cost_2 = manhattan_distance(source, coin_2) + manhattan_distance(coin_1, coin_2) + manhattan_distance(coin_1, target)
    #             path_cost = min(path_cost_1, path_cost_2)
    #             if path_cost > max_path_cost:
    #                 max_path_cost = path_cost
    # else:
    #     for coin in state.remaining_coins:
    #         path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #         if path_cost > max_path_cost:
    #             max_path_cost = path_cost
    
    # if max_path_cost == 0:
    #     max_path_cost = manhattan_distance(source, target)
    # return max_path_cost
    #Solution8:
    # source = state.player
    # target = problem.layout.exit
    # max_path_cost = 0
    # data_size = len(state.remaining_coins)
    # list_of_coins = list(state.remaining_coins)
    # if data_size > 2:
    #     for i in range(data_size):
    #         for j in range(i+1, data_size):
    #             for k in range(j+1, data_size):
    #                 path_cost_1 = manhattan_distance(source, list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[k]) + manhattan_distance(list_of_coins[k], target)
    #                 path_cost_2 = manhattan_distance(source, list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[k]) + manhattan_distance(list_of_coins[k], list_of_coins[j]) + manhattan_distance(list_of_coins[j], target)
    #                 path_cost_3 = manhattan_distance(source, list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[k]) + manhattan_distance(list_of_coins[k], target)
    #                 path_cost_4 = manhattan_distance(source, list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[k]) + manhattan_distance(list_of_coins[k], list_of_coins[i]) + manhattan_distance(list_of_coins[i], target)
    #                 path_cost_5 = manhattan_distance(source, list_of_coins[k]) + manhattan_distance(list_of_coins[k], list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[j]) + manhattan_distance(list_of_coins[j], target)
    #                 path_cost_6 = manhattan_distance(source, list_of_coins[k]) + manhattan_distance(list_of_coins[k], list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[i]) + manhattan_distance(list_of_coins[i], target)
    #                 path_cost = min(path_cost_1, path_cost_2, path_cost_3, path_cost_4, path_cost_5, path_cost_6)
    #                 if path_cost > max_path_cost:
    #                     max_path_cost = path_cost
    # elif data_size > 1:
    #     for i in range(data_size):
    #         for j in range(i+1, data_size):
    #             path_cost_1 = manhattan_distance(source, list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[j]) + manhattan_distance(list_of_coins[j], target)
    #             path_cost_2 = manhattan_distance(source, list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[i]) + manhattan_distance(list_of_coins[i], target)
    #             path_cost = min(path_cost_1, path_cost_2)
    #             if path_cost > max_path_cost:
    #                 max_path_cost = path_cost
    # else:
    #     for coin in state.remaining_coins:
    #         path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #         if path_cost > max_path_cost:
    #             max_path_cost = path_cost
    
    # if max_path_cost == 0:
    #     max_path_cost = manhattan_distance(source, target)
    # return max_path_cost
    #Solution9:
    # source = state.player
    # target = problem.layout.exit
    # max_path_cost = 0
    # data_size = len(state.remaining_coins)
    # list_of_coins = list(state.remaining_coins)

    # if data_size > 1:
    #     for i in range(data_size):
    #         for j in range(i+1, data_size):
    #             path_cost_1 = manhattan_distance(source, list_of_coins[i]) + manhattan_distance(list_of_coins[i], list_of_coins[j]) + manhattan_distance(list_of_coins[j], target)
    #             path_cost_2 = manhattan_distance(source, list_of_coins[j]) + manhattan_distance(list_of_coins[j], list_of_coins[i]) + manhattan_distance(list_of_coins[i], target)
    #             path_cost = min(path_cost_1, path_cost_2)
    #             if path_cost > max_path_cost:
    #                 max_path_cost = path_cost
    # else:
    #     for coin in state.remaining_coins:
    #         path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
    #         if path_cost > max_path_cost:
    #             max_path_cost = path_cost
    
    # if max_path_cost == 0:
    #     max_path_cost = manhattan_distance(source, target)
    # return max_path_cost
    #Solution10:
    source = state.player
    target = problem.layout.exit
    data_size = len(state.remaining_coins)
    
    if not problem.cache():
        for coin_1 in state.remaining_coins:
            problem.cache()[coin_1]=[]
            for coin_2 in state.remaining_coins-{coin_1}:
                    problem.cache()[coin_1].append(coin_2)
            problem.cache()[coin_1].sort(key=lambda x: manhattan_distance(coin_1, x)+manhattan_distance(x, target))
            problem.cache()[coin_1].reverse()
    
    max_path_cost = 0
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
    else:
        for coin in state.remaining_coins:
            path_cost = manhattan_distance(source, coin) + manhattan_distance(coin, target)
            if path_cost > max_path_cost:
                max_path_cost = path_cost
    
    if max_path_cost == 0:
        max_path_cost = manhattan_distance(source, target)
    return max_path_cost

