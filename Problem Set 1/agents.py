from abc import ABC, abstractmethod
from typing import Callable, Dict, Generic, List
from problem import HeuristicFunction, Problem, S, A, Solution

# This is an abstract class for all goal based agents
class GoalBasedAgent(ABC, Generic[S, A]):
    def __init__(self) -> None:
        super().__init__()
    
    # Given a state within a problem, the agent should return the action that is should take
    @abstractmethod
    def act(self, problem: Problem[S, A], observation: S) -> A:
        pass

# The human agent requests the action from the user (human)
class HumanAgent(GoalBasedAgent[S, A]):
    def __init__(self, user_input_fn: Callable[[Problem[S, A], S], A]) -> None:
        super().__init__()
        self.user_input_fn = user_input_fn

    def act(self, problem: Problem[S, A], state: S) -> A:
        return self.user_input_fn(problem, state)

# This agent applies an uninformed search algorithm to find the solution to goal for the given state
class UninformedSearchAgent(GoalBasedAgent[S, A]):
    def __init__(self, search_fn: Callable[[Problem[S, A], S], Solution]) -> None:
        super().__init__()
        self.search_fn = search_fn
        # The policy will store the action to do for each state so as not to search again after each observation
        self.policy: Dict[S, A] = {}
    
    def act(self, problem: Problem[S, A], state: S) -> A:
        # This state is not stored in the policy, we need to search for a solution 
        if state not in self.policy:
            solution = self.search_fn(problem, state)
            # if no solution was found, we return None
            if solution is None:
                self.policy[state] = None
                return None
            # Otherwise, we go through the solution path and store the action to do in each state into the policy
            current = state
            for action in solution:
                self.policy[current] = action
                current = problem.get_successor(current, action)
        return self.policy.get(state)

# This agent applies an informed search algorithm to find the solution to goal for the given state
class InformedSearchAgent(GoalBasedAgent[S, A]):
    def __init__(self, search_fn: Callable[[Problem[S, A], S, HeuristicFunction], Solution], heuristic: HeuristicFunction) -> None:
        super().__init__()
        self.search_fn = search_fn
        self.heuristic = heuristic
        # The policy will store the action to do for each state so as not to search again after each observation
        self.policy: Dict[S, A] = {}
    
    def act(self, problem: Problem[S, A], state: S) -> A:
        # This state is not stored in the policy, we need to search for a solution 
        if state not in self.policy:
            solution = self.search_fn(problem, state, self.heuristic)
            # if no solution was found, we return None
            if solution is None:
                self.policy[state] = None
                return None
            # Otherwise, we go through the solution path and store the action to do in each state into the policy
            current = state
            for action in solution:
                self.policy[current] = action
                current = problem.get_successor(current, action)
        return self.policy.get(state)