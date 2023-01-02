from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar, Union
from helpers.utils import CacheContainer, with_cache
from mdp import S, A

# Game is a generic abstract class for game definitions
# It also implements 'CacheContainer' which allows you to call the "cache" method
# which returns a dictionary in which you can store any data you want to cache
# The base class for all environments
class Environment(ABC, Generic[S, A], CacheContainer):
    
    # Resets the environment to the initial state and returns that initial state
    # seed: the seed for any random number generator to ensure reproducibility
    @abstractmethod
    def reset(self, seed: Optional[int] = None) -> S:
        pass

    # Returns a list of all the actions that can be taken in the current state
    @abstractmethod
    def actions(self) -> List[A]:
        pass

    # Applies an action "a" to the current state "s" and returns the following:
    # - s': The next state after applying the action
    # - R(s,a,s'): The reward
    # - done: Whether the new state "s'" is a terminal state or not
    # - info: a dictionary of info about the environment. It could be empty or contain debugging information.
    @abstractmethod
    def step(self, action: A) -> Tuple[S, float, bool, Dict]:
        pass

    # Print the current state to the console
    def render(self):
        pass

    #############################################################
    # Utility functions to convert strings to states/actions and vice versa 

    @abstractmethod
    def parse_state(self, string: str) -> S:
        pass

    @abstractmethod
    def format_state(self, state: S) -> str:
        pass

    @abstractmethod
    def parse_action(self, string: str) -> A:
        pass

    @abstractmethod
    def format_action(self, action: A) -> str:
        pass