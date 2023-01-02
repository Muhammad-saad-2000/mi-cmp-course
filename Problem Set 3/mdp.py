from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, Iterable, List, Optional, Tuple, TypeVar, Union
from helpers.utils import CacheContainer, with_cache

# S and A are used for generic typing where S represents the state type and A represents the action type
S = TypeVar("S")
A = TypeVar("A")

# MarkovDecisionProcess is a generic abstract class for defining a Markov Decision Process
class MarkovDecisionProcess(ABC, Generic[S, A], CacheContainer):

    # Returns all possible states in this MDP (even terminal states)
    @abstractmethod
    def get_states(self) -> List[S]:
        pass

    # This function checks whether the given state is terminal or not
    @abstractmethod
    def is_terminal(self, state: S) -> bool:
        pass

    # This function returns the reward for a (state, action, next_state) tuple (aka R(s,a,s'))
    @abstractmethod
    def get_reward(self, state: S, action: A, next_state: S) -> float:
        pass

    # This function returns all the possible actions from the given state
    @abstractmethod
    def get_actions(self, state: S) -> List[A]:
        pass

    # Given a state and an action, this function returns 
    # all possible next states "s'" and their corresponding probabilities P(s'|s, a) as a dictionary 
    @abstractmethod
    def get_successor(self, state: S, action: A) -> Dict[S, float]:
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