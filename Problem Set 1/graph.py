from typing import Dict, Iterable, List
from dataclasses import dataclass
import json

from problem import Problem
from mathutils import Point, euclidean_distance
from helpers.utils import record_calls

# In the graph routing problem, the state is a graph node
# We use dataclass with frozen=True to automatically implement:
#   the constructor, the == operator, the hash function and to make the class immutable
# Now it can be added to sets and used as keys in dictionaries
# This will the node name and position 
@dataclass(frozen=True)
class GraphNode:
    name: str
    position: Point

    def __str__(self) -> str:
        return self.name

# This is the implementation of the graph routing problem
class GraphRoutingProblem(Problem[GraphNode, GraphNode]):
    def __init__(self, start: GraphNode, goal: GraphNode, adjacency: Dict[GraphNode, List[GraphNode]]) -> None:
        super().__init__()
        self.start = start
        self.goal = goal
        self.adjacency = adjacency
    
    def get_initial_state(self) -> GraphNode:
        return self.start
    
    # We use @record_calls to track the arguments with which this function is called to retrieve the traversal order
    @record_calls
    def is_goal(self, state: GraphNode) -> bool:
        return state == self.goal
    
    # The actions for this problem are the neighboring nodes we can reach from the current node
    def get_actions(self, state: GraphNode) -> Iterable[GraphNode]:
        return self.adjacency.get(state, [])
    
    # The next state and the action are the exact same thing for this problem
    def get_successor(self, state: GraphNode, action: GraphNode) -> GraphNode:
        return action
    
    # The cost of an action is the distance between the current node and the next node 
    def get_cost(self, state: GraphNode, action: GraphNode) -> float:
        return euclidean_distance(state.position, action.position)
    
    # Read a graph routing problem from file
    @staticmethod
    def from_file(path: str) -> 'GraphRoutingProblem':
        problem_def: Dict[str, Dict] = json.load(open(path, 'r'))
        graph_def: Dict[str, Dict] = problem_def.get("graph", {})
        node_dict = {name: GraphNode(name, Point(*item.get("position", [0,0]))) for name, item in graph_def.items()}
        adjacency: Dict[GraphNode, List[GraphNode]] = {}
        for name, item in graph_def.items():
            node = node_dict[name]
            adjacent = [node_dict[adjacent] for adjacent in sorted(item.get("adjacent", [])) if adjacent in node_dict]
            adjacency[node] = adjacent
        start = node_dict[problem_def.get("start", "")]
        goal = node_dict[problem_def.get("goal", "")]
        return GraphRoutingProblem(start, goal, adjacency)

def graphrouting_heuristic(problem: GraphRoutingProblem, state: GraphNode) -> float:
    return euclidean_distance(state.position, problem.goal.position)