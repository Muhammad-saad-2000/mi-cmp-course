from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, List, TypeVar, Union
from helpers.utils import CacheContainer, with_cache

# S and A are used for generic typing where S represents the state type and A represents the action type
S = TypeVar("S")
A = TypeVar("A")

# Problem is a generic abstract class for search problems
# It also implements 'CacheContainer' which allows you to call the "cache" method
# which returns a dictionary in which you can store any data you want to cache
class Problem(ABC, Generic[S, A], CacheContainer):
    # This function returns the initial state
    @abstractmethod
    def get_initial_state(self) -> S:
        pass

    # This function checks whether the given state is a goal or not
    @abstractmethod
    def is_goal(self, state: S) -> bool:
        pass

    # This function returns all the possible actions from the given state
    @abstractmethod
    def get_actions(self, state: S) -> Iterable[A]:
        pass

    # Given a state and an action, this function returns the next state 
    @abstractmethod
    def get_successor(self, state: S, action: A) -> S:
        pass

    # Given a state and an action, this function computes the action cost
    def get_cost(self, state: S, action: A) -> float:
        return 1.0

# These are type aliases for:
# A solution which is a list of actions (or None if no solution is found)
Solution = Union[List[A], None]
# A heuristic function which estimates the path cost to the goal for a given state with a certain problem
HeuristicFunction = Callable[[Problem[S, A], S],float]