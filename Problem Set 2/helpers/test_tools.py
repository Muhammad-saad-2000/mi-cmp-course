from typing import Any, Dict, List, Optional, Tuple
from .utils import Result, fetch_recorded_calls, fetch_tracked_call_count, load_function

########################################################
##                  PART 2: CSP                     ##
########################################################

from CSP import UnaryConstraint, Assignment
from sudoku import SudokuProblem

# A Utility function to verify the type of domains in a Sudoku Problem
def check_sudoku_domains_type(domains: Dict[str, set]):
    if not isinstance(domains, dict):
        return f"Expected a dictionary, but got a {type(domains).__name__} (value: {repr(domains)})"
    wrong_keys = [(key, type(key).__name__) for key in domains.keys() if not isinstance(key, str)]
    if wrong_keys:
        return "Expected all keys to be strings, but some keys are:\n" + '\n'.join(f" - {repr(key)} (type: {ty})." for key, ty in wrong_keys)
    def check_sudoku_domain_type(domain: set):
        if not isinstance(domain, set):
            return f"Expected a set, but got a {type(domain).__name__} (value: {repr(domain)})"
        wrong_values = [(value, type(value).__name__) for value in domain if not isinstance(value, int)]
        if wrong_values:
            return "Expected all the domain members to be integers, but some members are: " + ', '.join(f"{repr(value)} (type: {ty})" for value, ty in wrong_values)
        return None
    wrong_domains = [(variable, check_sudoku_domain_type(domain)) for variable, domain in domains.items()]
    wrong_domains = [(variable, msg) for variable, msg in wrong_domains if msg is not None]
    if wrong_domains:
        return "Some domains have a type mismatch:\n" + '\n'.join(f" - For the domain of {repr(variable)}: {msg}" for variable, msg in wrong_domains)
    return None

# A Utility function to verify the type of assignments in a Sudoku Problem
def check_sudoku_solution_type(solution: Optional[Assignment]):
    if solution is None:
        return None
    if not isinstance(solution, dict):
        return f"Expected a dictionary or None, but got a {type(solution).__name__} (value: {repr(solution)})"
    wrong_keys = [(key, type(key).__name__) for key in solution.keys() if not isinstance(key, str)]
    if wrong_keys:
        return "Expected all keys to be strings, but some keys are:\n" + '\n'.join(f" - {key} (type: {ty})." for key, ty in wrong_keys)
    wrong_values = [(key, value, type(value).__name__) for key, value in solution.items() if not isinstance(value, int)]
    if wrong_values:
        return "Expected all values to be integers, but some values are:\n" + '\n'.join(f" - For {repr(key)}, tha value is {repr(value)} (type: {ty})" for key, value, ty in wrong_values)
    return None

########################################
## One Consistency Runner and Comparator

def run_one_consistency(
    function_path: str,
    problem: SudokuProblem) -> Tuple[SudokuProblem, bool]:

    one_consistency = load_function(function_path)
    ok = one_consistency(problem)

    return problem, ok

def compare_one_consistency(
    output: Tuple[SudokuProblem, bool],
    expected_ok: bool,
    expected_domains: Dict[str, set]) -> Result:

    problem, ok = output
    domains = problem.domains
    failure_message = None
    nl = '\n'

    if not isinstance(ok, bool):
        failure_message = f"Incorrect Function Output Type - Expected: bool, Got: {type(ok).__name__} (value: {repr(ok)})"
    elif ok != expected_ok:
        failure_message = f"Expected Function Output: {repr(expected_ok)}, Got: {repr(ok)}"
    elif ok:
        failure_message = check_sudoku_domains_type(domains)
        if failure_message is not None:
            failure_message = "Incorrect Domains Type:" + failure_message
        elif expected_domains != domains:
            failure_message = "Domain Mismatch\n"
            for variable in {*domains.keys(), *expected_domains.keys()}:
                expected_domain = expected_domains.get(variable, "No Domain")
                domain = domains.get(variable, "No Domain")
                if expected_domain != domain:
                    failure_message += f" - For the variable {variable}, Expected: {expected_domain}, Got: {domain}{nl}"
    elif ok and any(isinstance(constraint, UnaryConstraint) for constraint in problem.constraints):
        failure_message = "The problem still contains some Unary Constraints."
    
    if failure_message is not None:
        message = "For the puzzle:\n" + problem.format_assignment({}) + "\n"
        message += failure_message
        return Result(False, 0, message)

    return Result(True, 1, "")

##########################################
## Forward Checking Runner and Comparator

def run_forward_checking(
    function_path: str,
    problem: SudokuProblem,
    assignments: List[Tuple[str, Any]]) -> List[Tuple[str, Any, bool, Dict[str, set]]]:

    load_function("CSP_solver.one_consistency")(problem) # Run 1-Consistency first to eliminate unary constraints.

    forward_checking = load_function(function_path)

    domains = problem.domains
    results = []

    for assigned_variable, assigned_value in assignments:
        domains = {variable:domain.copy() for variable, domain in domains.items() if variable != assigned_variable}
        ok = forward_checking(problem, assigned_variable, assigned_value, domains)
        results.append((assigned_variable, assigned_value, ok, domains))

    return results

def compare_forward_checking_results(
    output: List[Tuple[str, Any, bool, Dict[str, set]]],
    problem: SudokuProblem,
    *expected: Tuple[bool, Dict[str, set]]) -> Result:

    assignment = {}
    nl = '\n'
    format_domains = lambda ds: nl.join(f' - {var}: {d}' for var, d in ds.items())

    previous_domains = problem.domains

    for (assigned_variable, assigned_value, ok, domains), (expected_ok, expected_domains) in zip(output, expected):

        failure_message = None
        if not isinstance(ok, bool):
            failure_message = f"Incorrect Function Output Type - Expected: bool, Got: {type(ok).__name__} (value: {repr(ok)})"
        elif ok != expected_ok:
            failure_message = f"Expected Function Output: {repr(expected_ok)}, Got: {repr(ok)}"
        elif ok:
            failure_message = check_sudoku_domains_type(domains)
            if failure_message is not None:
                failure_message = "Incorrect Domains Type:" + failure_message
            elif domains != expected_domains:
                failure_message = "Domain Mismatch\n"
                for variable in {*domains.keys(), *expected_domains.keys()}:
                    expected_domain = expected_domains.get(variable, "No Domain")
                    domain = domains.get(variable, "No Domain")
                    if expected_domain != domain:
                        failure_message += f" - For the variable {variable}, Expected: {expected_domain}, Got: {domain}{nl}"
        
        if failure_message is not None:
            message = "For the puzzle:\n" + problem.format_assignment(assignment) + "\n"
            message += f"While assigning the variable {assigned_variable} the value {assigned_value},{nl}"
            message += "Given the domains:\n" + format_domains(previous_domains) + "\n"
            message += failure_message
            return Result(False, 0, message)
        
        previous_domains = expected_domains
        assignment[assigned_variable] = assigned_value
    
    return Result(True, 1, "")

#################################################
## Least Restraining Values Runner and Comparator

def run_least_restraining_values(
    function_path: str,
    problem: SudokuProblem,
    variable_to_assign: str) -> Tuple[str, List[Any]]:

    load_function("CSP_solver.one_consistency")(problem) # Run 1-Consistency first to eliminate unary constraints.

    least_restraining_values = load_function(function_path)
    return variable_to_assign, least_restraining_values(problem, variable_to_assign, problem.domains)

def compare_least_restraining_values(
    output: Tuple[str, List[Any]],
    problem: SudokuProblem,
    expected: List[Any]) -> Result:

    variable_to_assign, output = output

    failure_message = None
    if not isinstance(output, list):
        failure_message = f"Incorrect Function Output Type - Expected: List, Got: {type(output).__name__} (value: {repr(output)})"
    elif not all(isinstance(value, int) for value in output):
        failure_message = f"Expected all the values to be integers, but got: " + ', '.join(f"{repr(value)} (type: {type(value).__name__})" for value in output if not isinstance(value, int))
    elif output != expected:
        failure_message = f"Expected: {repr(expected)}, Got: {repr(output)}"

    if failure_message is not None:
        nl = '\n'
        message = "For the puzzle:\n" + problem.format_assignment({}) + "\n"
        message += f"While ordering the values for the variable {variable_to_assign} using the 'Least Restraining Value' heursitic.{nl}"
        message += failure_message
        return Result(False, 0, message)

    return Result(True, 1, "")

#################################################
## Minimum Remaining Values Runner and Comparator

def run_minimum_remaining_values(
    function_path: str,
    problem: SudokuProblem) -> str:

    load_function("CSP_solver.one_consistency")(problem) # Run 1-Consistency first to eliminate unary constraints.

    minimum_remaining_values = load_function(function_path)
    return minimum_remaining_values(problem, problem.domains)

def compare_minimum_remaining_values(
    output: str,
    problem: SudokuProblem,
    expected: str) -> Result:

    failure_message = None
    if not isinstance(output, str):
        failure_message = f"Incorrect Function Output Type: Expected str, got {type(output).__name__} (value: {repr(output)})"
    if output != expected:
        failure_message = f"Expected: {repr(expected)}, Got: {repr(output)}"

    if failure_message is not None:
        nl = '\n'
        message = "For the puzzle:\n" + problem.format_assignment({}) + "\n"
        message += failure_message
        return Result(False, 0, message)

    return Result(True, 1, "")

###############################################
## Backtracking CSP Solve Runner and Comparator

def run_csp_solve(
    function_path: str,
    problem: SudokuProblem) -> Tuple[int, Optional[Assignment]]:
    
    fetch_tracked_call_count(SudokuProblem.is_complete) # Clear the recorded calls

    solve = load_function(function_path)
    solution = solve(problem)

    # get the count of nodes that have been explored by the search function
    explored = fetch_tracked_call_count(SudokuProblem.is_complete)

    return explored, solution

def compare_csp_solve(
    output: Tuple[int, Optional[Assignment]],
    problem: SudokuProblem,
    possible_outputs: List[Tuple[int, Optional[Assignment]]]) -> Result:

    # Check if the result matches any of the expected solutions
    explored, solution = output
    failure_message = check_sudoku_solution_type(solution)
    if failure_message is not None:
        return Result(False, 0, "Incorrect Function Output Type: " + failure_message)
    for expected_explored, expected_solution in possible_outputs:
        if explored == expected_explored and solution == expected_solution:
            return Result(True, 1, f"Explored {explored} nodes")
    
    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    format_solution = lambda s: ("No Solution" if s is None else "\n" + problem.format_assignment(s))
    expected = '\nor\n'.join(f'- Result: {format_solution(expected_solution)}{nl}- Explored {expected_explored} nodes' for expected_explored, expected_solution in possible_outputs)
    message = f"Puzzle:{nl}{problem.format_assignment({})}{nl}Expected:{nl}{repr(expected)}{nl}Got:{nl}- Result: {format_solution(solution)}{nl}- Explored {explored} nodes"
    return Result(False, 0, message)

########################################################
##                  PART 2: Games                     ##
########################################################

from tree import TreeGame, TreeNode, tree_heuristic
from dungeon import DungeonGame, Direction, dungeon_heuristic
from .pruned_tree import pruned_tree_string

# Checks if two floating point numbers are almost equal
def approx_eq(output, expected):
    return abs(output - expected)/(abs(output) + abs(expected)) < 1e-8

# Runs a testcase on a tree game 
def run_search_for_tree(
    function_path: str, 
    game: TreeGame) -> Tuple[List[str], List[str]]:

    fetch_recorded_calls(TreeGame.is_terminal) # Clear the recorded calls

    search_fn = load_function(function_path) # Load the search function
    
    initial_state = game.get_initial_state() # Get the initial state
    # Search without a depth limit
    value, action = search_fn(game, initial_state, tree_heuristic, -1)
    
    # get a list of nodes that have been explored by the search function
    explored = [call["args"][1] for call in fetch_recorded_calls(TreeGame.is_terminal)]
    
    return value, action, [node.name for node in explored]

# Compare a testcase result with the expected output on a tree game
def compare_search_results_for_tree(
    output: Tuple[float, str, List[str]],
    possible_outputs: List[Tuple[float, str, List[str]]],
    tree_path: str) -> Result:

    # Check if the result is one of the expected values
    # If yes, return a success result
    value, action, explored = output
    for expected_value, expected_action, expected_explored in possible_outputs:
        if approx_eq(value, expected_value) and action == expected_action and explored == expected_explored:
            return Result(True, 1, "")
    
    tree = TreeNode.from_file(tree_path) # Read the tree from a file to display in the failure message
    
    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    list_to_str = lambda l: repr(l) + "\n" + pruned_tree_string(tree, l) #
    out_to_str = lambda o: f'- Value: {o[0]} / Action: {o[1]} {nl}- Explored {len(o[2])} Nodes: {list_to_str(o[2])}'
    expected = '\nor\n'.join(out_to_str(expected) for expected in possible_outputs)
    message = f"Tree:{nl}{tree}{nl}Expected:{nl}{expected}{nl}Got:{nl}{out_to_str(output)}"
    
    return Result(False, 0, message)

# Runs a testcase on a dungeon game
def run_search_for_dungeon(
    function_path: str, 
    game: DungeonGame,
    max_search_depth: int) -> Tuple[float, Direction, int]:

    fetch_tracked_call_count(DungeonGame.is_terminal) # Clear the recorded calls
    
    search_fn = load_function(function_path) # Load the search function
    
    initial_state = game.get_initial_state() # Get the initial state
    # Search with the specified depth limit
    value, action = search_fn(game, initial_state, dungeon_heuristic, max_search_depth)
    
    # get the count of nodes that have been explored by the search function
    explored = fetch_tracked_call_count(DungeonGame.is_terminal)

    return value, action, explored

# Compare a testcase result with the expected output on a dungeon game
def compare_search_results_for_dungeon(
    output: Tuple[float, Direction, int],
    possible_outputs: List[Tuple[float, Direction, int]],
    level_path: str) -> Result:
    
    # Check if the result is one of the expected values
    # If yes, return a success result
    value, action, explored = output
    for expected_value, expected_action, expected_explored in possible_outputs:
        if approx_eq(value, expected_value) and action == expected_action and explored == expected_explored:
            return Result(True, 1, f"Explored {explored} nodes")
    
    # Since it is not a success, create and return a failure result with a failure message
    nl = '\n'
    expected = '\nor\n'.join(f'- Value: {value} / Action: {str(action)}{nl}- Explored {explored} nodes' for value, action, explored in possible_outputs)
    level = open(level_path, 'r').read()
    message = f"Level:{nl}{level}{nl}Expected:{nl}{expected}{nl}Got:{nl}- Value: {output[0]} / Action: {str(output[1])}{nl}- Explored {output[2]} nodes"
    return Result(False, 0, message)