from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from dataclasses import dataclass
from game import Game
import json

from helpers.utils import record_calls

# Some helper constants and functions to draw the tree node
BRANCH_DOWN = "\u252c\u2500"
CONTINUE_DOWN = "\u2502 "
BRANCH_END = "\u2514\u2500"
BRANCH_BOTH = "\u251c\u2500"
HORIZONTAL = "\u2500\u2500"
EMPTY = "  "

def prepad(l: List[str], s1: str, s2: str) -> List[str]:
    return [s1+l[0], *(s2+i for i in l[1:])] if l else l

PREPAD_FIRST  = lambda l: prepad(l, BRANCH_DOWN, CONTINUE_DOWN)
PREPAD_ONE    = lambda l: prepad(l, HORIZONTAL, EMPTY)
PREPAD_MIDDLE = lambda l: prepad(l, BRANCH_BOTH, CONTINUE_DOWN)
PREPAD_LAST   = lambda l: prepad(l, BRANCH_END, EMPTY)

# A tree node class that store the node name and the following:
# If the node is nonterminal, the children are stored in "children"
# If the node is terminal, its value is stored in "value" while "children" will contain None
@dataclass
class TreeNode:
    name: str
    children: Optional[Dict[str, 'TreeNode']]
    value: float

    # a private method used for drawing the tree
    def __recursive_str(self, is_root: bool):
        name = self.name
        if not is_root:
            _, name = name.rsplit("/", 1)
        if self.children is None:
            return [f'{name}: {self.value}']
        else:
            prepads = [PREPAD_MIDDLE] * len(self.children)
            if len(prepads) == 1:
                prepads[0] = PREPAD_ONE
            else:
                prepads[0] = PREPAD_FIRST
                prepads[-1] = PREPAD_LAST
            lines = [line for prepad, child in zip(prepads, self.children.values()) for line in prepad(child.__recursive_str(False))]
            return prepad(lines, name, ' '*len(name))
    
    # draw a tree as a string
    def __str__(self) -> str:
        return '\n'.join(self.__recursive_str(True))
    
    # read a tree from a file
    @staticmethod
    def from_file(path: str) -> 'TreeNode':
        problem_def: Dict = json.load(open(path, 'r'))
        def convert(tree: Union[float, Dict[str, Any]], name: str) -> TreeNode:
            if isinstance(tree, dict):
                return TreeNode(name, {key:convert(child, f'{name}/{key}') for key, child in tree.items()}, 0)
            else:
                return TreeNode(name, None, tree)
        root = convert(problem_def, 'root')
        return root

# This is the implementation of a game played on a game tree
class TreeGame(Game[List, str]):
    
    __root: TreeNode    # the root of the game tree
    
    def __init__(self, root: TreeNode) -> None:
        super().__init__()
        self.__root = root
    
    # This function returns the initial state
    def get_initial_state(self) -> TreeNode:
        return self.__root

    # how many agents are playing this game
    # For this game, there are 2 agents
    @property
    def agent_count(self) -> int:
        return 2

    # This function checks whether the given state is terminal or not
    # if it is a terminal state, the second return value will be a list of terminal values for all agents
    # if it is not a terminal state, the second return value will be None
    @record_calls
    def is_terminal(self, state: TreeNode) -> Tuple[bool, Optional[List[float]]]:
        if state.children is None:
            return True, [state.value, -state.value]
        else:
            return False, None

    # This function returns the index of the agent whose turn in now
    def get_turn(self, state: TreeNode) -> int:
        return state.name.count('/') % 2

    # This function returns all the possible actions from the given state
    def get_actions(self, state: TreeNode) -> Iterable[int]:
        if state.children is None:
            return []
        return list(state.children.keys())

    # Given a state and an action, this function returns the next state 
    def get_successor(self, state: TreeNode, action: str) -> TreeNode:
        return state.children[action]
    
    # create a tree game from a path to a tree file
    @staticmethod
    def from_file(path: str) -> 'TreeGame':
        return TreeGame(TreeNode.from_file(path))

# This heuristic is unrealistic but so is the tree game (we rarely have the whole game tree stored in memory)
# We will use it for the ordering in Alpha Beta with Move Ordering
def tree_heuristic(game: TreeGame, state: TreeNode, agent: int):
    def recursive_sum(state: TreeNode):
        if state.children is None:
            return state.value
        else:
            return sum(recursive_sum(child) for child in state.children.values())/len(state.children)
    value = recursive_sum(state)
    if agent != 0: value = -value
    return value