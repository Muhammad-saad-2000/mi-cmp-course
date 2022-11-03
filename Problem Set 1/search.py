from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers import utils
#COMMENT:
from queue import PriorityQueue
from dataclasses import dataclass

# COMMENT: Those are the only functions you need to implement
def PopFromQueue(queue, node):
    index = queue.queue.index(node)
    if index != -1:
        return queue.queue.pop(index)
    return None

def IsInFrontier(frontier, state):
    for item in frontier:
        if item[0] == state:
            return True
    return False

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    frontier = deque()# COMMENT: This is a regular queue (FIFO)
    explored = set()
    if problem.is_goal(initial_state):# COMMENT: Check if the initial state is the goal state
        return []
    frontier.append((initial_state,[]))# COMMENT: The path should be taken into consideration
    while frontier:
        state, path = frontier.popleft()# COMMENT: The state item is popped according to FIFO
        explored.add(state)
        for action in problem.get_actions(state):# COMMENT: Get all the actions that can be taken from the current state
            successor = problem.get_successor(state, action) # COMMENT: Apply the action to the current state to get the successor
            if successor not in explored and not IsInFrontier(frontier,successor):# COMMENT: Check if the successor is already explored
                successor_path = path + [action]# COMMENT: Callculate the comulative path to the successor
                if problem.is_goal(successor):# COMMENT: Check if the successor is the goal state (before adding it to the frontier)
                    return successor_path
                frontier.append((successor, successor_path))# COMMENT: Add the successor to the frontier (if it is not the goal state)
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    frontier = deque()# COMMENT: This is a regular stack (LIFO)
    explored = set()
    frontier.append((initial_state,[]))# COMMENT: The path should be taken into consideration
    while frontier:
        state, path = frontier.pop()# COMMENT: The state item is popped according to LIFO
        if problem.is_goal(state):# COMMENT: Check if the state is the goal state (when it is popped from the frontier)
            return path
        explored.add(state)
        for action in problem.get_actions(state):# COMMENT: Get all the actions that can be taken from the current state
            successor = problem.get_successor(state, action)# COMMENT: Apply the action to the current state to get the successor
            successor_path = path + [action]# COMMENT: Callculate the comulative path to the successor
            if successor not in explored:# COMMENT: Check if the successor is already explored
                frontier.append((successor, successor_path))# COMMENT: Add the successor to the frontier
    return None

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    @dataclass()
    class Node:
        state: S
        path: list
        cost: int
        def __lt__(self, other):
            return self.cost < other.cost
        def __eq__(self, other):
            return self.state == other.state

    
    frontier = PriorityQueue()# COMMENT: This is a priority queue
    explored = set()
    initial_node = Node(initial_state, [], 0)
    frontier.put(initial_node)# COMMENT: The path should be taken into consideration along with the cost (The cost is the priority of the state item)
    while frontier:
        node = frontier.get()# COMMENT: The state item is popped according to the priority
        state, path, cost = node.state, node.path, node.cost
        if problem.is_goal(state):# COMMENT: Check if the state is the goal state (when it is popped from the frontier)
            return path
        explored.add(state)
        for action in problem.get_actions(state):# COMMENT: Get all the actions that can be taken from the current state
            successor = problem.get_successor(state, action)# COMMENT: Apply the action to the current state to get the successor
            successor_path = path + [action]# COMMENT: Callculate the comulative path to the successor
            successor_cost = cost + problem.get_cost(state, action)# COMMENT: Callculate the comulative cost to the successor
            successor_node = Node(successor, successor_path, successor_cost)
            existing_node = PopFromQueue(frontier, successor_node)# COMMENT: Check if the successor is already in the frontier
            if existing_node is not None:
                successor_node = min(successor_node, existing_node)# COMMENT: Check if the successor cost is less than the cost of the state that is already in the frontier
            if successor not in explored:# COMMENT: Check if the successor is already explored
                frontier.put(successor_node)# COMMENT: Add the successor (the one that has lowest path cost{if it is already in the frontier}) to the frontier
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    frontier = PriorityQueue()# COMMENT: This is a priority queue
    explored = set()
    frontier.put((0, (0, initial_state, [])))# COMMENT: The path should be taken into consideration along with the path cost and total cost (heuristic + path cost) (The total cost is the priority of the state item)
    while frontier:
        _, (path_cost, state, path) = frontier.get()# COMMENT: The state item is popped according to the priority
        if problem.is_goal(state):# COMMENT: Check if the state is the goal state (when it is popped from the frontier)
            return path
        explored.add(state)
        for action in problem.get_actions(state):# COMMENT: Get all the actions that can be taken from the current state
            successor = problem.get_successor(state, action)# COMMENT: Apply the action to the current state to get the successor
            successor_path = path + [action]# COMMENT: Callculate the comulative path to the successor
            successor_path_cost = path_cost + problem.get_cost(state, action)# COMMENT: Callculate the comulative path cost to the successor (using the path cost of the current state)
            successor_cost = heuristic(problem, successor) + successor_path_cost# COMMENT: Callculate the total cost of the successor (using the path cost of the current state and the heuristic of the successor)
            old_item = PopFromQueue(frontier, successor)# COMMENT: Check if the successor is already in the frontier and get it if it is
            if old_item is not None:# COMMENT: Check if the successor is already in the frontier
                old_cost, (_, _, old_path) = old_item# COMMENT: Get the old total cost and path of the successor
                if successor_cost > old_cost:# COMMENT: Check if the successor total cost is less than the total cost of the state that is already in the frontier
                    successor_cost = old_cost
                    successor_path = old_path
            if successor not in explored:# COMMENT: Check if the successor is already explored
                frontier.put((successor_cost, (successor_path_cost, successor, successor_path)))# COMMENT: Add the successor (the one that has lowest total cost{if it is already in the frontier}) to the frontier
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    frontier = PriorityQueue()# COMMENT: This is a priority queue
    explored = set()
    frontier.put((0, (initial_state, [])))# COMMENT: The path should be taken into consideration along with the cost (heuristic)
    while frontier:
        _, (state, path) = frontier.get()# COMMENT: The state item is popped according to the priority
        if problem.is_goal(state):# COMMENT: Check if the state is the goal state (when it is popped from the frontier)
            return path
        explored.add(state)
        for action in problem.get_actions(state):# COMMENT: Get all the actions that can be taken from the current state
            successor = problem.get_successor(state, action)# COMMENT: Apply the action to the current state to get the successor
            successor_path = path + [action]# COMMENT: Callculate the comulative path to the successor
            successor_cost = heuristic(problem, successor)# COMMENT: Callculate the cost of the successor using the heuristic of the successor (note that we don't use the cost of the parent state{not comulative})
            if state not in explored:# COMMENT: Check if the state is already explored
                frontier.put((successor_cost, (successor, successor_path)))# COMMENT: Add the successor to the frontier
    return None
