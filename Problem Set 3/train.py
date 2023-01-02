from grid import GridMDP, GridEnv
from value_iteration import ValueIterationAgent
from policy_iteration import PolicyIterationAgent
from helpers.rl_utils import *
from reinforcement_learning import RLAgent, SARSALearningAgent, QLearningAgent, ApproximateQLearningAgent
from training_loops import q_agent_training_loop, sarsa_agent_training_loop
from features_grid import GridFeatureExtractor
import argparse, time

# Prints the training results to the console
def print_results(env: GridEnv, agent: Agent[Point, Direction]):
    size = env.mdp.size
    if isinstance(agent, ValueIterationAgent):
        print("Utility:")
        print(format_utilities(extract_utilities(env, agent), size))
        print()
    if isinstance(agent, PolicyIterationAgent):
        print("Utility:")
        print(format_utilities(extract_utilities(env, agent), size))
        print("Policy:")
        print(format_utilities(extract_policy(env, agent), size))
        print()
    elif isinstance(agent, RLAgent):
        print("Q-Values:")
        print(format_q_values(extract_q_values(env, agent), size))
        print()
    print("Policy:")
    print(format_policy(extract_policy(env, agent), size))
    print()

# Train a value iteration agent
def train_value_iteration(args: argparse.Namespace):
    print("Training a Value Iteration Agent...")
    
    # Create the requested GridMDP
    mdp = GridMDP.from_file(args.level)
    if args.noise is not None: # if set, the noise argument will override the default action noise in the MDP
        mdp.noise = args.noise
    
    # Create an environment that wraps the MDP
    env = GridEnv(mdp)
    env.reset()

    # Create the Value iteration agent
    agent = ValueIterationAgent(mdp, args.discount)

    print_frequency = args.verbosity # How frequently should the agent results be printed
    tolerance = args.tolerance

    # Apply value iteration for the given number of iterations 
    for iteration in range(int(args.iterations)):
        converged = agent.update(tolerance)
        if converged:
            print(f"Coverged in {iteration + 1} iterations")
            break

        # if requested, print the intermediate agent results (Utility & Policy)
        if print_frequency != 0 and iteration % print_frequency == 0:
            print(f"Results after {iteration} iterations:")
            print_results(env, agent)
    
    # print the agent results (Utility & Policy) after training was finished
    print("Final Results:")
    print_results(env, agent)

    # save the model utilities to a file
    agent.save(env, args.model)

# Train a policy iteration agent
def train_policy_iteration(args: argparse.Namespace):
    print("Training a Policy Iteration Agent...")
    
    # Create the requested GridMDP
    mdp = GridMDP.from_file(args.level)
    if args.noise is not None: # if set, the noise argument will override the default action noise in the MDP
        mdp.noise = args.noise
    
    # Create an environment that wraps the MDP
    env = GridEnv(mdp)
    env.reset()

    # Create the Value iteration agent
    agent = PolicyIterationAgent(mdp, args.discount)

    print_frequency = args.verbosity # How frequently should the agent results be printed

    # Apply value iteration for the given number of iterations 
    for iteration in range(int(args.iterations)):
        converged = agent.update()
        if converged:
            print(f"Coverged in {iteration + 1} iterations")
            break

        # if requested, print the intermediate agent results (Utility & Policy)
        if print_frequency != 0 and iteration % print_frequency == 0:
            print(f"Results after {iteration} iterations:")
            print_results(env, agent)
    
    # print the agent results (Utility & Policy) after training was finished
    print("Final Results:")
    print_results(env, agent)

    # save the model utilities & policy to a file
    agent.save(env, args.model)

# Train a SARSA iteration agent
def train_sarsa(args: argparse.Namespace):
    print("Training a SARSA Agent...")

    # Create the SARSA agent
    agent = SARSALearningAgent(ACTIONS, args.discount, args.epsilon, args.learning_rate, args.seed)
    
    # Create the environment and override the default action noise if requested
    env = GridEnv.from_file(args.level)
    if args.noise is not None:
        env.mdp.noise = args.noise
    
    print_frequency = args.verbosity # How frequently should the agent results be printed

    # This callback function will be called after every agent update
    # It will be used to print intermediate results if requested
    def callback(iteration):
        if print_frequency != 0 and iteration % print_frequency == 0:
            print(f"Results after {iteration} iterations:")
            print_results(env, agent)
    
    # Run the SARSA agent training loop
    sarsa_agent_training_loop(env, agent, args.iterations, args.step_limit, args.seed, callback)
    
    # print the agent results (Q-values & Policy) after training was finished
    print("Final Results:")
    print_results(env, agent)

    # save the model utilities to a file
    agent.save(env, args.model)

def train_q_learning(args: argparse.Namespace):
    
    # Created the requested agent (tabular or approximate)
    agent_type = args.agent
    if agent_type == "q_learning":
        print("Training a Q Learning Agent...")
        agent = QLearningAgent(ACTIONS, args.discount, args.epsilon, args.learning_rate, args.seed)
    elif agent_type == "q_learning_approx":
        print("Training a Approximate Q Learning Agent...")
        agent = ApproximateQLearningAgent(GridFeatureExtractor(), ACTIONS, args.discount, args.epsilon, args.learning_rate)
    else:
        print(f"Requested Agent '{agent_type}' is invalid")
        exit(-1)

    # Create the environment and override the default action noise if requested
    env = GridEnv.from_file(args.level)
    if args.noise is not None:
        env.mdp.noise = args.noise
    
    print_frequency = args.verbosity # How frequently should the agent results be printed
    
    # This callback function will be called after every agent update
    # It will be used to print intermediate results if requested
    def callback(iteration):
        if print_frequency != 0 and iteration % print_frequency == 0:
            print(f"Results after {iteration} iterations:")
            print_results(env, agent)
    
    # Run the Q-learning agent training loop
    q_agent_training_loop(env, agent, args.iterations, args.step_limit, args.seed, callback)
    
    # print the agent results (Q-values & Policy) after training was finished
    print("Final Results:")
    print_results(env, agent)

    # save the model utilities to a file
    agent.save(env, args.model)

def main(args: argparse.Namespace):
    start = time.time() # Track run time

    # Create and train an agent of the requested type 
    agent_type: str = args.agent
    if agent_type == "value_iteration":
        train_value_iteration(args)
    if agent_type == "policy_iteration":
        train_policy_iteration(args)
    elif agent_type == "sarsa":
        train_sarsa(args)
    elif agent_type.startswith("q_learning"):
        train_q_learning(args)
    else:
        print(f"Requested Agent '{agent_type}' is invalid")
        exit(-1)
    
    # Finally print the elapsed time for the whole process
    print(f"Elapsed time: {time.time() - start} seconds")

if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Train an agent in a Grid Environment")
    parser.add_argument("agent", type=str, choices=["value_iteration", "policy_iteration", "sarsa", "q_learning", "q_learning_approx"])
    parser.add_argument("level", type=str, help="path to the level to play")
    parser.add_argument("model", type=str, help="path to the model to save after training")
    parser.add_argument("--iterations", "-i", type=int, default=100, help="the number of training iteration")
    parser.add_argument("--tolerance", "-t", type=float, default=0, help="the tolerence of the convergence check in Value Iteration")
    parser.add_argument("--step-limit", "-sl", type=int, default=100,
                        help="the maximum number of steps per episode (For SARSA & Q-Learning Only)")
    parser.add_argument("--discount", "-d", type=float, default=0.9, help="the discount factor")
    parser.add_argument("--epsilon", "-e", type=float, default=0.5,
                        help="the epsilon value of the e-greedy q-learning agent (For SARSA & Q-Learning Only)")
    parser.add_argument("--learning-rate", "-lr", type=float, default=0.05, help="the learning rate (For SARSA & Q-Learning Only)")
    parser.add_argument("--noise", "-n", type=float, help="the action noise (if set, overrides the original value from level file)")
    parser.add_argument("--seed", "-s", type=int, default=time.time_ns(), help="the seed value used for training (To ensure reproducibility)")
    parser.add_argument("--verbosity", "-v", type=int, default=0, help="How often to display the training results (0 will display at the end only)")
    parser.add_argument("--sleep", type=float, default=0, help="How much time (seconds) to wait between iterations")

    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")