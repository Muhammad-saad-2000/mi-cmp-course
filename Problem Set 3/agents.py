from typing import Callable, Generic
from environment import Environment, S, A
from helpers.mt19937 import RandomGenerator

# This is an abstract class for all agents
class Agent(Generic[S, A]):
    def __init__(self) -> None:
        super().__init__()
    
    # Given a state within a problem, the agent should return the action that is should take
    def act(self, env: Environment[S, A], observation: S) -> A:
        return env.actions()[0]

# The human agent requests the action from the user (human)
class HumanAgent(Agent[S, A]):
    def __init__(self, user_input_fn: Callable[[Environment[S, A], S], A]) -> None:
        super().__init__()
        self.user_input_fn = user_input_fn

    def act(self, env: Environment[S, A], state: S) -> A:
        return self.user_input_fn(env, state)

# The random agent selects actions randomly
class RandomAgent(Agent[S, A]):
    def __init__(self, seed: int = None) -> None:
        super().__init__()
        self.rng = RandomGenerator(seed)

    def act(self, env: Environment[S, A], state: S) -> A:
        actions = env.actions()
        return actions[self.rng.int(0, len(actions)-1)]