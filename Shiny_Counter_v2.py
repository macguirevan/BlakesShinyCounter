import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import keyboard
from threading import Thread
import sys

class ShinyCounter:
    def __init__(self, root):
        self.root = root
        self.root.title("Shiny Pokemon Counter")
        self.root.geometry("550x450")
        self.root.configure(bg="#2c3e50")
        
        # Default settings
        self.counter = 0
        self.increment_hotkey = "F2"  # Default increment hotkey
        self.decrement_hotkey = "F3"  # Default decrement hotkey
        self.config_file = "shiny_counter_config.json"
        
        # Store hotkey IDs for removal
        self.hotkey_ids = {}
        
        # Load existing config
        self.load_config()
        
        # Create GUI
        self.setup_gui()
        
        # Setup hotkey listeners
        self.setup_hotkeys()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start hotkey listener in separate thread
        self.listening = True
        self.listener_thread = Thread(target=self.hotkey_listener, daemon=True)
        self.listener_thread.start()
    
    def setup_gui(self):
        # Title
        title_label = tk.Label(
            self.root,
            text="✨ Shiny Pokemon Counter ✨",
            font=("Arial", 20, "bold"),
            fg="#f1c40f",
            bg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # Counter display
        self.counter_label = tk.Label(
            self.root,
            text=str(self.counter),
            font=("Arial", 48, "bold"),
            fg="#e74c3c",
            bg="#34495e",
            relief="ridge",
            bd=5,
            width=10
        )
        self.counter_label.pack(pady=15)
        
        # Counter text
        self.counter_text = tk.Label(
            self.root,
            text="Encounters",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        self.counter_text.pack()
        
        # Buttons frame
        button_frame = tk.Frame(self.root, bg="#2c3e50")
        button_frame.pack(pady=15)
        
        # Decrement button
        decrement_btn = tk.Button(
            button_frame,
            text="-1 Encounter",
            font=("Arial", 12),
            bg="#e67e22",
            fg="white",
            padx=15,
            pady=8,
            command=self.decrement_counter
        )
        decrement_btn.grid(row=0, column=0, padx=5)
        
        # Increment button
        increment_btn = tk.Button(
            button_frame,
            text="+1 Encounter",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=15,
            pady=8,
            command=self.increment_counter
        )
        increment_btn.grid(row=0, column=1, padx=5)
        
        # Reset button
        reset_btn = tk.Button(
            button_frame,
            text="Reset Counter",
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=8,
            command=self.reset_counter
        )
        reset_btn.grid(row=0, column=2, padx=5)
        
        # Hotkey info frame
        hotkey_frame = tk.Frame(self.root, bg="#2c3e50")
        hotkey_frame.pack(pady=10)
        
        # Increment hotkey display
        self.increment_hotkey_label = tk.Label(
            hotkey_frame,
            text=f"Increment: {self.increment_hotkey}",
            font=("Arial", 10),
            fg="#27ae60",
            bg="#2c3e50"
        )
        self.increment_hotkey_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Decrement hotkey display
        self.decrement_hotkey_label = tk.Label(
            hotkey_frame,
            text=f"Decrement: {self.decrement_hotkey}",
            font=("Arial", 10),
            fg="#e67e22",
            bg="#2c3e50"
        )
        self.decrement_hotkey_label.grid(row=1, column=0, padx=10, pady=5)
        
        # Change hotkey buttons frame
        change_hotkey_frame = tk.Frame(self.root, bg="#2c3e50")
        change_hotkey_frame.pack(pady=5)
        
        # Change increment hotkey button
        change_inc_btn = tk.Button(
            change_hotkey_frame,
            text="Change Increment Hotkey",
            font=("Arial", 9),
            bg="#27ae60",
            fg="white",
            padx=10,
            pady=3,
            command=lambda: self.change_hotkey("increment")
        )
        change_inc_btn.grid(row=0, column=0, padx=5, pady=2)
        
        # Change decrement hotkey button
        change_dec_btn = tk.Button(
            change_hotkey_frame,
            text="Change Decrement Hotkey",
            font=("Arial", 9),
            bg="#e67e22",
            fg="white",
            padx=10,
            pady=3,
            command=lambda: self.change_hotkey("decrement")
        )
        change_dec_btn.grid(row=0, column=1, padx=5, pady=2)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Hotkeys work even when window is minimized",
            font=("Arial", 9, "italic"),
            fg="#95a5a6",
            bg="#2c3e50"
        )
        instructions.pack(pady=10)
    
    def increment_counter(self):
        self.counter += 1
        self.update_display()
        self.save_config()
        # Flash the window to show it worked
        self.flash_window()
    
    def decrement_counter(self):
        if self.counter > 0:
            self.counter -= 1
            self.update_display()
            self.save_config()
            # Flash the window to show it worked
            self.flash_window()
        else:
            # Play system sound to indicate cannot go below 0
            self.root.bell()
    
    def flash_window(self):
        # Briefly change background color to show hotkey worked
        original_color = self.counter_label.cget("bg")
        self.counter_label.config(bg="#3498db")
        self.root.after(100, lambda: self.counter_label.config(bg=original_color))
    
    def reset_counter(self):
        if messagebox.askyesno("Reset Counter", "Are you sure you want to reset the counter to 0?"):
            self.counter = 0
            self.update_display()
            self.save_config()
    
    def update_display(self):
        self.counter_label.config(text=str(self.counter))
    
    def change_hotkey(self, hotkey_type):
        action = "increment" if hotkey_type == "increment" else "decrement"
        current_hotkey = self.increment_hotkey if hotkey_type == "increment" else self.decrement_hotkey
        
        new_hotkey = simpledialog.askstring(
            f"Change {action.title()} Hotkey",
            f"Current {action} hotkey: {current_hotkey}\n\nEnter the key you want to use as the {action} hotkey:\n\n(Examples: F1, F2, F3, F4, F5, F6, insert, delete, home, end, etc.)",
            parent=self.root
        )
        
        if new_hotkey and new_hotkey.strip():
            # Clean the input
            new_hotkey = new_hotkey.strip().upper()
            
            # Remove old hotkey
            if hotkey_type == "increment":
                old_key = self.increment_hotkey
                self.increment_hotkey = new_hotkey
            else:
                old_key = self.decrement_hotkey
                self.decrement_hotkey = new_hotkey
            
            # Re-setup hotkeys
            self.setup_hotkeys()
            
            # Update labels
            self.increment_hotkey_label.config(text=f"Increment: {self.increment_hotkey}")
            self.decrement_hotkey_label.config(text=f"Decrement: {self.decrement_hotkey}")
            
            self.save_config()
            messagebox.showinfo("Success", f"{action.title()} hotkey changed to: {new_hotkey}")
    
    def setup_hotkeys(self):
        # Clear any existing hotkeys first
        keyboard.unhook_all()
        
        # Set up increment hotkey
        try:
            keyboard.add_hotkey(self.increment_hotkey, self.increment_counter)
        except Exception as e:
            print(f"Error setting increment hotkey: {e}")
            messagebox.showwarning("Hotkey Error", 
                f"Could not set increment hotkey '{self.increment_hotkey}'. Try a different key.\nDefaulting to F2.")
            self.increment_hotkey = "F2"
            keyboard.add_hotkey(self.increment_hotkey, self.increment_counter)
        
        # Set up decrement hotkey
        try:
            keyboard.add_hotkey(self.decrement_hotkey, self.decrement_counter)
        except Exception as e:
            print(f"Error setting decrement hotkey: {e}")
            messagebox.showwarning("Hotkey Error", 
                f"Could not set decrement hotkey '{self.decrement_hotkey}'. Try a different key.\nDefaulting to F3.")
            self.decrement_hotkey = "F3"
            keyboard.add_hotkey(self.decrement_hotkey, self.decrement_counter)
    
    def hotkey_listener(self):
        # This runs in a separate thread to keep the hotkey active
        while self.listening:
            try:
                keyboard.wait()
            except:
                pass
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.counter = config.get('counter', 0)
                    self.increment_hotkey = config.get('increment_hotkey', 'F2')
                    self.decrement_hotkey = config.get('decrement_hotkey', 'F3')
            except:
                pass
    
    def save_config(self):
        config = {
            'counter': self.counter,
            'increment_hotkey': self.increment_hotkey,
            'decrement_hotkey': self.decrement_hotkey
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def on_closing(self):
        self.listening = False
        self.save_config()
        # Clean up keyboard hooks
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.destroy()

if __name__ == "__main__":
    # Check if keyboard module is installed
    try:
        import keyboard
    except ImportError:
        print("Please install the 'keyboard' module first:")
        print("Open terminal/command prompt and run: pip install keyboard")
        print("\nOr in VS Code:")
        print("1. Open Terminal (View → Terminal)")
        print("2. Type: pip install keyboard")
        print("3. Press Enter")
        input("\nPress Enter to exit...")
        exit()
    
    # Check if running on Windows (keyboard module works best on Windows)
    if sys.platform != "win32":
        print("Warning: The keyboard module works best on Windows.")
        print("Some features may not work correctly on other operating systems.")
        print("Press Enter to continue anyway...")
        input()
    
    root = tk.Tk()
    app = ShinyCounter(root)
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    root.mainloop()
    