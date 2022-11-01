import time
from graph import GraphRoutingProblem, GraphNode, graphrouting_heuristic
from agents import HumanAgent, UninformedSearchAgent, InformedSearchAgent
from helpers.utils import fetch_recorded_calls
import argparse, os, json

# Create an agent based on the user selections
def create_agent(args: argparse.Namespace):
    agent_type: str = args.agent
    if agent_type == "human":
        # This function reads the action from the user (human)
        def graph_user_action(problem: GraphRoutingProblem, state: GraphNode) -> GraphNode:
            possible_actions = list(problem.get_actions(state))
            node_map = {node.name: node for node in possible_actions}
            while True:
                if possible_actions:
                    action_prompt = "Possible actions:\n"
                    action_prompt += '\n'.join(f'{name} (cost: {problem.get_cost(state, action)})' for name, action in node_map.items())
                    print(action_prompt)
                else:
                    print("No possible actions. Press Ctrl+C to exit.")
                user_input = input("Choose an action: ").strip()
                action = node_map.get(user_input)
                if action in possible_actions:
                    return action
                else:
                    print("Invalid Action")
        return HumanAgent(graph_user_action)
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
        return InformedSearchAgent(AStarSearch, graphrouting_heuristic)
    if agent_type == "gbfs":
        from search import BestFirstSearch
        return InformedSearchAgent(BestFirstSearch, graphrouting_heuristic)
    print(f"Requested Agent '{agent_type}' is invalid")
    exit(-1)

def main(args: argparse.Namespace):
    start = time.time() # Track run time
    graph_path = args.graph
    problem = GraphRoutingProblem.from_file(graph_path) # create the problem
    # Check if there is a figure for the graph that we can display on the console
    figure_path = json.load(open(graph_path, 'r')).get("figure")
    figure = None
    if figure_path:
        figure_path = os.path.join(os.path.dirname(graph_path), figure_path)
        figure = open(figure_path, 'r').read()
    # Get the initial state
    state = problem.get_initial_state()
    print("Initial State:")
    if figure:
        print(figure)
    print("Current Node:", state)
    agent = create_agent(args)
    step = 0 # This will store the current step
    path_cost = 0 # This will store the total path cost
    traversed_nodes = [] # This will store all the traversed nodes in order of traversal
    unsolvable = False # This will store whether the problem is unsolvable or not
    while not problem.is_goal(state):
        fetch_recorded_calls(GraphRoutingProblem.is_goal) # Clear the recorded calls
        action = agent.act(problem, state) # Request an action from the agent
        # Retrieve the traversed nodes
        traversed_nodes += [call["args"][1].name for call in list(fetch_recorded_calls(GraphRoutingProblem.is_goal))]
        # If no solution was found, break
        if action is None:
            print("Agent cannot find a solution, exiting...")
            unsolvable = True
            break
        # Get the cost and add it to the path cost
        cost = problem.get_cost(state, action)
        path_cost += cost
        # Apply the action to the state
        state = problem.get_successor(state, action)
        step += 1
        # Print any useful information to the user
        print("Step:", step)
        print("Action:", str(action), f"(cost: {cost})")
        if figure:
            print(figure)
        print("Current Node:", state)
    if not unsolvable: print("YOU WON!!")
    print("Path Cost:", path_cost)
    # This was a search agent, display the traversed nodes
    if not isinstance(agent, HumanAgent):
        print(f"Traversal Order: {'->'.join(traversed_nodes)}")
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")

if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play Graph as Human or AI")
    parser.add_argument("graph", help="path to the graph to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'bfs', 'dfs', 'ucs', 'astar', 'gbfs'],
                        help="the agent that will play the game")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")