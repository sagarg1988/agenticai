from tools.registry import ToolRegistry

class ToolExecutor:
    def __init__(self):
        self.registry = ToolRegistry()

    def execute_plan(self, plan, session_id):
        results = {}
        for step in plan.get("steps", []):
            step_id = step.get("id")
            tool_name = step.get("tool")
            args = step.get("args", {})
            tool = self.registry.get(tool_name)
            if not tool:
                results[step_id] = {"error": f"Unknown tool {tool_name}"}
                continue
            try:
                res = tool.run(args, session_id=session_id)
                results[step_id] = {"ok": True, "result": res}
            except Exception as e:
                results[step_id] = {"ok": False, "error": str(e)}
        return results
