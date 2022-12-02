import time
from tree import TreeGame, TreeNode, tree_heuristic
from agents import HumanAgent, SearchAgent, RandomAgent
from helpers.utils import fetch_recorded_calls
from helpers.pruned_tree import pruned_tree_string
from helpers.mt19937 import RandomGenerator
import argparse

seed_gen = RandomGenerator(0)

# Return the heuristic selected by the user
def get_heuristic(name: str):
    if name == "zero":
        return lambda *_: 0
    if name == "heuristic":
        return tree_heuristic
    print(f"Requested Heuristic '{name}' is invalid")
    exit(-1)

# Create an agent based on the user selections
def create_agent(agent_type: str, heuristic_type: str):
    if agent_type == "human":
        # This function reads the action from the user (human)
        def tree_user_action(game: TreeGame, state: TreeNode) -> int:
            possible_actions = list(game.get_actions(state))
            while True:
                if possible_actions:
                    action_prompt = "Possible actions:\n"
                    action_prompt += ''.join(f'{action}' for action in possible_actions)
                    print(action_prompt)
                else:
                    print("No possible actions. Press Ctrl+C to exit.")
                action = input("Choose an action: ").strip()
                if action in possible_actions:
                    return action
                print("Invalid Action")
        return HumanAgent(tree_user_action)
    if agent_type == "minimax":
        from search import minimax
        return SearchAgent(minimax)
    if agent_type == "alphabeta":
        from search import alphabeta
        return SearchAgent(alphabeta)
    if agent_type == "alphabeta_order":
        from search import alphabeta_with_move_ordering
        return SearchAgent(alphabeta_with_move_ordering, get_heuristic(heuristic_type))
    if agent_type == "expectimax":
        from search import expectimax
        return SearchAgent(expectimax)
    if agent_type == "random":
        return RandomAgent(seed_gen.generate())
    print(f"Requested Agent '{agent_type}' is invalid")
    exit(-1)

def main(args: argparse.Namespace):
    start = time.time() # Track run time
    game = TreeGame.from_file(args.tree) # create the problem
    
    # Get the initial state
    state = game.get_initial_state()
    print("Initial State:")
    print(state)
    
    # create the agents that will play the game
    agent_types = [args.agent, args.adversary]
    agents = [create_agent(agent_type, args.heuristic) for agent_type in agent_types]
    
    step = 0 # This will store the current step
    
    while True:
        
        # check if the state is terminal and break if true
        terminal, values = game.is_terminal(state)
        if terminal:
            print("Final Values:", values)
            break

        # if requested, sleep for a certain amount of time between actions
        if args.sleep != 0:
            time.sleep(args.sleep)
        
        fetch_recorded_calls(TreeGame.is_terminal) # Clear the recorded calls
        
        # if this is the turn of the first player, increment the step counter
        if turn == 0: step += 1
        
        turn = game.get_turn(state) # get the current turn
        agent = agents[turn] # get the agent that will play the current turn
        action = agent.act(game, state) # Request an action from the agent
        
        # Retrieve the traversed nodes, if the current agent is a search agent
        if isinstance(agent, SearchAgent):
            explored_nodes = [call["args"][1].name for call in list(fetch_recorded_calls(TreeGame.is_terminal))]
            print(f"The agent explored {len(explored_nodes)} Node(s): {', '.join(explored_nodes)}")
            # if drawing the pruned tree is requested and the search function uses alpha beta pruning
            # draw the pruned tree
            if args.show_pruning and "alphabeta" in agent_types[turn]:
                print("Pruned Tree:")
                print(pruned_tree_string(state, explored_nodes))
        
        # Apply the action to the state
        state = game.get_successor(state, action)
        
        # Print any useful information to the user
        print("Step:", step, "/ Turn:", turn, "/ Action:", str(action))
        print(state)

        print()
    
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")

if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play tree as Human or AI")
    parser.add_argument("tree", help="path to the tree to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'minimax', 'alphabeta', 'alphabeta_order', 'expectimax', 'random'],
                        help="the agent that will play the game")
    parser.add_argument("--adversary", "-adv", default="human",
                        choices=['human', 'minimax', 'alphabeta', 'alphabeta_order', 'expectimax', 'random'],
                        help="the agent that will play as your adversary (enemy) the game")
    parser.add_argument("--heuristic", '-hf', default="zero",
                        choices=["zero", "heuristic"],
                        help="choose the heuristic to use")
    parser.add_argument("--show-pruning", "-sp", action='store_true', default=False,
                        help="Draw the pruned tree in case the agent uses Alpha Beta pruning")
    parser.add_argument("--sleep", "-s", type=float, default=0, help="How much time (seconds) to wait between actions")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")