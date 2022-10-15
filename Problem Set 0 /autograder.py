import importlib
from importlib import util as ilu
import threading, _thread
import time
import json
import argparse
import os
from typing import Any, Callable, Dict, List, Tuple, Union

from globals import *
from utils import *

root = "testcases"

solution_path = ""

def load_function(name: str, use_local: bool = False) -> Callable:
    path, function = name.rsplit(".", 1)
    if solution_path and not use_local:
        spec = ilu.spec_from_file_location(path, os.path.join(solution_path, path + ".py"))
        module = ilu.module_from_spec(spec)
        spec.loader.exec_module(module)
    else:
        module = importlib.import_module(path)
    return getattr(module, function)

def get_test_cases(path: str) -> List[Dict[str, Any]]:
    test_cases = []
    for filename in os.listdir(path):
        if filename.startswith("__"): continue
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath) and os.path.splitext(filepath)[1] == ".json":
            test_cases.append(json.load(open(filepath, 'r')))
    return test_cases

def read_problems() -> Tuple[str, List[Dict[Any, str]]]:
    data = json.load(open(os.path.join(root, "problems.json")))
    return data.get("name", ""), data.get("problems", [])

def timeout_function():
    _thread.interrupt_main()

def run_test(fn: Callable, input_args: Arguments, cmp: Callable, cmp_args: Arguments, timeout: 10) -> Union[Result, None]:
    timer = threading.Timer(timeout, timeout_function)
    timer.start()
    start = time.time()
    try:
        output = fn(*input_args.args, **input_args.kwargs)
        result = cmp(output, *cmp_args.args, **cmp_args.kwargs)
    except KeyboardInterrupt as err:
        elapsed = time.time() - start
        if elapsed >= timeout:
            result = Result(False, 0, "Timeout")
        else:
            result = Result(False, 0, str(err))
    except NotImplementedError as err:
        result = None
    except BaseException as err:
        result = Result(False, 0, str(err))
    finally:
        timer.cancel()
    return result

def default_comparator(output, expected):
    success = output == expected
    grade = (1 if success else 0)
    message = ""
    if not success:
        message = f"Expected {expected} but got {output}"
    return Result(success, grade, message)

def approximate_comparator(output, expected):
    success = output == expected
    if not success:
        success = abs(output - expected)/(abs(output) + abs(expected)) < 1e-8
    grade = (1 if success else 0)
    message = ""
    if not success:
        message = f"Expected {expected} but got {output}"
    return Result(success, grade, message)

class Problem:
    def __init__(self, **kwargs) -> None:
        self.name = kwargs.get("name", "Unnamed Problem")
        self.testcases_path = kwargs.get("testcases_path", self.name)
        self.default_fn = lambda x: x
        if "function" in kwargs: 
            try: self.default_fn = load_function(kwargs["function"])
            except: pass
        self.default_cmp = default_comparator
        if "comparator" in kwargs: self.default_cmp = load_function(kwargs["comparator"], use_local=True)
        self.weight = kwargs.get("weight", 1)
        self.default_timeout = kwargs.get("timeout", 1)
        self.grade = 0
        self.maximum_grade = 0
    
    def run(self):
        print(f"Problem: {self.name}")
        test_cases = get_test_cases(os.path.join(root, self.testcases_path))
        self.grade = 0
        self.maximum_grade = 0
        for test_index, test_case in enumerate(test_cases):
            description = test_case.get("description", f"Test Case {test_index+1}")
            timeout = test_case.get("timeout", self.default_timeout)
            print(f"{test_index+1}: {description} :: time-limit = {timeout}sec")
            fn = self.default_fn
            if "function" in test_case:
                try: fn = load_function(test_case["function"])
                except: pass
            input_args = test_case.get("input_args", [])
            input_kwargs = test_case.get("input_kwargs", {})
            fn_args = Arguments(
                [eval(arg) for arg in input_args], {key:eval(value) for key, value in input_kwargs.items()})
            cmp = self.default_cmp
            if "comparator" in test_case: cmp = load_function(test_case["comparator"], use_local=True)
            cmp_args = Arguments(
                [eval(arg) for arg in test_case.get("comparison_args", [])],
                {key:eval(value) for key, value in test_case.get("comparison_kwargs", {}).items()})
            weight = test_case.get("weight", 1)
            maximum_grade = self.weight * weight * test_case.get("maximum_grade", 1)
            self.maximum_grade += maximum_grade
            result = run_test(fn, fn_args, cmp, cmp_args, timeout)
            if result is None:
                print("Function is not implemented yet")
                continue
            grade = self.weight * weight * result.grade
            if result.success:
                print(f"Result: PASS {grade}/{maximum_grade}")
            else:
                print(f"Result: FAIL {grade}/{maximum_grade} - {result.message}")
                if input_args:
                    print("Input positional arguments:")
                    for arg in input_args: print(f"- {arg}")
                if input_kwargs:
                    print(f"Input keyword arguments:")
                    for key, val in input_kwargs.items(): print(f"- {key}: {val}")
                print()
            self.grade += grade
        print(f"Total {self.grade}/{self.maximum_grade}")

def main(args: argparse.Namespace):
    global solution_path
    solution_path = args.solution
    name, problems = read_problems()
    problems = [Problem(**problem) for problem in problems]
    print(f"\n{name}\n")
    total_grade = 0
    maximum_grade = 0
    if args.question != "all":
        try:
            questions: str = args.question
            exclude = False
            if questions.startswith("~"):
                questions = questions[1:]
                exclude = True
            selected = {int(index)-1 for index in questions.split(",")}
            if exclude:
                problems = [problem for index, problem in enumerate(problems) if index not in selected]
            else:
                problems = [problem for index, problem in enumerate(problems) if index in selected]
        except:
            pass
    for problem in problems:
        problem.run()
        print()
        total_grade += problem.grade
        maximum_grade += problem.maximum_grade
    print(f"Problem Set Total {total_grade}/{maximum_grade}\n")
    exit(total_grade)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Autograder")
    parser.add_argument("--question", "-q", default="all")
    parser.add_argument("--solution", "-s", default="")
    args = parser.parse_args()
    main(args)