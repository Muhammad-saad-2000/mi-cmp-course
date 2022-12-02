from abc import ABC, abstractmethod
from typing import Callable, Generic
from game import HeuristicFunction, Game, S, A
from helpers.mt19937 import RandomGenerator

# This is an abstract class for all agents
class Agent(ABC, Generic[S, A]):
    def __init__(self) -> None:
        super().__init__()
    
    # Given a state within a problem, the agent should return the action that is should take
    @abstractmethod
    def act(self, game: Game[S, A], observation: S) -> A:
        pass

# The human agent requests the action from the user (human)
class HumanAgent(Agent[S, A]):
    def __init__(self, user_input_fn: Callable[[Game[S, A], S], A]) -> None:
        super().__init__()
        self.user_input_fn = user_input_fn

    def act(self, game: Game[S, A], state: S) -> A:
        return self.user_input_fn(game, state)

# The search agent requests the action from a search algorithm
class SearchAgent(Agent[S, A]):
    def __init__(self,
        search_fn: Callable[[Game[S, A], S, HeuristicFunction, int], A],
        heuristic: HeuristicFunction = (lambda *_: 0), 
        search_depth: int = -1) -> None:
        super().__init__()
        self.search_fn = search_fn
        self.heuristic = heuristic
        self.search_depth = search_depth
    
    def act(self, game: Game[S, A], state: S) -> A:
        _, action = self.search_fn(game, state, self.heuristic, self.search_depth)
        return action

# The random agent selects actions randomly
class RandomAgent(Agent[S, A]):
    def __init__(self, seed: int = None) -> None:
        super().__init__()
        self.rng = RandomGenerator(seed)

    def act(self, game: Game[S, A], state: S) -> A:
        actions = game.get_actions(state)
        return actions[self.rng.int(0, len(actions)-1)]