
"""
Entry point for the core component.
"""

from core.main.src.impl.tool.ToolManager import ToolManager

class CoreComponent:
    def __init__(self):
        self.tool_manager = ToolManager

    def start(self):
        print("Core component started.")
        self.tool_manager.start()

def build_core_component():
    return CoreComponent()

if __name__ == "__main__":
    build_core_component().start()
