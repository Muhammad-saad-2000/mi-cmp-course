from sudoku import SudokuProblem
from CSP_solver import solve
import argparse, time

# This function requests a solution from the user
def solve_via_human(problem: SudokuProblem):
    assignment = {}
    
    help = """Valid commands are:
    \t- quit (or q for short) to end the game and return the current assignment.
    \t- (r,c)=v to assign the value v to the cell in row r and column c. r & c are 0-indexed."""

    while True:
        print(problem.format_assignment(assignment))
        command = input("Please enter a command: ").strip().lower()

        if command in {"q", "quit", "exit", "ok", "done", "finish"}:
            break

        if '=' not in command:
            print(f"Unknown Command. {help}")
            continue

        variable, value = command.rsplit('=', 1)
        variable = str(eval(variable))
        value = eval(value)

        if variable not in problem.variables:
            print(f"Unknown variable. Valid variables are: {problem.variables}")
            continue
        if value not in problem.domains[variable]:
            print(f"Invalid value. The domain of the variable {variable} is {problem.domains[variable]}")
            continue

        assignment[variable] = value
        
        if problem.check_solution(assignment):
            print("Congratulations! This Assignment is a solution. If you don't want to make any further changes, you can quit by entering quit or q.")
        elif problem.is_complete(assignment):
            print("This assignment is complete, but it does not satisfy some constraints. Please re-assign some variables to satisfy the constraints.")
    
    return assignment

def main(args: argparse.Namespace):
    start = time.time() # Track run time

    problem = SudokuProblem.from_file(args.puzzle)
    
    agent_name = args.agent.lower()
    if agent_name == "human":
        solve_fn = solve_via_human
    elif agent_name == "backtrack":
        solve_fn = solve
    else:
        print(f"Unknown Agent: {agent_name}. Please select a valid agent.")
        return

    result = solve_fn(problem)

    print("The Result:")
    if result is None:
        print("No solution was found")
    else:
        print(problem.format_assignment(result))
        if problem.is_complete(result):
            if problem.satisfies_constraints(result):
                print("The result is a correct solution.")
            else:
                print("The result is a complete assignment, but it does not satisfy all the constraints.")
        else:
            print("The result is an incomplete assignment.")
    
    # Finally print the elapsed time for the whole process
    print(f"Done in {time.time() - start} seconds")

if __name__ == "__main__":
    # Read the arguments from the command line
    parser = argparse.ArgumentParser(description="Play Sudoku as Human or AI")
    parser.add_argument("puzzle", help="path to the puzzle to play")
    parser.add_argument("--agent", "-a", default="human",
                        choices=['human', 'backtrack'],
                        help="the agent that will play the game")
    
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("Goodbye!!")