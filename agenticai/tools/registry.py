from .web_search import WebSearchTool
from .db_query import DBQueryTool
from .python_fn import PythonFnTool
from .http_api import HTTPAPITool

class ToolRegistry:
    def __init__(self):
        self.tools = {
            "web_search": WebSearchTool(),
            "db_query": DBQueryTool(),
            "python_fn": PythonFnTool(),
            "http_api": HTTPAPITool(),
            "llm_synth": None
        }

    def get(self, name):
        return self.tools.get(name)
