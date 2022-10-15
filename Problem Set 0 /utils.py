
from dataclasses import dataclass
from typing import Any, Dict, List

@dataclass
class Result:
    success:     bool
    grade:       int
    message:     str

@dataclass
class Arguments:
    args:   List[Any]
    kwargs: Dict[str, Any]

def NotImplemented():
    raise NotImplementedError()