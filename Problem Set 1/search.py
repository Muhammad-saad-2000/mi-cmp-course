from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers import utils

from queue import PriorityQueue #COMMENT: For the UCS, A* and GBFS
from dataclasses import dataclass #COMMENT: For defining the nodes data type(state, path, cost)


# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    @dataclass()
    #COMMENT: Only need to keep track of the state and the path
    class Node:
        state: S
        path: list
        def __eq__(self, other):
            return self.state == other.state
    
    frontier = deque()#COMMENT: Regular queue
    explored = set()
    initial_node = Node(initial_state, [])
    if problem.is_goal(initial_state):
        return []
    frontier.append(initial_node)
    while frontier:
        node = frontier.popleft()
        state, path = node.state, node.path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_node = Node(successor, successor_path)
            if successor not in explored and successor_node not in frontier:
                if problem.is_goal(successor):#COMMENT: Check if the successor is the goal before dequeuing it
                    return successor_path
                frontier.append(successor_node)
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    @dataclass()
    #COMMENT: Only need to keep track of the state and the path
    class Node:
        state: S
        path: list
        def __eq__(self, other):
            return self.state == other.state
    
    frontier = deque()#COMMENT: Regular stack
    explored = set()
    initial_node = Node(initial_state, [])
    frontier.append(initial_node)
    while frontier:
        node = frontier.pop()
        state, path = node.state, node.path
        
        #COMMENT: the first check to make it pass the test cases that was giving problems {the ones that was later modified} (and generaly any additional check is for the same resnon)
        if state not in explored and problem.is_goal(state):#COMMENT: Check if the successor is the goal after popping it
            return path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_node = Node(successor, successor_path)
            if successor not in explored:
                frontier.append(successor_node)
    return None

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #COMMENT: Now an aditional cost is needed to keep track of the path cost, order is also needed to keep
    #track of the order of the nodes in the frontier (To pass the given cases)
    @dataclass()
    class Node:
        state: S
        path: list
        cost: int#COMMENT: Path cost
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):
            return self.state == other.state
    
    order = 0#COMMENT: To keep track of the order of the nodes entering the frontier
    frontier = PriorityQueue()#COMMENT: Priority queue based on the cost(path cost)
    explored = set()
    initial_node = Node(initial_state, [], 0)
    frontier.put(initial_node)
    while frontier.queue:
        node = frontier.get()
        state, path, cost = node.state, node.path, node.cost
        if problem.is_goal(state):#COMMENT: Check the node after getting it from the frontier
            return path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_cost = cost + problem.get_cost(state, action)
            successor_node = Node(successor, successor_path, successor_cost)
            successor_node.order = order
            order += 1
            if successor_node not in frontier.queue and successor not in explored:
                frontier.put(successor_node)
            elif successor_node in frontier.queue:
                index = frontier.queue.index(successor_node)
                existing_node = frontier.queue[index]
                if successor_node < existing_node:#COMMENT: Replace the node if the new one has a lower cost
                    frontier.queue[index] = successor_node
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #COMMENT: Now cost has two typespath cost
    @dataclass()
    class Node:
        state: S
        path: list
        path_cost: int#COMMENT: Path cost
        cost: int#COMMENT: Path cost + heuristic cost (is the one used to order the nodes in the frontier)
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):
            return self.state == other.state

    frontier = PriorityQueue()#COMMENT: Priority queue based on the cost(path cost + heuristic cost)
    explored = set()
    initial_node = Node(initial_state, [], 0, 0)
    frontier.put(initial_node)
    order = 0
    while frontier.queue:
        node = frontier.get()
        state, path, path_cost = node.state, node.path, node.path_cost
        if problem.is_goal(state):#COMMENT: Check the node after getting it from the frontier
            return path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_path_cost = path_cost + problem.get_cost(state, action)
            successor_cost = heuristic(problem, successor) + successor_path_cost#COMMENT: Total cost
            successor_node = Node(successor, successor_path, successor_path_cost, successor_cost)
            successor_node.order = order
            order += 1
            if successor_node not in frontier.queue and successor not in explored:
                frontier.put(successor_node)
            elif successor_node in frontier.queue:
                index = frontier.queue.index(successor_node)
                existing_node = frontier.queue[index]
                if successor_node < existing_node:#COMMENT: Replace the node if the new one has a lower cost
                    frontier.queue[index] = successor_node
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #COMMENT: Now cost is only one type again but it is the heuristic cost
    @dataclass()
    class Node:
        state: S
        path: list
        cost: int #COMMENT: Heuristic cost
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):
            return self.state == other.state

    frontier = PriorityQueue()#COMMENT: Priority queue based on the cost(heuristic cost)
    explored = set()
    initial_node = Node(initial_state, [], 0)
    order = 0
    frontier.put(initial_node)
    while frontier.queue:
        node = frontier.get()
        state, path = node.state, node.path
        if problem.is_goal(state):
            return path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_cost = heuristic(problem, successor)
            successor_node = Node(successor, successor_path, successor_cost)
            successor_node.order = order
            order += 1
            if successor_node not in frontier.queue and successor not in explored:
                frontier.put(successor_node)
            elif successor_node in frontier.queue:
                index = frontier.queue.index(successor_node)
                existing_node = frontier.queue[index]
                if successor_node < existing_node:#COMMENT: Replace the node if the new one has a lower cost
                    frontier.queue[index] = successor_node
    return None
