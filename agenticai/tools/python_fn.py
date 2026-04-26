class PythonFnTool:
    def __init__(self, allowed_functions=None):
        self.allowed_functions = allowed_functions or []

    def run(self, args, session_id=None):
        fn_name = args.get("fn")
        fn_args = args.get("args", {})
        # TODO: implement secure sandboxed execution (do NOT run arbitrary user code in process)
        from .fn_registry import FN_REGISTRY
        fn = FN_REGISTRY.get(fn_name)
        if not fn:
            raise ValueError("Function not found")
        return fn(**fn_args)
