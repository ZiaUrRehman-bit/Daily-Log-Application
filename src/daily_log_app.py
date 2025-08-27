import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import ttkbootstrap as ttkbs
from ttkbootstrap.constants import *
import os
import json
from datetime import datetime, timedelta
import calendar
import sys
import subprocess

class DailyLogManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Research Log Manager")
        self.root.geometry("1000x700")
        self.style = ttkbs.Style("darkly")
        
        # Initialize variables
        self.current_date = datetime.now()
        self.current_file = None
        self.dark_mode = True
        
        # Setup application data - using Documents folder for better accessibility
        self.documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
        self.app_data_dir = os.path.join(self.documents_dir, "Research Logs")
        if not os.path.exists(self.app_data_dir):
            os.makedirs(self.app_data_dir)
            
        self.settings_file = os.path.join(self.app_data_dir, "settings.json")
        self.load_settings()
        
        # Create UI
        self.setup_ui()
        
        # Load today's log
        self.load_todays_log()
        
        # Setup auto-save
        self.setup_auto_save()
        
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill=BOTH, expand=True)
        
        # Header with title and buttons
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Research Log Manager", 
                 font=("Helvetica", 16, "bold")).pack(side=LEFT)
        
        # Theme toggle button
        self.theme_btn = ttk.Button(header_frame, text="☀️", width=3,
                                   command=self.toggle_theme)
        self.theme_btn.pack(side=RIGHT, padx=(5, 0))
        
        # Formatting buttons
        format_frame = ttk.Frame(header_frame)
        format_frame.pack(side=RIGHT, padx=10)
        
        ttk.Button(format_frame, text="B", width=2, 
                  command=lambda: self.apply_format("bold")).pack(side=LEFT, padx=2)
        ttk.Button(format_frame, text="I", width=2, 
                  command=lambda: self.apply_format("italic")).pack(side=LEFT, padx=2)
        ttk.Button(format_frame, text="•", width=2, 
                  command=lambda: self.apply_format("bullet")).pack(side=LEFT, padx=2)
        
        # Save button
        ttk.Button(header_frame, text="Save", width=6,
                  command=self.save_log).pack(side=RIGHT, padx=5)
        
        # Calendar and editor panes
        paned_window = ttk.PanedWindow(main_container, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=True)
        
        # Calendar frame
        calendar_frame = ttk.Frame(paned_window, width=180, padding=3)
        paned_window.add(calendar_frame, weight=1)
        
        # Calendar navigation
        cal_nav_frame = ttk.Frame(calendar_frame)
        cal_nav_frame.pack(fill=X, pady=(0, 5))
        
        ttk.Button(cal_nav_frame, text="◀", width=3,
                  command=self.prev_month).pack(side=LEFT)
        self.month_year_var = tk.StringVar()
        self.month_year_label = ttk.Label(cal_nav_frame, textvariable=self.month_year_var,
                                         font=("Helvetica", 10, "bold"))
        self.month_year_label.pack(side=LEFT, expand=True)
        ttk.Button(cal_nav_frame, text="▶", width=3,
                  command=self.next_month).pack(side=RIGHT)
        ttk.Button(cal_nav_frame, text="Today", width=5,
                  command=self.load_todays_log).pack(side=RIGHT, padx=(5, 0))
        
        # Calendar display
        self.cal_frame = ttk.Frame(calendar_frame)
          # Left pane split vertically: calendar on top, reserved area below
        left_split = ttk.PanedWindow(calendar_frame, orient=VERTICAL)
        left_split.pack(fill=BOTH, expand=True)

        top_half = ttk.Frame(left_split)
        bottom_half = ttk.Frame(left_split)
        left_split.add(top_half, weight=1)
        left_split.add(bottom_half, weight=1)

        # Calendar display (upper part)
        self.cal_frame = ttk.Frame(top_half)
        self.cal_frame.pack(fill=BOTH, expand=True)
        # Reserved lower area (kept empty for now)
        self.left_lower_frame = bottom_half
        
        # Editor frame
        editor_frame = ttk.Frame(paned_window, padding=5)
        paned_window.add(editor_frame, weight=3)
        
        # Date label
        self.date_label = ttk.Label(editor_frame, text="", 
                                   font=("Helvetica", 12, "bold"))
        self.date_label.pack(fill=X, pady=(0, 5))
        
        # Text editor with scrollbar
        editor_container = ttk.Frame(editor_frame)
        editor_container.pack(fill=BOTH, expand=True)
        
        self.text_editor = scrolledtext.ScrolledText(
            editor_container, wrap=tk.WORD, font=("Helvetica", 11), 
            undo=True, maxundo=-1, padx=10, pady=10
        )
        self.text_editor.pack(fill=BOTH, expand=True)
        
        # Status bar
        status_frame = ttk.Frame(main_container, height=25)
        status_frame.pack(fill=X, pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(status_frame, textvariable=self.status_var,
                 font=("Helvetica", 9)).pack(side=LEFT)
        
        # Auto-save indicator
        self.auto_save_var = tk.StringVar(value="Auto-save: ON")
        ttk.Label(status_frame, textvariable=self.auto_save_var,
                 font=("Helvetica", 9)).pack(side=RIGHT)
        
        # Compact, modern calendar styles
        try:
            self.style.configure("CalendarHeader.TLabel", font=("Helvetica", 8, "bold"))
            self.style.configure("Compact.TButton", padding=(4, 1), font=("Helvetica", 9))
        except Exception:
            pass
        
        # Build the calendar
        self.build_calendar()
        
    def build_calendar(self):
        # Clear existing calendar widgets
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
            
        # Set month-year label
        self.month_year_var.set(self.current_date.strftime("%B %Y"))
        
        # Create calendar
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Create day headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            label = ttk.Label(self.cal_frame, text=day, style="CalendarHeader.TLabel",
                             anchor="center", padding=0)
            label.grid(row=0, column=i, sticky="ew", padx=1, pady=1)
            
        # Create day buttons
        for week_idx, week in enumerate(cal):
            for day_idx, day in enumerate(week):
                if day == 0:
                    continue
                    
                btn = ttk.Button(
                    self.cal_frame, 
                    text=str(day), 
                    width=2,
                    style="Compact.TButton",
                    bootstyle="secondary-outline",
                    command=lambda d=day: self.load_log_by_date(d)
                )
                
                # Highlight today
                today = datetime.now()
                if (self.current_date.year == today.year and 
                    self.current_date.month == today.month and 
                    day == today.day):
                    btn.configure(bootstyle="primary")
                
                # Check if log exists for this day
                log_date = datetime(self.current_date.year, self.current_date.month, day)
                if self.log_exists(log_date):
                    btn.configure(bootstyle="success-outline")
                
                btn.grid(row=week_idx+1, column=day_idx, sticky="nsew", padx=1, pady=1)
                
        # Configure grid weights
        for i in range(7):
            self.cal_frame.columnconfigure(i, weight=1)
        for i in range(len(cal) + 1):
            self.cal_frame.rowconfigure(i, weight=1)
            
    def log_exists(self, date):
        month_folder = date.strftime("%B %Y")
        filename = date.strftime("%d-%m-%Y") + ".txt"
        filepath = os.path.join(self.app_data_dir, month_folder, filename)
        return os.path.exists(filepath)
        
    def load_log_by_date(self, day):
        selected_date = datetime(self.current_date.year, self.current_date.month, day)
        self.load_log(selected_date)
        
    def load_todays_log(self):
        self.current_date = datetime.now()
        self.build_calendar()
        self.load_log(self.current_date)
        
    def load_log(self, date):
        # Save current log first if needed
        self.save_log()
        
        # Update current date
        self.current_date = date
        
        # Update date label
        self.date_label.config(text=date.strftime("%A, %d %B %Y"))
        
        # Determine file path - using the correct format
        month_folder = date.strftime("%B %Y")
        filename = date.strftime("%d-%m-%Y") + ".txt"
        filepath = os.path.join(self.app_data_dir, month_folder, filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Load or create file
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = f"# Research Log - {date.strftime('%A, %d %B %Y')}\n\n"
            
        # Update text editor
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(1.0, content)
        
        # Update status
        self.status_var.set(f"Loaded log for {date.strftime('%d %B %Y')}")
        
        # Store current file
        self.current_file = filepath
        
    def save_log(self):
        if not self.current_file:
            return
            
        content = self.text_editor.get(1.0, tk.END)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.current_file), exist_ok=True)
        
        # Save to file
        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_var.set(f"Saved: {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            self.status_var.set(f"Error saving: {str(e)}")
            
        # Update calendar to reflect new log
        self.build_calendar()
        
    def setup_auto_save(self):
        def auto_save():
            self.save_log()
            self.root.after(30000, auto_save)  # Save every 30 seconds
            
        self.root.after(30000, auto_save)
        
    def apply_format(self, format_type):
        if format_type == "bold":
            self.text_editor.insert(tk.INSERT, "**bold text**")
        elif format_type == "italic":
            self.text_editor.insert(tk.INSERT, "*italic text*")
        elif format_type == "bullet":
            self.text_editor.insert(tk.INSERT, "• ")
            
    def toggle_theme(self):
        if self.dark_mode:
            self.style.theme_use("flatly")
            self.theme_btn.config(text="🌙")
            self.dark_mode = False
        else:
            self.style.theme_use("darkly")
            self.theme_btn.config(text="☀️")
            self.dark_mode = True
            
        self.save_settings()
        
    def prev_month(self):
        self.current_date = self.current_date.replace(day=1) - timedelta(days=1)
        self.build_calendar()
        
    def next_month(self):
        next_month = self.current_date.replace(day=28) + timedelta(days=4)
        self.current_date = next_month.replace(day=1)
        self.build_calendar()
        
    def load_settings(self):
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                pass
                
        self.dark_mode = settings.get('dark_mode', True)
        
    def save_settings(self):
        settings = {
            'dark_mode': self.dark_mode
        }
        
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f)
            
    def on_closing(self):
        self.save_log()
        self.save_settings()
        self.root.destroy()

def main():
    root = ttkbs.Window(themename="darkly")
    app = DailyLogManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()