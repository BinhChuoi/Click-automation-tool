import tkinter as tk

class HotkeyOverlay:
    def __init__(self, tk_root, hotkey_action_pairs):
        self.overlay = tk.Toplevel(tk_root)
        self.overlay.title("Hotkey Overlay")
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.9)  # Semi-transparent overlay window
        self.overlay.configure(bg='black')
        self.overlay.overrideredirect(True)
        self.overlay.lift()
        self.overlay.update_idletasks()
        screen_width = self.overlay.winfo_screenwidth()
        screen_height = self.overlay.winfo_screenheight()
        label_width = 350
        label_height = 80
        num_labels = len(hotkey_action_pairs)
        total_width = label_width * num_labels
        x = (screen_width // 2) - (total_width // 2)
        y = screen_height - label_height - 40  # 40px above bottom
        self.overlay.geometry(f"{total_width}x{label_height}+{x}+{y}")
        overlay_frame = tk.Frame(self.overlay, bg='black', width=total_width, height=label_height)
        overlay_frame.pack(fill=tk.BOTH, expand=True)
        for idx, (hotkey, action_name) in enumerate(hotkey_action_pairs):
            label_text = f"{hotkey} → {action_name}"
            label = tk.Label(
                overlay_frame,
                text=label_text,
                bg='black',  # Match overlay background
                fg='yellow',
                font=("Arial", 24, "bold"),
                borderwidth=0,
                highlightthickness=0,
                padx=0,
                pady=0
            )
            label.place(x=idx*label_width, y=0, width=label_width, height=label_height)
        # Auto-close after 20 seconds
        self.overlay.after(20000, self.overlay.destroy)

    def destroy(self):
        self.overlay.destroy()
