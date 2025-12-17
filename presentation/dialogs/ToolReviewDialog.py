import tkinter as tk
from tkinter import messagebox
from utils.Signals import StartTool, DeleteTool
from presentation.PresentationManager import PresentationManager
def show_tool_review_dialog(tool_maker, tool_files, tool_data_map):
    if not tool_files:
        messagebox.showinfo("Tool Review", "No tools found in storage.")
        return

    root = PresentationManager.get_instance().get_tk_root()
    review_win = tk.Toplevel(root)
    review_win.title("Tool Review")

    listbox = tk.Listbox(review_win, width=50)
    for f in tool_files:
        listbox.insert(tk.END, f)
    listbox.pack()

    info_label = tk.Label(review_win, text="Select a tool to see info")
    info_label.pack()

    def on_select(event):
        selection = listbox.curselection()
        if selection:
            selected_tool = tool_files[selection[0]]
            tool_data = tool_data_map.get(selected_tool)
            if tool_data:
                info = f"Tool ID: {tool_data.get('tool_id', selected_tool)}\nType: {tool_data.get('tool_type', 'Unknown')}\n"
            else:
                info = f"Failed to load tool: {selected_tool}"
            info_label.config(text=info)

    listbox.bind('<<ListboxSelect>>', on_select)

    def start_tool():
        selection = listbox.curselection()
        if selection:
            selected_tool = tool_files[selection[0]]
            tool_data = tool_data_map.get(selected_tool)
            if tool_data:
                StartTool.send("tool_review", data={"tool_id": tool_data.get('tool_id', selected_tool)})

    def delete_tool():
        selection = listbox.curselection()
        if selection:
            selected_tool = tool_files[selection[0]]
            tool_data = tool_data_map.get(selected_tool)
            if tool_data:
                DeleteTool.send("tool_review", data={"tool_id": tool_data.get('tool_id', selected_tool)})

    tk.Button(review_win, text="Start", command=start_tool).pack(side=tk.LEFT)
    tk.Button(review_win, text="Delete", command=delete_tool).pack(side=tk.LEFT)
    tk.Button(review_win, text="Back", command=review_win.destroy).pack(side=tk.RIGHT)
