from problem import A, S, Problem
from .utils import add_call_listener

class InconsistentHeuristicException(Exception):
    pass

def test_heuristic_consistency(heuristic):
    def listener(next_state: S, problem: Problem[S, A], state: S, action: A):
        h = heuristic(problem, state)
        next_h = heuristic(problem, next_state)
        c = problem.get_cost(state, action)
        if h - next_h > c:
            message = f"State (heuristic = {h}):" + "\n" + str(state) + "\n"
            message += f"Action: {str(action)} (cost = {c})" + "\n"
            message += f"Next State (heuristic = {next_h}):" + "\n" + str(next_state) + "\n"
            message += "Decrease in heuristic exceeds the actions cost\n"
            message += f"h(state) - h(next state) = {h} - {next_h} = {h - next_h} > {c} (action cost)"
            raise InconsistentHeuristicException(message)
    return add_call_listener(listener)