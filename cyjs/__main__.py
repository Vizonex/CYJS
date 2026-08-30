from pathlib import Path
from typing import Annotated

from typer import Argument, Option, Typer

from ._cyjs import Context

app = Typer()

@app.command()
def cli(
    args:Annotated[list[str] | None, Argument(help="Arguments to pass to quickjs script")] = None,
    script: Annotated[Path | None, Option("-C", "--script", help="load module as a script", exists=True)] = None,
    eval_code: Annotated[str | None, Option("-e", "--eval", metavar="EVAL", help= "evaluate EXPR")] = None,
    strict: bool = False,
    backtrace_barrier: bool = False,
    promise: bool = False
) -> None:
    """A Simplistic script runner for testing code with cyjs"""
    
    ctx = Context()
    if args:
        ctx.set_script_arguments(*args)
    ctx.add_std_print_handlers()

    if script:
        code = script.read_bytes()
        ctx.eval_module(code, script.as_posix(), strict, backtrace_barrier, promise)
    elif eval_code:
        ctx.eval(eval_code, strict=strict, backtrace_barrier=backtrace_barrier, promise=promise)

if __name__ == "__main__":
    app()
