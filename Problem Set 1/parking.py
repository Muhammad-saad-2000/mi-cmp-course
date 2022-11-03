from typing import Any, Dict, Set, Tuple, List
from problem import Problem
from mathutils import Direction, Point
from helpers import utils

# COMMENT: I chose point because the car locations are Points and the state is just the location of cars:)
ParkingState = Tuple[Point]
# An action of the parking problem is a tuple containing an index 'i' and a direction 'd' where car 'i' should move in the direction 'd'.
ParkingAction = Tuple[int, Direction]

# This is the implementation of the parking problem
class ParkingProblem(Problem[ParkingState, ParkingAction]):
    passages: Set[Point]    # A set of points which indicate where a car can be (in other words, every position except walls).
    cars: Tuple[Point]      # A tuple of points where state[i] is the position of car 'i'. 
    slots: Dict[Point, int] # A dictionary which indicate the index of the parking slot (if it is 'i' then it is the lot of car 'i') for every position.
                            # if a position does not contain a parking slot, it will not be in this dictionary.
    width: int              # The width of the parking lot.
    height: int             # The height of the parking lot.

    # This function should return the initial state
    def get_initial_state(self) -> ParkingState:
        # COMMENT: The cars locations are the things the diffrentiate the states
        return self.cars
    
    # This function should return True if the given state is a goal. Otherwise, it should return False.
    def is_goal(self, state: ParkingState) -> bool:
        # COMMENT: The goal is when all the cars are in their parking slots
        for car_index, _ in enumerate(state):
            if not(state[car_index]in self.slots) or self.slots[state[car_index]] != car_index:
                return False
        return True
    
    # This function returns a list of all the possible actions that can be applied to the given state
    def get_actions(self, state: ParkingState) -> List[ParkingAction]:
        #COMMENT: Loop over all the cars and test all the directions and return the valid ones (empty location that has no walls and is not another car)
        possible_actions = []
        for car_index, car_location in enumerate(state):
            for direction in Direction:
                new_car_location = car_location + direction.to_vector()
                if new_car_location in self.passages and new_car_location not in state:
                    possible_actions.append((car_index, direction))
        return possible_actions
    
    # This function returns a new state which is the result of applying the given action to the given state
    def get_successor(self, state: ParkingState, action: ParkingAction) -> ParkingState:
        # COMMENT: Move the car in the action in the direction of the action
        successor = []
        for car_index, car_location in enumerate(state):
            if car_index == action[0]:
                successor.append(car_location + action[1].to_vector())
            else:
                successor.append(car_location)
        return tuple(successor)
    
    # This function returns the cost of applying the given action to the given state
    def get_cost(self, state: ParkingState, action: ParkingAction) -> float:
        # COMMENT: The cost is 1 for every move and if the car moves to another car's parking slot it is 100
        cost = 1
        car_index, direction = action
        car_location = state[car_index]
        new_car_location = car_location + direction.to_vector()
        if new_car_location in self.slots and self.slots[new_car_location] != car_index:
            cost += 100
        return cost

    
    # Read a parking problem from text containing a grid of tiles
    @staticmethod
    def from_text(text: str) -> 'ParkingProblem':
        passages =  set()
        cars, slots = {}, {}
        lines = [line for line in (line.strip() for line in text.splitlines()) if line]
        width, height = max(len(line) for line in lines), len(lines)
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char != "#":
                    passages.add(Point(x, y))
                    if char == '.':
                        pass
                    elif char in "ABCDEFGHIJ":
                        cars[ord(char) - ord('A')] = Point(x, y)
                    elif char in "0123456789":
                        slots[int(char)] = Point(x, y)
        problem = ParkingProblem()
        problem.passages = passages
        problem.cars = tuple(cars[i] for i in range(len(cars)))
        problem.slots = {position:index for index, position in slots.items()}
        problem.width = width
        problem.height = height
        return problem

    # Read a parking problem from file containing a grid of tiles
    @staticmethod
    def from_file(path: str) -> 'ParkingProblem':
        with open(path, 'r') as f:
            return ParkingProblem.from_text(f.read())
    
