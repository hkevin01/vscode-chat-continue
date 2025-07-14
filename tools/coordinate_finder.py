#!/usr/bin/env python3
"""
Coordinate finder tool for VS Code Chat Continue automation.
Helps users find the exact coordinates of Continue buttons and chat fields.
"""

import json
import sys
import time
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import messagebox, ttk

    import pyautogui
    from PIL import ImageTk
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install pyautogui pillow")
    sys.exit(1)


class CoordinateFinder:
    """GUI tool for finding and testing coordinates."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VS Code Chat Continue - Coordinate Finder")
        self.root.geometry("800x600")
        
        self.coordinates = []
        self.screenshot = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Instructions
        instructions = tk.Text(main_frame, height=8, width=70)
        instructions.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        instructions.insert(tk.END, """
Coordinate Finder for VS Code Chat Continue

Instructions:
1. Click 'Take Screenshot' to capture your screen
2. Click on the Continue button in the image to mark its position
3. Click on the chat input field to mark its position
4. Use 'Test Click' to verify coordinates work correctly
5. Save coordinates to configuration file

Tips:
- Make sure VS Code is open and visible
- Try to capture when Continue button is visible
- Chat field is usually at the bottom of the chat panel
        """)
        instructions.config(state=tk.DISABLED)
        
        # Screenshot button
        ttk.Button(
            main_frame, text="Take Screenshot",
            command=self.take_screenshot
        ).grid(row=1, column=0, pady=5, sticky=tk.W)
        
        # Clear button
        ttk.Button(
            main_frame, text="Clear Coordinates",
            command=self.clear_coordinates
        ).grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Coordinates display
        self.coords_frame = ttk.LabelFrame(main_frame, text="Coordinates")
        self.coords_frame.grid(
            row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E)
        )
        
        self.coords_text = tk.Text(self.coords_frame, height=4, width=70)
        self.coords_text.pack(padx=5, pady=5)
        
        # Test buttons
        test_frame = ttk.Frame(main_frame)
        test_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        ttk.Button(
            test_frame, text="Test Continue Button",
            command=self.test_continue_click
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            test_frame, text="Test Chat Field",
            command=self.test_chat_click
        ).pack(side=tk.LEFT, padx=5)
        
        # Save button
        ttk.Button(
            main_frame, text="Save to Config",
            command=self.save_to_config
        ).pack(pady=10)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.pack(pady=5)
        
        # Canvas for screenshot
        self.canvas = tk.Canvas(main_frame, bg='white', width=600, height=400)
        self.canvas.grid(row=4, column=0, columnspan=2, pady=10)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
    def take_screenshot(self):
        """Take a screenshot and display it."""
        self.status_label.config(text="Taking screenshot...")
        self.root.update()
        
        try:
            # Hide window temporarily
            self.root.withdraw()
            time.sleep(1)  # Give time for window to hide
            
            # Take screenshot
            self.screenshot = pyautogui.screenshot()
            
            # Show window again
            self.root.deiconify()
            
            # Resize screenshot to fit canvas
            canvas_width = 600
            canvas_height = 400
            
            img_width, img_height = self.screenshot.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            resized_img = self.screenshot.resize((new_width, new_height))
            self.photo = ImageTk.PhotoImage(resized_img)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2, canvas_height // 2,
                image=self.photo
            )
            
            self.scale_factor = scale
            msg = "Screenshot taken. Click on Continue button and chat field."
            self.status_label.config(text=msg)
            
        except Exception as e:
            error_msg = f"Failed to take screenshot: {str(e)}"
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="Screenshot failed")
    
    def on_canvas_click(self, event):
        """Handle clicks on the screenshot canvas."""
        if not self.screenshot:
            messagebox.showwarning("Warning", "Take a screenshot first!")
            return
        
        # Convert canvas coordinates to screen coordinates
        canvas_x = event.x - (600 // 2 - self.photo.width() // 2)
        canvas_y = event.y - (400 // 2 - self.photo.height() // 2)
        
        # Scale back to original screenshot size
        screen_x = int(canvas_x / self.scale_factor)
        screen_y = int(canvas_y / self.scale_factor)
        
        # Determine what type of coordinate this is
        if len(self.coordinates) == 0:
            coord_type = "Continue Button"
            color = "red"
        elif len(self.coordinates) == 1:
            coord_type = "Chat Field"
            color = "blue"
        else:
            # Replace last coordinate
            self.coordinates.pop()
            coord_type = "Chat Field"
            color = "blue"
        
        self.coordinates.append({
            'type': coord_type,
            'x': screen_x,
            'y': screen_y
        })
        
        # Draw marker on canvas
        marker_x = canvas_x + (600 // 2 - self.photo.width() // 2)
        marker_y = canvas_y + (400 // 2 - self.photo.height() // 2)
        
        self.canvas.create_oval(
            marker_x - 5, marker_y - 5,
            marker_x + 5, marker_y + 5,
            fill=color, outline='white', width=2
        )
        
        # Update coordinates display
        self.update_coordinates_display()
        
        self.status_label.config(
            text=f"Marked {coord_type} at ({screen_x}, {screen_y})"
        )
    
    def update_coordinates_display(self):
        """Update the coordinates text display."""
        self.coords_text.delete(1.0, tk.END)
        
        for coord in self.coordinates:
            self.coords_text.insert(
                tk.END,
                f"{coord['type']}: X={coord['x']}, Y={coord['y']}\n"
            )
    
    def clear_coordinates(self):
        """Clear all marked coordinates."""
        self.coordinates = []
        self.coords_text.delete(1.0, tk.END)
        
        # Redraw screenshot without markers
        if self.screenshot:
            self.take_screenshot()
        
        self.status_label.config(text="Coordinates cleared")
    
    def test_continue_click(self):
        """Test clicking the Continue button coordinate."""
        continue_coords = [
            c for c in self.coordinates if c['type'] == 'Continue Button'
        ]
        
        if not continue_coords:
            msg = "No Continue button coordinate marked!"
            messagebox.showwarning("Warning", msg)
            return
        
        coord = continue_coords[0]
        self.test_click(coord['x'], coord['y'], "Continue Button")
    
    def test_chat_click(self):
        """Test clicking the chat field coordinate."""
        chat_coords = [c for c in self.coordinates if c['type'] == 'Chat Field']
        
        if not chat_coords:
            messagebox.showwarning("Warning", "No chat field coordinate marked!")
            return
        
        coord = chat_coords[0]
        self.test_click(coord['x'], coord['y'], "Chat Field")
    
    def test_click(self, x, y, name):
        """Test a click at given coordinates."""
        result = messagebox.askyesno(
            "Test Click",
            f"Test click {name} at ({x}, {y})?\n\n"
            "This will minimize the window and perform the click."
        )
        
        if result:
            try:
                # Hide window
                self.root.withdraw()
                time.sleep(1)
                
                # Perform click
                pyautogui.click(x, y)
                time.sleep(2)
                
                # Show window again
                self.root.deiconify()
                
                self.status_label.config(text=f"Test click performed at ({x}, {y})")
                
            except Exception as e:
                messagebox.showerror("Error", f"Click test failed: {str(e)}")
                self.root.deiconify()
    
    def save_to_config(self):
        """Save coordinates to configuration file."""
        if len(self.coordinates) < 2:
            messagebox.showwarning(
                "Warning",
                "Please mark both Continue button and chat field coordinates!"
            )
            return
        
        continue_coord = None
        chat_coord = None
        
        for coord in self.coordinates:
            if coord['type'] == 'Continue Button':
                continue_coord = coord
            elif coord['type'] == 'Chat Field':
                chat_coord = coord
        
        if not continue_coord or not chat_coord:
            messagebox.showwarning("Warning", "Both coordinates are required!")
            return
        
        # Load existing config
        config_path = Path('config/default.json')
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception:
                config = {}
        else:
            config = {}
        
        # Update automation section
        if 'automation' not in config:
            config['automation'] = {}
        
        config['automation']['continue_button_coordinates'] = {
            'x': continue_coord['x'],
            'y': continue_coord['y']
        }
        
        config['automation']['chat_field_coordinates'] = {
            'x': chat_coord['x'],
            'y': chat_coord['y']
        }
        
        config['automation']['enable_chat_fallback'] = True
        
        # Save config
        try:
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo(
                "Success",
                f"Coordinates saved to {config_path}\n\n"
                f"Continue Button: ({continue_coord['x']}, {continue_coord['y']})\n"
                f"Chat Field: ({chat_coord['x']}, {chat_coord['y']})"
            )
            
            self.status_label.config(text="Coordinates saved to config")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")
    
    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Run the coordinate finder tool."""
    try:
        import json
        finder = CoordinateFinder()
        finder.run()
    except KeyboardInterrupt:
        print("\n👋 Coordinate finder closed by user")
    except Exception as e:
        print(f"❌ Error running coordinate finder: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
