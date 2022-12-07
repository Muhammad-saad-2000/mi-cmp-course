from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function should apply 1-Consistency to the problem.
# In other words, it should modify the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints should be removed from the problem (they are no longer needed).
# The function should return False if any domain becomes empty. Otherwise, it should return True.
def one_consistency(problem: Problem) -> bool:
    unary_constraints = [constraint for constraint in problem.constraints if isinstance(constraint, UnaryConstraint)]
    for constraint in unary_constraints:
        variable = constraint.variable
        variable_domain = problem.domains[variable]
        values_to_remove = [value for value in variable_domain if not constraint.is_satisfied({variable: value})]
        if len(variable_domain) == len(values_to_remove):
            return False
        for value in values_to_remove: variable_domain.remove(value)
    problem.constraints = [constraint for constraint in problem.constraints if not isinstance(constraint, UnaryConstraint)]
    return True

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    binary_constraints = [constraint for constraint in problem.constraints if isinstance(constraint, BinaryConstraint)]
    for constraint in binary_constraints:
        if assigned_variable in constraint.variables:
            other_variable = constraint.get_other(assigned_variable)
            if other_variable in domains:
                values_to_remove = []
                for value in domains[other_variable]:
                    assignment = {assigned_variable: assigned_value, other_variable: value}
                    if not constraint.is_satisfied(assignment):
                        values_to_remove.append(value)
                if len(domains[other_variable]) == len(values_to_remove):
                    return False
                for value in values_to_remove:
                    domains[other_variable].remove(value)
    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    values_list=[]
    binary_constraints = [constraint for constraint in problem.constraints if isinstance(constraint, BinaryConstraint)]
    domains_copy = domains.copy()
    for value in domains_copy[variable_to_assign]:
        count = 0
        for constraint in binary_constraints:
            if variable_to_assign in constraint.variables:
                other_variable = constraint.get_other(variable_to_assign)
                if other_variable in domains_copy:
                    other_domain = domains_copy[other_variable]
                    for other_value in other_domain:
                        assignment = {variable_to_assign: value, other_variable: other_value}
                        if not constraint.is_satisfied(assignment):
                            count += 1
        values_list.append((value, count))
    values_list.sort(key=lambda x: x[0])
    values_list.sort(key=lambda x: x[1])
    return [x[0] for x in values_list]

# This function should return the variable that should be picked based on the MRV heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
# IMPORTANT: If multiple variables have the same priority given the MRV heuristic, 
#            order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    varibles_list = []
    for variable in problem.variables:
        if variable in domains:
            varibles_list.append((variable, len(domains[variable])))
    varibles_list.sort(key=lambda x: x[1])
    return varibles_list[0][0]

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    if not one_consistency(problem):
        return None
    assignment = {}
    def backtrack(assignment, domains, csp):
        if csp.is_complete(assignment):
            return assignment
        var = minimum_remaining_values(csp, domains)
        for value in least_restraining_values(csp, var, domains):
            assignment[var] = value
            domains_copy = domains.copy()
            # AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH (set inside set case)
            for set_var in domains_copy:
                domains_copy[set_var]=domains_copy[set_var].copy()
            # AHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH
            domains_copy.pop(var)
            if forward_checking(csp, var, value, domains_copy):
                result = backtrack(assignment, domains_copy, csp)
                if result is not None:
                    return result
            assignment.pop(var)
        return None
    return backtrack(assignment, problem.domains, problem)