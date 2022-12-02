from dungeon import DungeonGame, Direction, DungeonState, DungeonTile, MonsterAgent
from agents import HumanAgent, SearchAgent, RandomAgent
from helpers.utils import fetch_tracked_call_count
import argparse, time

def colored_dungeon(level: str):
    from helpers.utils import bcolors
    header, level = level.split('\n', 1)
    level = level.replace(DungeonTile.COIN, f'{bcolors.BRIGHT_GREEN}{DungeonTile.COIN}{bcolors.ENDC}')
    level = level.replace(DungeonTile.PLAYER, f'{bcolors.YELLOW}{DungeonTile.PLAYER}{bcolors.ENDC}')
    level = level.replace(DungeonTile.WALL, f'{bcolors.BRIGHT_BLACK}{DungeonTile.WALL}{bcolors.ENDC}')
    level = level.replace(DungeonTile.EMPTY, f'{bcolors.BRIGHT_BLACK}{DungeonTile.EMPTY}{bcolors.ENDC}')
    level = level.replace(DungeonTile.KEY, f'{bcolors.BLUE}{DungeonTile.KEY}{bcolors.ENDC}')
    level = level.replace(DungeonTile.EXIT, f'{bcolors.BRIGHT_BLUE}{DungeonTile.EXIT}{bcolors.ENDC}')
    level = level.replace(DungeonTile.MONSTER, f'{bcolors.BRIGHT_RED}{DungeonTile.MONSTER}{bcolors.ENDC}')
    level = level.replace(DungeonTile.DAGGER, f'{bcolors.BRIGHT_GREEN}{DungeonTile.DAGGER}{bcolors.ENDC}')
    return f"{header}\n{level}"

# Return the heuristic selected by the user
def get_heuristic(name: str):
    if name == "zero":
        return lambda *_: 0
    if name == "heuristic":
        from dungeon import dungeon_heuristic
        return dungeon_heuristic
    print(f"Requested Heuristic '{name}' is invalid")
    exit(-1)

# Create an agent based on the user selections
def create_agent(args: argparse.Namespace):
    agent_type: str = args.agent
    if agent_type == "human":
        # This function reads the action from the user (human)
        def dungeon_user_action(problem: DungeonGame, state: DungeonState) -> Direction:
            possible_actions = list(problem.get_actions(state))
            while True:
                user_input = input("Enter action (WASD or Nothing): ").strip().lower()
                action = {
                    'w': Direction.UP,
                    's': Direction.DOWN,
                    'a': Direction.LEFT,
                    'd': Direction.RIGHT,
                    '': Direction.NONE
                }.get(user_input)
                if action in possible_actions:
                    return action
                else:
                    print("Invalid Action")
        return HumanAgent(dungeon_user_action)
    if agent_type == "random":
        return RandomAgent(402)
    if agent_type == "greedy":
        from search import greedy
        heuristic = get_heuristic(args.heuristic)
        return SearchAgent(greedy, heuristic, -1)
    if agent_type == "minimax":
        from search import minimax
        heuristic = get_heuristic(args.heuristic)
        return SearchAgent(minimax, heuristic, args.depth)
    if agent_type == "alphabeta":
        from search import alphabeta
        heuristic = get_heuristic(args.heuristic)
        return SearchAgent(alphabeta, heuristic, args.depth)
    if agent_type == "alphabeta_order":
        from search import alphabeta_with_move_ordering
        heuristic = get_heuristic(args.heuristic)
        return SearchAgent(alphabeta_with_move_ordering, heuristic, args.depth)
    if agent_type == "expectimax":
        from search import expectimax
        heuristic = get_heuristic(args.heuristic)
        return SearchAgent(expectimax, heuristic, args.depth)
    print(f"Requested Agent '{agent_type}' is invalid")
    exit(-1)

def main(args: argparse.Namespace):
    state_printer = lambda state: print(state)
    if args.ansicolors: state_printer = lambda state: print(colored_dungeon(str(state)))

    start = time.time() # Track run time
    game = DungeonGame.from_file(args.level) # create the game
    state = game.get_initial_state() # Get the initial state
    print("Initial State:")
    state_printer(state)

    # create the agents that will play the game
    agents = [create_agent(args), *(MonsterAgent(index) for index in range(game.agent_count - 1))]
    
    step = 0 # This will store the current step
    
    while True:

        # check if the state is terminal and break if true
        terminal, values = game.is_terminal(state)
        if terminal:
            value = values[0]
            if value > 0:
                print("YOU WON")
                print("Score:", state.score())
            else:
                print("YOU LOST")
            break

        # if requested, sleep for a certain amount of time between actions
        if args.sleep != 0:
            time.sleep(args.sleep)

        fetch_tracked_call_count(DungeonGame.is_terminal) # Clear the call counter
        
        # if this is the turn of the first player, increment the step counter
        if turn == 0: step += 1

        turn = game.get_turn(state) # get the current turn
        agent = agents[turn] # get the agent that will play the current turn
        action = agent.act(game, state) # Request an action from the agent
        
        # Get the number of explored nodes, if the current agent is a search agent
        if isinstance(agent, SearchAgent):
            print("Explored Nodes:", fetch_tracked_call_count(DungeonGame.is_terminal))
        
        # Apply the action to the state
        state = game.get_successor(state, action)
        
        # Print any useful information to the user
        print("Step:", step, "/ Turn:", turn, "/ Action:", str(action))
        state_printer(state)
    
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")


if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play Dungeon as Human or AI")
    parser.add_argument("level", help="path to the dungeon to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'greedy', 'random', 'minimax', 'alphabeta', 'alphabeta_order', 'expectimax'],
                        help="the agent that will play the game")
    parser.add_argument("--heuristic", '-hf', default="zero",
                        choices=["zero", "heuristic"],
                        help="choose the heuristic to use")
    parser.add_argument("--depth", "-d", type=int, default=5, help="How deep the algorithms should search")
    parser.add_argument("--ansicolors", "-ac", action="store_true",
                        help="Print the dungeon on the console with ANSI colors (only works on some terminals)")
    parser.add_argument("--sleep", "-s", type=float, default=0, help="How much time (seconds) to wait between actions")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")