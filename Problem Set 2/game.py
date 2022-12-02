from abc import ABC, abstractmethod
from typing import Callable, Generic, Iterable, List, Optional, Tuple, TypeVar, Union
from helpers.utils import CacheContainer, with_cache

# S and A are used for generic typing where S represents the state type and A represents the action type
S = TypeVar("S")
A = TypeVar("A")

# Game is a generic abstract class for game definitions
# It also implements 'CacheContainer' which allows you to call the "cache" method
# which returns a dictionary in which you can store any data you want to cache
class Game(ABC, Generic[S, A], CacheContainer):
    # This function returns the initial state
    @abstractmethod
    def get_initial_state(self) -> S:
        pass

    # How many agents are playing this game
    @property
    def agent_count(self) -> int:
        return 1

    # This function returns a tuple containing:
    # 1- A boolean that determinces whether the given state is terminal or not
    # 2- A list of terminal values for all agents if this is a terminal state, or None otherwise.
    # In the list of terminal values, the value of the state for the agent 'i' will be be at the index 'i'.
    # So for example, if the game contains two players fighting each other, values[0] will be the state's value
    # for player 1 and value[1] will be the state's value for player 2. Usually, the value[0] = -value[1] since
    # they are enemies and if one of them receives a positive value (reward) in a certain state, the other will most likely
    # receive a negative value (penalty).
    @abstractmethod
    def is_terminal(self, state: S) -> Tuple[bool, Optional[List[float]]]:
        pass

    # This function returns the index of the agent whose turn in now
    # The returned value will be between 0 and (game.agent_count - 1).
    @abstractmethod
    def get_turn(self, state: S) -> int:
        pass

    # This function returns all the possible actions from the given state
    @abstractmethod
    def get_actions(self, state: S) -> List[A]:
        pass

    # Given a state and an action, this function returns the next state 
    @abstractmethod
    def get_successor(self, state: S, action: A) -> S:
        pass

# A heuristic function which estimates the value of a given state for a certain agent within a certain game.
# E.g. if the heuristic function returns a high value for a certain agent, it should return low values for their enemies.
HeuristicFunction = Callable[[Game[S, A], S, int], float]