from typing import Generic, TypeVar, Union

T = TypeVar('T') 
E = TypeVar('E') 

class Ok(Generic[T]):
    """Represents a successful execution path."""
    def __init__(self, value: T):
        self.value = value
    def is_ok(self) -> bool: return True
    def is_err(self) -> bool: return False

class Err(Generic[E]):
    """Represents a failed execution path containing error data."""
    def __init__(self, error: E):
        self.error = error
    def is_ok(self) -> bool: return False
    def is_err(self) -> bool: return True

# Define our unified type hint
Result = Union[Ok[T], Err[E]]