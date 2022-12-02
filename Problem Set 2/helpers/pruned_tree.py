from typing import List, Set
from tree import *

def _recursive_pruned_str(node: TreeNode, is_root: bool, explored: Set[str]) -> List[str]:
    name = node.name
    if not is_root:
        _, name = name.rsplit("/", 1)
    if node.name not in explored:
        name = "[PRUNED]" + name
    if node.children is None:
        return [f'{name}: {node.value}']
    else:
        prepads = [PREPAD_MIDDLE] * len(node.children)
        if len(prepads) == 1:
            prepads[0] = PREPAD_ONE
        else:
            prepads[0] = PREPAD_FIRST
            prepads[-1] = PREPAD_LAST
        lines = [line for prepad, child in zip(prepads, node.children.values()) for line in prepad(_recursive_pruned_str(child, False, explored))]
        return prepad(lines, name, ' '*len(name))

# This function draws a tree and marks pruned nodes with the "[PRUNED]" tag
def pruned_tree_string(node: TreeNode, explored) -> str:
    return '\n'.join(_recursive_pruned_str(node, True, set(explored)))