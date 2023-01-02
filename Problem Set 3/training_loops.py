from typing import Callable, Optional, Union
from environment import Environment
from helpers.mt19937 import RandomGenerator
from mdp import A, S
from base_rl import RLAgent

# This training loop is used to train a SARSA agent
# It does not store any experience; instead it updates the agent as soon as a transition is done
# then the transition is discarded
def sarsa_agent_training_loop(
    env: Environment[S, A], agent: RLAgent[S, A], 
    iterations: int, step_limit: int, seed: int,
    callback: Optional[Callable[[int], None]] = None):

    prev_transition = None # This will store the previous State, Action & Reward
    done = False # Store whether the past transition lead to a terminal state
    step = 0 # the number of steps taking in the current episode
    
    seed_gen = RandomGenerator(seed) # a random seed generator used to seed the environment on reset

    state = env.reset(seed_gen.generate()) # reset the environment and retrieve the initial state

    # loop for a certain number of updates
    iteration = 0
    while iteration < iterations:
        
        # if the episode ended or we spent to long in it, we restart the episode
        if done or step == step_limit:
            if done: # if this is a terminal state, we update the agent where next_action = None
                agent.update(env, *prev_transition, state, None)
                if callback: callback(iteration) # call the callback after every update
                iteration += 1
            # reset the environment, steps and clear the previous transition
            state = env.reset(seed_gen.generate())
            step = 0
            prev_transition = None
        
        # Ask the agent for an action in training mode to enable exploration (if epsilon > 0)
        action = agent.act(env, state, training=True)
        # Act on the environment
        next_state, reward, done, _ = env.step(action)

        # if there is previous transition stored, we update the agent
        if prev_transition is not None:
            agent.update(env, *prev_transition, state, action)
            step += 1
            if callback: callback(iteration) # call the callback after every update
            iteration += 1

        prev_transition = (state, action, reward) # store the new transition
        state = next_state # move to the new state

# This training loop is used to train a SARSA agent
# It does not store any experience; instead it updates the agent as soon as a transition is done
# then the transition is discarded
def q_agent_training_loop(
    env: Environment[S, A], agent: RLAgent[S, A], 
    iterations: int, step_limit: int, seed: int,
    callback: Optional[Callable[[int], None]] = None):

    seed_gen = RandomGenerator(seed) # a random seed generator used to seed the environment on reset

    state = env.reset(seed_gen.generate()) # reset the environment and retrieve the initial state

    step = 0 # the number of steps taking in the current episode
    
    # loop for a certain number of updates
    for iteration in range(iterations):
        
        # Ask the agent for an action in training mode to enable exploration (if epsilon > 0)
        action = agent.act(env, state, training=True)
        # Act on the environment
        next_state, reward, done, _ = env.step(action)

        # update the agent
        agent.update(env, state, action, reward, next_state, done)
        if callback: callback(iteration) # call the callback after every update

        state = next_state # move to the new state
        
        step += 1

        # if the episode ended or we spent to long in it, we restart the episode
        if done or step == step_limit:
            state = env.reset(seed_gen.generate())
            step = 0