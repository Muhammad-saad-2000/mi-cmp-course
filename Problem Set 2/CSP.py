from typing import Callable, Dict, List, Any, Tuple
from helpers.utils import track_call_count

# This is the type definition for an Assignment
# Basically, an assignment is a dictionary where each key-value pair represents a variable and its assigned value respectively.
# If a variable is missing from an assignment, then its is still unassigned.
Assignment = Dict[str, Any]

# The is the base class for all the constraints
# The only function defined in a constraint is "is_satisfied" that checks if an assignment satisfies this constraint.
class Constraint:
    # Given an assignment, this function returns True if it satisfies the constraint, and False otherwise.
    def is_satisfied(self, assignment: Assignment) -> bool:
        return False

# This is a class for unary constraints (constraints involving one variable only).
class UnaryConstraint(Constraint):
    variable: str  # The name of the variable that is in the constraint.
    condition: Callable[[Any], bool] # A function that takes the variable's value and returns whether it satisfies the constraint or not.

    def __init__(self, variable: str, condition: Callable[[Any], bool]) -> None:
        super().__init__()
        self.variable = variable
        self.condition = condition

    # This function looks for the variable in the assignment and checks if it satisfies the constraint.
    # If the variable is unassigned, the assignment does not satisfy the condition.
    # Important: If the value of a variable in the assignment is None, then it is assumed as if it is unassigned.
    def is_satisfied(self, assignment: Assignment) -> bool:
        value = assignment.get(self.variable)
        if value is None: return False
        return self.condition(value)

# This is a class for binary constraints (constraints involving two variable only).
class BinaryConstraint(Constraint):
    variables: Tuple[str, str]  # The name of the two variables that are in the constraint.
    condition: Callable[[Any, Any], bool] # A function that takes the variables' values and returns whether they satisfies the constraint or not.

    def __init__(self, variables: Tuple[str, str], condition: Callable[[Any, Any], bool]) -> None:
        super().__init__()
        self.variables = variables
        self.condition = condition
    
    # This function looks for the variables in the assignment and checks if they satisfy the constraint.
    # If any of the variables are unassigned, the assignment does not satisfy the condition.
    # Important: If the value of a variable in the assignment is None, then it is assumed as if it is unassigned.
    def is_satisfied(self, assignment: Assignment) -> bool:
        variable1, variable2 = self.variables
        value1, value2 = assignment.get(variable1), assignment.get(variable2)
        if value1 is None or value2 is None: return False
        return self.condition(value1, value2)
    
    # Given the name of a variable in the constraint, this function returns the other variable.
    # For example, if the constraint contains the variables A & B, this function will return A if given B, and will return B if given A.
    # Important: This function only works correctly if the given variable is in the constraint.
    def get_other(self, variable: str) -> str:
        variable1, variable2 = self.variables
        return variable2 if variable == variable1 else variable1

# This defines a generic CSP problem
class Problem:
    variables: List[str]            # A list of the variable names in the problem
    domains: Dict[str, set]         # A dictionary containing the domain of each variable.
                                    # The domain is a set of values that the variable can take. 
    constraints: List[Constraint]   # A list of constraints in the problem.

    # Returns True if the assignment is complete (all the variables has an value in the given assignment).
    @track_call_count
    def is_complete(self, assignment: Assignment) -> bool:
        return all(var in assignment for var in self.variables)
    
    # Return True if the assignment satisfies all the constraints.
    def satisfies_constraints(self, assignment: Assignment) -> bool:
        return all(constraint.is_satisfied(assignment) for constraint in self.constraints)
