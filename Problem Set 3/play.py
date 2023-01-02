import time
from grid import GridEnv, GridMDP
from agents import HumanAgent, RandomAgent
from value_iteration import ValueIterationAgent
from policy_iteration import PolicyIterationAgent
from reinforcement_learning import SARSALearningAgent, QLearningAgent, ApproximateQLearningAgent
from features_grid import GridFeatureExtractor
import argparse

from mathutils import Direction, Point

ACTIONS = [Direction.LEFT, Direction.RIGHT, Direction.DOWN, Direction.UP]

# Create an agent based on the user selections
def create_agent(env: GridEnv, args: argparse.Namespace):
    agent_type = args.agent
    if agent_type == "human":
        # This function reads the action from the user (human)
        def grid_user_action(env: GridEnv, state: Point) -> int:
            possible_actions = env.actions()
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
        return HumanAgent(grid_user_action)

    elif agent_type == "random":
        return RandomAgent(args.seed)
    
    elif agent_type == "value_iteration":
        agent = ValueIterationAgent(env.mdp, args.discount)
    
    elif agent_type == "policy_iteration":
        agent = PolicyIterationAgent(env.mdp, args.discount)
    
    elif agent_type == "sarsa":
        agent = SARSALearningAgent(ACTIONS, args.discount)
    
    elif agent_type == "q_learning":
        agent = QLearningAgent(ACTIONS, args.discount)
    
    elif agent_type == "q_learning_approx":
        agent = ApproximateQLearningAgent(GridFeatureExtractor(), ACTIONS, args.discount)
    
    else:
        print(f"Requested Agent '{agent_type}' is invalid")
        exit(-1)

    # The model file is supplied, we load the pretrained model file
    # To train a model, run "train.py"
    if args.model: agent.load(env, args.model)
    
    return agent

def main(args: argparse.Namespace):
    start = time.time() # Track run time
    
    env = GridEnv.from_file(args.level) # create the environment
    if args.noise is not None:
        env.mdp.noise = args.noise
    
    # Reset the environment and get the initial state
    state = env.reset(args.seed)
    print("Initial State:")
    env.render() # Render the environment to the console
    print()
    
    agent = create_agent(env, args) # Create the requested agent
    
    step = 0 # This will store the current step
    total_reward = 0 # This will store the total amount of reward gained while playing
    
    while True:
        
        # if requested, sleep for a certain amount of time between actions
        if args.sleep != 0:
            time.sleep(args.sleep)
        
        
        action = agent.act(env, state) # Request an action from the agent
        
        # Apply the action to the environment
        state, reward, done, _ = env.step(action)
        
        # Increment the step count and accumulate the reward
        step += 1
        total_reward += reward

        # Print any useful information to the user
        print("Step:", step, "/ Action:", str(action), " / Reward:", reward)
        
        env.render() # Render the environment to the screen

        print()

        if done: # if the episode is done, we print the total gained reward and break out of the loop
            print("Total Reward:", total_reward)
            break
    
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")

if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play tree as Human or AI")
    parser.add_argument("level", help="Path to the tree to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'value_iteration', 'policy_iteration', 'sarsa', 'q_learning', 'q_learning_approx', 'random'],
                        help="The agent that will play the game")
    parser.add_argument("--model", "-m", type=str, default="", help="The model file to load")
    parser.add_argument("--discount", "-d", type=float, default=0.9, help="the discount factor")
    parser.add_argument("--noise", "-n", type=float, help="the action noise (if set, overrides the original value from level file)")
    parser.add_argument("--seed", "-s", type=int, default=time.time_ns(), help="the seed value used for training")
    parser.add_argument("--sleep", type=float, default=0, help="How much time (seconds) to wait between actions")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")