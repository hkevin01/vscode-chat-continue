#!/usr/bin/env python3
"""
Optional GUI for VS Code Chat Continue automation tool.

This provides a simple graphical interface for:
- Starting/stopping automation
- Viewing real-time statistics
- Configuring settings
- Emergency stop functionality
"""

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from core.automation_engine import AutomationEngine
    from core.config_manager import ConfigManager
    from utils.logger import AutomationLogger
except ImportError as e:
    print(f"Warning: Could not import automation components: {e}")
    AutomationEngine = None
    ConfigManager = None
    AutomationLogger = None


class AutomationGUI:
    """Simple GUI for VS Code Chat Continue automation."""
    
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.root.title("VS Code Chat Continue Automation")
        self.root.geometry("600x500")
        
        # State
        self.engine: Optional[AutomationEngine] = None
        self.config_manager: Optional[ConfigManager] = None
        self.is_running = False
        
        # Setup GUI
        self._setup_gui()
        self._load_config()
        
    def _setup_gui(self):
        """Set up the GUI components."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="VS Code Chat Continue Automation",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Control buttons frame
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        controls_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Start/Stop button
        self.start_stop_btn = ttk.Button(controls_frame, text="Start Automation",
                                        command=self._toggle_automation)
        self.start_stop_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Pause/Resume button  
        self.pause_resume_btn = ttk.Button(controls_frame, text="Pause",
                                          command=self._toggle_pause, state="disabled")
        self.pause_resume_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Emergency stop button
        self.emergency_btn = ttk.Button(controls_frame, text="Emergency Stop",
                                       command=self._emergency_stop, state="disabled")
        self.emergency_btn.grid(row=0, column=2)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Interval setting
        ttk.Label(config_frame, text="Interval (seconds):").grid(row=0, column=0, sticky=tk.W)
        self.interval_var = tk.StringVar(value="2.0")
        interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        # Dry run checkbox
        self.dry_run_var = tk.BooleanVar(value=True)
        dry_run_cb = ttk.Checkbutton(config_frame, text="Dry Run Mode",
                                    variable=self.dry_run_var)
        dry_run_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Config buttons
        config_btn_frame = ttk.Frame(config_frame)
        config_btn_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(config_btn_frame, text="Load Config",
                  command=self._load_config_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="Save Config",
                  command=self._save_config_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(config_btn_frame, text="Reset to Defaults",
                  command=self._reset_config).pack(side=tk.LEFT)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Statistics text area
        self.stats_text = tk.Text(stats_frame, height=10, width=70, state=tk.DISABLED)
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        # Update stats periodically
        self._update_stats()
        
    def _load_config(self):
        """Load configuration."""
        try:
            if ConfigManager:
                self.config_manager = ConfigManager()
                
                # Update GUI with config values
                interval = self.config_manager.get('automation.interval_seconds', 2.0)
                self.interval_var.set(str(interval))
                
                dry_run = self.config_manager.get('automation.dry_run', True)
                self.dry_run_var.set(dry_run)
                
                self.status_var.set("Configuration loaded")
            else:
                self.status_var.set("Warning: Automation components not available")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
            self.status_var.set("Error loading configuration")
    
    def _load_config_file(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if ConfigManager:
                    self.config_manager = ConfigManager(Path(filename))
                    self._load_config()
                    messagebox.showinfo("Success", "Configuration loaded successfully")
                else:
                    messagebox.showwarning("Warning", "Automation components not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def _save_config_file(self):
        """Save configuration to file."""
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Update config with GUI values
                if self.config_manager:
                    self.config_manager.set('automation.interval_seconds',
                                          float(self.interval_var.get()))
                    self.config_manager.set('automation.dry_run',
                                          self.dry_run_var.get())
                    
                    # Save to file
                    config_data = self.config_manager.config
                    with open(filename, 'w') as f:
                        json.dump(config_data, f, indent=2)
                    
                    messagebox.showinfo("Success", "Configuration saved successfully")
                else:
                    messagebox.showwarning("Warning", "No configuration to save")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def _reset_config(self):
        """Reset configuration to defaults."""
        if messagebox.askyesno("Confirm", "Reset configuration to defaults?"):
            try:
                if ConfigManager:
                    self.config_manager = ConfigManager()
                    self._load_config()
                    messagebox.showinfo("Success", "Configuration reset to defaults")
                else:
                    messagebox.showwarning("Warning", "Automation components not available")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset configuration: {e}")
    
    def _toggle_automation(self):
        """Toggle automation on/off."""
        try:
            if not self.is_running:
                # Start automation
                if not AutomationEngine or not self.config_manager:
                    messagebox.showwarning("Warning", 
                                         "Automation components not available for testing")
                    self.status_var.set("Demo mode - automation components not available")
                    self.is_running = True
                    self._update_gui_state()
                    return
                
                # Update config with GUI values
                self.config_manager.set('automation.interval_seconds',
                                      float(self.interval_var.get()))
                self.config_manager.set('automation.dry_run',
                                      self.dry_run_var.get())
                
                # Create engine
                self.engine = AutomationEngine(self.config_manager)
                
                # Start automation (in dry run mode for GUI demo)
                self.is_running = True
                self.status_var.set("Automation started (demo mode)")
                
            else:
                # Stop automation
                if self.engine:
                    # In a real implementation, we'd call self.engine.stop()
                    self.engine = None
                
                self.is_running = False
                self.status_var.set("Automation stopped")
            
            self._update_gui_state()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle automation: {e}")
            self.status_var.set("Error")
    
    def _toggle_pause(self):
        """Toggle pause/resume."""
        try:
            if self.engine:
                if self.pause_resume_btn.cget("text") == "Pause":
                    self.engine.pause()
                    self.pause_resume_btn.config(text="Resume")
                    self.status_var.set("Automation paused")
                else:
                    self.engine.resume()
                    self.pause_resume_btn.config(text="Pause")
                    self.status_var.set("Automation resumed")
            else:
                # Demo mode
                current_text = self.pause_resume_btn.cget("text")
                if current_text == "Pause":
                    self.pause_resume_btn.config(text="Resume")
                    self.status_var.set("Demo: Paused")
                else:
                    self.pause_resume_btn.config(text="Pause")
                    self.status_var.set("Demo: Resumed")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to toggle pause: {e}")
    
    def _emergency_stop(self):
        """Emergency stop automation."""
        try:
            if self.engine:
                self.engine.emergency_stop()
            
            self.is_running = False
            self.engine = None
            self.status_var.set("EMERGENCY STOP activated")
            self._update_gui_state()
            
            messagebox.showwarning("Emergency Stop", "Automation has been stopped immediately")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to emergency stop: {e}")
    
    def _update_gui_state(self):
        """Update GUI button states based on automation state."""
        if self.is_running:
            self.start_stop_btn.config(text="Stop Automation")
            self.pause_resume_btn.config(state="normal", text="Pause")
            self.emergency_btn.config(state="normal")
        else:
            self.start_stop_btn.config(text="Start Automation")
            self.pause_resume_btn.config(state="disabled", text="Pause")
            self.emergency_btn.config(state="disabled")
    
    def _update_stats(self):
        """Update statistics display."""
        try:
            # Clear text area
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            
            if self.engine and hasattr(self.engine, 'get_performance_report'):
                # Get real statistics
                report = self.engine.get_performance_report()
                
                stats_text = f"Runtime: {report['runtime_seconds']:.1f} seconds\n"
                stats_text += f"Windows processed: {report['statistics']['windows_processed']}\n"
                stats_text += f"Buttons found: {report['statistics']['buttons_found']}\n"
                stats_text += f"Success rate: {report['success_rate']:.1%}\n"
                stats_text += f"Cache hit rate: {report['cache_efficiency']['hit_rate']:.1%}\n"
                
            elif self.is_running:
                # Demo statistics
                stats_text = "DEMO MODE - Automation components not available\n\n"
                stats_text += "This GUI demonstrates the interface for:\n"
                stats_text += "• Starting/stopping automation\n"
                stats_text += "• Real-time statistics monitoring\n"
                stats_text += "• Configuration management\n"
                stats_text += "• Emergency stop functionality\n\n"
                stats_text += "To use with real automation:\n"
                stats_text += "1. Install all dependencies (see requirements.txt)\n"
                stats_text += "2. Set up proper Python environment\n"
                stats_text += "3. Run with automation components available\n"
                
            else:
                stats_text = "Automation not running\n\n"
                stats_text += "Click 'Start Automation' to begin monitoring VS Code windows\n"
                stats_text += "for Continue buttons in Copilot Chat.\n\n"
                stats_text += "Statistics will appear here when running."
            
            self.stats_text.insert(1.0, stats_text)
            self.stats_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error updating stats: {e}")
        
        # Schedule next update
        self.root.after(2000, self._update_stats)
    
    def run(self):
        """Run the GUI."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("GUI interrupted by user")
        except Exception as e:
            print(f"GUI error: {e}")


def main():
    """Main function to run the GUI."""
    print("Starting VS Code Chat Continue Automation GUI...")
    
    try:
        app = AutomationGUI()
        app.run()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
