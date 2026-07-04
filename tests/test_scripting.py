from cyjs import Context


def test_script_args(ctx: Context):
    ctx.set_script_arguments("cool.py", "--help")
    assert ctx.get("scriptArgs").to_json() == b'cool.py,--help'

def test_std_handlers(ctx: Context):
    ctx.add_std_helpers("--help")
    assert ctx.get("scriptArgs").to_json() == b'--help'
