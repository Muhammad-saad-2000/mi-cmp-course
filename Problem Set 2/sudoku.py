from typing import Dict
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

# A class for the sudoku problem which inherits from the generic CSP problem class
class SudokuProblem(Problem):
    size: int   # The size of the sudoku puzzle (usually, it is 9). This is needed for printing only.
    clues: Dict[str, int]   # A dictionary of the clues (the fixed values that are already defined in the puzzle). This is needed for printing only.

    # Convert an assignment into a string (so that is can be printed or saved).
    def format_assignment(self, assignment: Assignment) -> str:
        cell_dim = int(self.size ** 0.5)
        group_elements = lambda l, size: zip(*[l[i::size] for i in range(size)])
        separator = ' + '.join([' '.join(['-']*cell_dim)]*cell_dim)
        separator = '\n' + separator + '\n'
        values = {**assignment, **self.clues}
        lines = [[str(values.get(str((r,c))) or '.') for c in range(self.size)] for r in range(self.size)]
        lines = [' | '.join(' '.join(group) for group in group_elements(line, cell_dim)) for line in lines]
        return separator.join('\n'.join(group) for group in group_elements(lines, cell_dim))

    # Read a sudoku puzzle from a string
    @staticmethod
    def from_text(text: str) -> 'SudokuProblem':
        not_equal_condition = lambda a, b: a != b
        unary_not_equal_condition = lambda f: (lambda v: v != f)
        
        lines = [line.strip() for line in text.splitlines()]
        lines = [line.replace('| ', '').split() for line in lines if len(line) != 0 and not line.startswith('-')]
        size = len(lines)
        cell_dim = int(size ** 0.5)
        
        domain = set(range(1, size+1))
        variables = []

        vars_in_rows = [[] for _ in range(size)]
        vars_in_cols = [[] for _ in range(size)]
        vars_in_sqrs = [[] for _ in range(size)]

        fixed_values = {}

        fixed_in_rows = [[] for _ in range(size)]
        fixed_in_cols = [[] for _ in range(size)]
        fixed_in_sqrs = [[] for _ in range(size)]

        for r, line in enumerate(lines):
            for c, cell in enumerate(line):
                s = (r//cell_dim) * cell_dim + (c//cell_dim)
                if cell == '.':
                    variable = str((r, c))
                    variables.append(variable)
                    vars_in_rows[r].append(variable)
                    vars_in_cols[c].append(variable)
                    vars_in_sqrs[s].append(variable)
                else:
                    value = int(cell)
                    fixed_in_rows[r].append(value)
                    fixed_in_cols[c].append(value)
                    fixed_in_sqrs[s].append(value)
                    fixed_values[str((r, c))] = value
        
        constraints = []

        var_fixed_pairs = [
            (vars_in_rows, fixed_in_rows),
            (vars_in_cols, fixed_in_cols),
            (vars_in_sqrs, fixed_in_sqrs)
        ]

        for pair in var_fixed_pairs:
            for var_list, fixed_list in zip(*pair):
                for index, variable in enumerate(var_list):
                   constraints.extend(UnaryConstraint(variable, unary_not_equal_condition(fixed)) for fixed in fixed_list)
                   constraints.extend(BinaryConstraint((variable, other), not_equal_condition) for other in var_list[index+1:])
        
        problem = SudokuProblem()
        problem.size = size
        problem.clues = fixed_values
        problem.variables = variables
        problem.domains = {variable:domain.copy() for variable in variables}
        problem.constraints = constraints
        
        return problem

    # Read a sudoku puzzle from a file
    @staticmethod
    def from_file(path: str) -> "SudokuProblem":
        with open(path, 'r') as f:
            return SudokuProblem.from_text(f.read())