from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers import utils

from queue import PriorityQueue
from dataclasses import dataclass


# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    @dataclass()
    class Node:
        state: S
        path: list
        def __eq__(self, other):
            return self.state == other.state
    
    frontier = deque()
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
                if problem.is_goal(successor):
                    return successor_path
                frontier.append(successor_node)
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    @dataclass()
    class Node:
        state: S
        path: list
        def __eq__(self, other):
            return self.state == other.state
    
    frontier = deque()
    explored = set()
    initial_node = Node(initial_state, [])
    frontier.append(initial_node)
    while frontier:
        node = frontier.pop()
        state, path = node.state, node.path
        if state not in explored and problem.is_goal(state):
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
    @dataclass()
    class Node:
        state: S
        path: list
        cost: int
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):
            return self.state == other.state
    order = 0
    frontier = PriorityQueue()
    explored = set()
    initial_node = Node(initial_state, [], 0)
    frontier.put(initial_node)
    while frontier.queue:
        node = frontier.get()
        state, path, cost = node.state, node.path, node.cost
        if problem.is_goal(state):
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
                if successor_node < existing_node:
                    frontier.queue[index] = successor_node
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    @dataclass()
    class Node:
        state: S
        path: list
        path_cost: int
        cost: int
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):
            return self.state == other.state

    frontier = PriorityQueue()
    explored = set()
    initial_node = Node(initial_state, [], 0, 0)
    frontier.put(initial_node)
    order = 0
    while frontier.queue:
        node = frontier.get()
        state, path, path_cost = node.state, node.path, node.path_cost
        if problem.is_goal(state):
            return path
        explored.add(state)
        for action in problem.get_actions(state):
            successor = problem.get_successor(state, action)
            successor_path = path + [action]
            successor_path_cost = path_cost + problem.get_cost(state, action)
            successor_cost = heuristic(problem, successor) + successor_path_cost
            successor_node = Node(successor, successor_path, successor_path_cost, successor_cost)
            successor_node.order = order
            order += 1
            if successor_node not in frontier.queue and successor not in explored:
                frontier.put(successor_node)
            elif successor_node in frontier.queue:
                index = frontier.queue.index(successor_node)
                existing_node = frontier.queue[index]
                if successor_node < existing_node:
                    frontier.queue[index] = successor_node
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    @dataclass()
    class Node:
        state: S
        path: list
        cost: int
        order = 0
        def __gt__(self, other):
            if self.cost > other.cost:
                return True
            if self.cost == other.cost:
                return self.order > other.order
            return False
        def __eq__(self, other):#for checking if node is in frontier
            return self.state == other.state

    frontier = PriorityQueue()
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
                if successor_node < existing_node:
                    frontier.queue[index] = successor_node
    return None
