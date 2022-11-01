from typing import List
from dungeon import DungeonProblem, Direction, DungeonState, DungeonTile
from agents import HumanAgent, UninformedSearchAgent, InformedSearchAgent
from helpers.utils import fetch_tracked_call_count
from helpers.heuristic_checks import test_heuristic_consistency
from functools import lru_cache
import argparse, time

def colored_dungeon(level: str):
    from helpers.utils import bcolors
    level = level.replace(DungeonTile.COIN, f'{bcolors.BRIGHT_GREEN}{DungeonTile.COIN}{bcolors.ENDC}')
    level = level.replace(DungeonTile.PLAYER, f'{bcolors.YELLOW}{DungeonTile.PLAYER}{bcolors.ENDC}')
    level = level.replace(DungeonTile.WALL, f'{bcolors.BRIGHT_BLACK}{DungeonTile.WALL}{bcolors.ENDC}')
    level = level.replace(DungeonTile.EMPTY, f'{bcolors.BRIGHT_BLACK}{DungeonTile.EMPTY}{bcolors.ENDC}')
    level = level.replace(DungeonTile.EXIT, f'{bcolors.BRIGHT_BLUE}{DungeonTile.EXIT}{bcolors.ENDC}')
    return level

# Return the heuristic selected by the user
def get_heuristic(name: str):
    if name == "zero":
        return lambda *_: 0
    if name == "weak":
        from dungeon_heuristic import weak_heuristic
        return weak_heuristic
    if name == "strong":
        from dungeon_heuristic import strong_heuristic
        return strong_heuristic
    print(f"Requested Heuristic '{name}' is invalid")
    exit(-1)

# Create an agent based on the user selections
def create_agent(args: argparse.Namespace):
    agent_type: str = args.agent
    if agent_type == "human":
        # This function reads the action from the user (human)
        def dungeon_user_action(problem: DungeonProblem, state: DungeonState) -> Direction:
            possible_actions = list(problem.get_actions(state))
            while True:
                user_input = input("Enter action (WASD): ").strip().lower()
                action = {
                    'w': Direction.UP,
                    's': Direction.DOWN,
                    'a': Direction.LEFT,
                    'd': Direction.RIGHT
                }.get(user_input)
                if action in possible_actions:
                    return action
                else:
                    print("Invalid Action")
        return HumanAgent(dungeon_user_action)
    if agent_type == "bfs":
        from search import BreadthFirstSearch
        return UninformedSearchAgent(BreadthFirstSearch)
    if agent_type == "dfs":
        from search import DepthFirstSearch
        return UninformedSearchAgent(DepthFirstSearch)
    if agent_type == "ucs":
        from search import UniformCostSearch
        return UninformedSearchAgent(UniformCostSearch)
    if agent_type == "astar":
        from search import AStarSearch
        # We cache the heuristic calls to speed up the search process if the heuristic is not fast
        heuristic = lru_cache(2**16)(get_heuristic(args.heuristic))
        # If desired by the user, we track every transition and check for the heuristic consistency for each transition
        if args.checks:
            DungeonProblem.get_successor = test_heuristic_consistency(heuristic)(DungeonProblem.get_successor)
        return InformedSearchAgent(AStarSearch, heuristic)
    if agent_type == "gbfs":
        from search import BestFirstSearch
        # We cache the heuristic calls to speed up the search process if the heuristic is not fast
        heuristic = lru_cache(2**16)(get_heuristic(args.heuristic))
        # If desired by the user, we track every transition and check for the heuristic consistency for each transition
        if args.checks:
            DungeonProblem.get_successor = test_heuristic_consistency(heuristic)(DungeonProblem.get_successor)
        return InformedSearchAgent(BestFirstSearch, heuristic)
    print(f"Requested Agent '{agent_type}' is invalid")
    exit(-1)

def main(args: argparse.Namespace):
    state_printer = lambda state: print(state)
    if args.ansicolors: state_printer = lambda state: print(colored_dungeon(str(state)))
    start = time.time() # Track run time
    problem = DungeonProblem.from_file(args.level) # create the problem
    state = problem.get_initial_state() # Get the initial state
    print("Initial State:")
    state_printer(state)
    agent = create_agent(args)
    step = 0 # This will store the current step
    total_explored_nodes = 0 # This will store the number of traversed nodes during search
    unsolvable = False # This will store whether the problem is unsolvable or not
    while not problem.is_goal(state):
        fetch_tracked_call_count(DungeonProblem.is_goal) # Clear the call counter
        action = agent.act(problem, state) # Request an action from the agent
        # If no solution was found, break
        if action is None:
            print("Agent cannot find a solution, exiting...")
            unsolvable = True
            break
        # Get the number of traversed nodes
        total_explored_nodes += fetch_tracked_call_count(DungeonProblem.is_goal)
        # Apply the action to the state
        state = problem.get_successor(state, action)
        step += 1
        # Print any useful information to the user
        print("Step:", step)
        print("Action:", str(action))
        state_printer(state)
    if not unsolvable: 
        # If desired by the user, we check that the heuristic is zero at the goal state
        if args.checks and isinstance(agent, InformedSearchAgent):
            goal_heuristic = agent.heuristic(problem, state)
            if goal_heuristic != 0:
                print(f"ERROR: Expected heuristic at goal to be 0, got {goal_heuristic}")
        print("YOU WON!!")
    # This was a search agent, display the number of traversed nodes
    if not isinstance(agent, HumanAgent):
        print(f"Search explored {total_explored_nodes} nodes")
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")


if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play Dungeon as Human or AI")
    parser.add_argument("level", help="path to the dungeon to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'bfs', 'dfs', 'ucs', 'astar', 'gbfs'],
                        help="the agent that will play the game")
    parser.add_argument("--heuristic", '-hf', default="zero",
                        choices=["zero", "weak", "strong"],
                        help="choose the heuristic to use with A* or Greedy Best First Search")
    parser.add_argument("--checks", "-c", action='store_true', default=False,
                        help="Enable consistency checks for the heuristic")
    parser.add_argument("--ansicolors", "-ac", action="store_true",
                        help="Print the dungeon on the console with ANSI colors (only works on some terminals)")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")