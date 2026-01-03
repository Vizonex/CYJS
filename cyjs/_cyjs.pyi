from typing import Generator

class JSError(Exception):
    """Represents Numerous Exceptions raised from CYJS"""


class MemoryUsage:
    malloc_size: int
    malloc_limit: int
    memory_used_size: int
    malloc_count: int
    memory_used_count: int
    atom_count: int
    atom_size: int
    str_count: int
    str_size: int
    obj_count: int
    obj_size: int
    prop_count: int
    prop_size: int
    shape_count: int
    shape_size: int
    js_func_count: int
    js_func_size: int
    js_func_code_size: int
    js_func_pc2line_count: int
    array_count: int
    fast_array_count: int
    fast_array_elements: int
    binary_object_count: int
    binary_object_size: int



class Runtime:
    def compute_memory_usage(self) -> MemoryUsage:
        ...
    
    def dump_memory_usage(self, file: object) -> object:
        ...

    def execute_pending_job(self) -> Context | None:
        ...

    def is_job_pending(self) -> bool:
        ...
    
    def run_gc(self) -> None:
        """
        Runs QuickJS-NG's internal Garbage Collector
        
        **Warning!** Use at your own risk.
        """
    
    def set_memory_limit(self, limit: int) -> None:
        ...
    
    def set_max_stack_size(self, max_stack_size: int) -> None:
        ...
    
    def update_statck_top(self) -> None:
        ...
    


class _OView:
    def __init__(self, obj: Object) -> None:
        ...
    
    def __len__(self): # -> unsigned int:
        ...
    


class _ObjectItemsView(_OView):
    def __iter__(self) -> Generator[tuple[object, object], None, None]:
        ...
    


class _ObjectKeysView(_OView):
    def __iter__(self) -> Generator[object, None, None]:
        ...
    
    def __contains__(self, key: object) -> bool:
        ...
    


class _ObjectValuesView(_OView):
    def __iter__(self) -> Generator[object, None, None]:
        ...
    
    def __contains__(self, value: object) -> bool:
        ...
    


class Object:
    def to_json(self) -> bytes:
        """
        Useful when debugging or handling unknown js to py conversions
        NOTE: for best results, using third party libraries like orjson 
        or msgspec is advised. 
        """
        ...
    
    def items(self) -> _ObjectItemsView:
        ...
    
    def values(self) -> _ObjectValuesView:
        ...
    
    def keys(self) -> _ObjectKeysView:
        ...
    


class Context:
    def __init__(self, runtime: Runtime = Runtime()) -> None:
        ...
    
    def eval(self, code: object, filename: object = ..., module: bool = ..., strict: bool = ..., backtrace_barrier: bool = ..., promise: bool = ...) -> object:
        """evaluates javascript code"""
        ...
    
    def get_global(self) -> object | Object:
        ...
    
    def json_parse(self, json: object):
        ...
    


class CancelledError(Exception):
    """Promise was rejected"""
    ...


class InvalidStateError(Exception):
    """Promise on inavlid state"""
    ...


class Promise(Object):
    def add_done_callback(self, fn: object) -> object:
        """Attaches a callable callback when promise finishes or raises an exception"""
        ...
    
    def exception(self) -> object:
        ...
    
    def done(self) -> bool:
        ...
    
    def remove_done_callback(self, fn: object) -> int:
        """Remove all instances of a callback from the "call when done" list.

        Returns the number of callbacks removed.
        """
        ...
    
    def result(self) -> object:
        ...
    
    def poll(self) -> object:
        """Polls QuickJS Eventloop a single cycle while attempting
        to wait for this Promise to complete"""
        ...
    



