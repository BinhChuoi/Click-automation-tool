import sys
from common.impl.contextAction.KeyboardManager import KeyboardManager


class ToolMaker:
    """
    Helper class to create new tool instances and define keyboard settings interactively.
    """
    def __init__(self):
        self.tool_name = None
        self.keyboard_mappings = {}

    def show_hotkeys_gui(self):
        import tkinter as tk
        root = tk.Tk()
        root.title("Bound Hotkeys")
        label = tk.Label(root, text="Currently bound hotkeys:")
        label.pack()
        for action, key in self.keyboard_mappings.items():
            tk.Label(root, text=f"{action}: {key}").pack()
        root.mainloop()

    def prompt_tool_name(self):
        self.tool_name = input("Enter the name of the new tool: ").strip()
        print(f"Tool name set to: {self.tool_name}")

    def prompt_keyboard_settings(self):
        print("Define keyboard actions for this tool.")
        while True:
            action = input("Enter action name (or 'done' to finish): ").strip()
            if action.lower() == 'done':
                break
            key = input(f"Enter keyboard key(s) for action '{action}': ").strip()
            self.keyboard_mappings[action] = key
            print(f"Mapped action '{action}' to key(s) '{key}'")

    def create_tool(self):
        self.prompt_tool_name()
        self.prompt_keyboard_settings()
        print("Tool creation complete!")
        print(f"Tool name: {self.tool_name}")
        print("Keyboard mappings:")
        for action, key in self.keyboard_mappings.items():
            print(f"  {action}: {key}")
        self.show_hotkeys_gui()
        # Here you could add logic to save these settings or generate a tool class
        return {
            'tool_name': self.tool_name,
            'keyboard_mappings': self.keyboard_mappings
        }

if __name__ == "__main__":
    maker = ToolMaker()
    maker.create_tool()
