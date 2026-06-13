import pytest

from cyjs._cyjs import Context


# oldest trick in the book...
def add(a: int, b: int) -> int:
    return a + b

def format_it(f: str):
    return f"{f} with data!"

def test_cclousre_bug_13(ctx: Context) -> None:
    """
    SEE: https://github.com/Vizonex/CYJS/issues/13
    """
    ctx.set("format_it", ctx.add_function(format_it, "format_it"))
    result = ctx.eval("globalThis.format_it(\"item\")")
    assert result == "item with data!"


def test_cclosure_eval(ctx: Context) -> None:
    func = ctx.add_function(add, "add")
    ctx.set("add", func)
    result = ctx.eval("globalThis.add(1, 2)")
    assert result == 3


def throw_exception():
    raise RuntimeError("Boo")


def test_function_that_raises_exception(ctx: Context):
    func = ctx.add_function(throw_exception, "py_throw_exception")
    ctx.set("py_throw", func)

    # The lower level gets the worm in this case since python does better with python
    # and Javascript does better with Javascript.
    with pytest.raises(RuntimeError, match=r"Boo"):
        ctx.eval("globalThis.py_throw()")
