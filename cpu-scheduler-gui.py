import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from typing import List
from scheduler_algorithms import Process, Algorithm, calculate_metrics
import config  # Assuming a config.py file with constants

class SchedulerGUI:
    """A graphical user interface for simulating CPU scheduling algorithms."""
    
    def __init__(self, root):
        """Initialize the SchedulerGUI with a themed Tkinter root window."""
        self.root = root
        self.root.title("Intelligent CPU Scheduler Simulator")
        self.root.geometry(config.WINDOW_SIZE)
        self.processes: List[Process] = []
        self.process_entries = []
        self.current_theme = config.DEFAULT_THEME
        self.current_processes = []
        self.current_algo_name = "N/A"
        self.timeline = []
        
        self.root.set_theme(self.current_theme)
        main_frame = tk.Frame(root, bg=config.LIGHT_BG)
        main_frame.pack(fill="both", expand=True)
        
        # Input Frame with Scrollable Canvas
        input_frame = ttk.LabelFrame(main_frame, text="Process Configuration", padding=15)
        input_frame.pack(fill="x", pady=10, padx=10)
        
        self.canvas = tk.Canvas(input_frame, height=250, bg=config.LIGHT_BG)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        headers = ["PID", "Arrival", "Burst", "Priority", "Actions"]
        for i, header in enumerate(headers):
            label = ttk.Label(self.scrollable_frame, text=header, font=("Helvetica", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=5)
            self.add_tooltip(label, f"Enter {header.lower()} for each process")
        
        self.add_process_row()
        
        ttk.Button(input_frame, text="Add Process", command=self.add_process_row).pack(pady=10)
        
        # Algorithm and Settings Frame
        algo_frame = ttk.LabelFrame(main_frame, text="Algorithm & Settings", padding=15)
        algo_frame.pack(fill="x", pady=10, padx=10)
        self.algo_var = tk.StringVar(value="Intelligent")
        algos = [
            (algo.value, algo.name) for algo in Algorithm  # Map enum to display name and value
        ]
        for i, (text, value) in enumerate(algos):
            rb = ttk.Radiobutton(algo_frame, text=text, variable=self.algo_var, value=value)
            rb.grid(row=0, column=i, padx=10, pady=5)
            self.add_tooltip(rb, f"Select {text} scheduling algorithm")
        
        ttk.Label(algo_frame, text="RR Quantum:").grid(row=1, column=0, padx=10, pady=5)
        self.quantum_var = tk.StringVar(value=str(config.DEFAULT_QUANTUM))
        quantum_entry = ttk.Entry(algo_frame, textvariable=self.quantum_var, width=5)
        quantum_entry.grid(row=1, column=1, padx=10, pady=5)
        self.add_tooltip(quantum_entry, "Set quantum for Round Robin (default: 2)")
        
        ttk.Label(algo_frame, text="Theme:").grid(row=1, column=4, padx=10, pady=5)
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_menu = ttk.OptionMenu(algo_frame, self.theme_var, self.current_theme, *config.THEMES, command=self.change_theme)
        theme_menu.grid(row=1, column=5, padx=10, pady=5)
        self.add_tooltip(theme_menu, "Select UI theme (e.g., 'equilux' for dark mode)")
        
        # Control Frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(pady=15, padx=10)
        buttons = [
            ("Run Simulation", self.run_simulation, "Run the selected scheduling algorithm"),
            ("Reset", self.reset, "Reset all inputs and results"),
            ("Help", self.show_help, "Display help information")
        ]
        for text, cmd, tip in buttons:
            btn = ttk.Button(control_frame, text=text, command=cmd)
            btn.pack(side="left", padx=10)
            self.add_tooltip(btn, tip)
        
        # Result Frame
        self.result_frame = ttk.LabelFrame(main_frame, text="Simulation Results", padding=15)
        self.result_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        self.summary_frame = ttk.Frame(self.result_frame)
        self.summary_frame.pack(fill="x", pady=5)
        
        self.algo_label = ttk.Label(self.summary_frame, text="Algorithm: N/A", font=("Helvetica", 12, "bold"))
        self.algo_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        
        self.wait_label = ttk.Label(self.summary_frame, text="Avg Waiting Time: N/A", font=("Helvetica", 11))
        self.wait_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        
        self.turn_label = ttk.Label(self.summary_frame, text="Avg Turnaround Time: N/A", font=("Helvetica", 11))
        self.turn_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        self.cpu_label = ttk.Label(self.summary_frame, text="CPU Utilization: N/A", font=("Helvetica", 11))
        self.cpu_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)
        
        self.throughput_label = ttk.Label(self.summary_frame, text="Throughput: N/A", font=("Helvetica", 11))
        self.throughput_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        self.result_tree = ttk.Treeview(self.result_frame, columns=("PID", "Start", "End", "Waiting", "Turnaround"),
                                        show="headings", height=10)
        self.result_tree.heading("PID", text="PID")
        self.result_tree.heading("Start", text="Start Time")
        self.result_tree.heading("End", text="End Time")
        self.result_tree.heading("Waiting", text="Waiting Time")
        self.result_tree.heading("Turnaround", text="Turnaround Time")
        
        self.result_tree.column("PID", width=100, anchor="center")
        self.result_tree.column("Start", width=100, anchor="center")
        self.result_tree.column("End", width=100, anchor="center")
        self.result_tree.column("Waiting", width=100, anchor="center")
        self.result_tree.column("Turnaround", width=100, anchor="center")
        
        self.result_tree.pack(fill="both", expand=True, padx=10, pady=5)
        scrollbar = ttk.Scrollbar(self.result_frame, orient="vertical", command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def add_process_row(self):
        """Add a new row for process input with real-time validation."""
        row = len(self.process_entries) + 1
        pid_entry = ttk.Entry(self.scrollable_frame, width=10)
        arrival_entry = ttk.Entry(self.scrollable_frame, width=10)
        burst_entry = ttk.Entry(self.scrollable_frame, width=10)
        priority_entry = ttk.Entry(self.scrollable_frame, width=10)
        
        # Real-time validation
        vcmd_arrival = (self.root.register(lambda p, f="arrival": self.validate_entry(p, f)), '%P')
        vcmd_burst = (self.root.register(lambda p, f="burst": self.validate_entry(p, f)), '%P')
        vcmd_priority = (self.root.register(lambda p, f="priority": self.validate_entry(p, f)), '%P')
        
        pid_entry.insert(0, f"P{row}")
        arrival_entry.insert(0, "0")
        burst_entry.insert(0, "0")
        priority_entry.insert(0, "0")
        
        pid_entry.grid(row=row, column=0, padx=10, pady=5)
        arrival_entry.grid(row=row, column=1, padx=10, pady=5)
        burst_entry.grid(row=row, column=2, padx=10, pady=5)
        priority_entry.grid(row=row, column=3, padx=10, pady=5)
        
        arrival_entry.config(validate="key", validatecommand=vcmd_arrival)
        burst_entry.config(validate="key", validatecommand=vcmd_burst)
        priority_entry.config(validate="key", validatecommand=vcmd_priority)
        
        remove_btn = ttk.Button(self.scrollable_frame, text="Remove", command=lambda: self.remove_process_row(row-1))
        remove_btn.grid(row=row, column=4, padx=10, pady=5)
        self.add_tooltip(remove_btn, "Remove this process")
        
        self.process_entries.append((pid_entry, arrival_entry, burst_entry, priority_entry, remove_btn))
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_process_row(self, index):
        """Remove a process row from the input configuration."""
        if len(self.process_entries) > 1:
            for widget in self.process_entries.pop(index):
                widget.destroy()
            for i, (pid_e, *_) in enumerate(self.process_entries):
                pid_e.delete(0, tk.END)
                pid_e.insert(0, f"P{i+1}")
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def validate_entry(self, value, field):
        """Validate entry input in real-time."""
        if not value:
            return True
        try:
            val = int(value)
            if field == "burst" and val <= 0:
                return False
            if field in ["arrival", "priority"] and val < 0:
                return False
            return True
        except ValueError:
            return False

    def get_processes(self):
        """Retrieve and validate process data from input fields."""
        self.processes.clear()
        for pid_entry, arrival_entry, burst_entry, priority_entry, _ in self.process_entries:
            pid = pid_entry.get()
            try:
                arrival = int(arrival_entry.get())
                burst = int(burst_entry.get())
                priority = int(priority_entry.get())
                if arrival < 0 or burst <= 0:
                    raise ValueError("Arrival >= 0, Burst > 0")
                self.processes.append(Process(pid, arrival, burst, priority))
            except ValueError as e:
                raise ValueError(f"Invalid input for {pid}: {str(e)}")

    def run_simulation(self):
        """Run the selected scheduling algorithm and display results."""
        try:
            self.get_processes()
            algo = self.algo_var.get()
            quantum = int(self.quantum_var.get())
            algo_map = {
                "FCFS": lambda p: fcfs_scheduler(p),
                "SJF-NP": lambda p: sjf_non_preemptive(p),
                "SJF-P": lambda p: sjf_preemptive(p),
                "RR": lambda p: rr_scheduler(p, quantum),
                "PR-NP": lambda p: priority_non_preemptive(p),
                "PR-P": lambda p: priority_preemptive(p),
                "INTELLIGENT": lambda p: intelligent_scheduler(p, quantum)
            }
            if algo not in algo_map:
                raise ValueError(f"Unknown algorithm: {algo}")
            
            processes, algo_name, timeline = algo_map[algo](self.processes[:])
            self.timeline = timeline
            self.current_processes = processes
            self.current_algo_name = algo_name
            avg_wait, avg_turn, cpu_util, throughput = calculate_metrics(processes)
            self.display_results(processes, algo_name, avg_wait, avg_turn, cpu_util, throughput)
        
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def display_results(self, processes, algo_name, avg_wait, avg_turn, cpu_util, throughput):
        """Display simulation results in the GUI."""
        bg_color = config.DARK_BG if self.current_theme == "equilux" else config.LIGHT_BG
        fg_color = "white" if self.current_theme == "equilux" else "black"
        
        self.algo_label.config(text=f"Algorithm: {algo_name}", foreground=fg_color)
        self.wait_label.config(text=f"Avg Waiting Time: {avg_wait:.2f}", foreground=fg_color)
        self.turn_label.config(text=f"Avg Turnaround Time: {avg_turn:.2f}", foreground=fg_color)
        self.cpu_label.config(text=f"CPU Utilization: {cpu_util:.2f}%", foreground=fg_color)
        self.throughput_label.config(text=f"Throughput: {throughput:.4f} processes/unit time", foreground=fg_color)
        
        style = ttk.Style()
        style.configure("Custom.TFrame", background=bg_color)
        self.summary_frame.config(style="Custom.TFrame")
        
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for p in processes:
            self.result_tree.insert("", "end", values=(p.pid, p.start_time, p.end_time, p.waiting_time, p.turnaround_time))

    def reset(self):
        """Reset all inputs and results to default state."""
        while len(self.process_entries) > 1:
            self.remove_process_row(0)
        pid_entry, arrival_entry, burst_entry, priority_entry, _ = self.process_entries[0]
        arrival_entry.delete(0, tk.END)
        burst_entry.delete(0, tk.END)
        priority_entry.delete(0, tk.END)
        arrival_entry.insert(0, "0")
        burst_entry.insert(0, "0")
        priority_entry.insert(0, "0")
        self.display_results([], "N/A", 0, 0, 0, 0)
        self.processes.clear()
        self.timeline = []
        self.current_processes = []
        self.current_algo_name = "N/A"

    def change_theme(self, theme):
        """Change the GUI theme and update widget colors."""
        if theme != self.current_theme:
            self.root.set_theme(theme)
            self.current_theme = theme
            bg_color = config.DARK_BG if theme == "equilux" else config.LIGHT_BG
            fg_color = "white" if theme == "equilux" else "black"
            for widget in self.root.winfo_children():
                if isinstance(widget, tk.Frame) or isinstance(widget, tk.Canvas):
                    widget.configure(bg=bg_color)
            self.canvas.configure(bg=bg_color)
            self.display_results(self.current_processes, self.current_algo_name,
                               *calculate_metrics(self.current_processes) if self.current_processes else (0, 0, 0, 0))

    def add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        def enter(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{widget.winfo_rootx() + 10}+{widget.winfo_rooty() + 20}")
            label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1, font=("Helvetica", 9))
            label.pack(padx=5, pady=2)
            widget.tooltip = tooltip
        
        def leave(event):
            if hasattr(widget, 'tooltip') and widget.tooltip:
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def show_help(self):
        """Display a help window with usage instructions."""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("400x300")
        help_text = """
        **CPU Scheduler Simulator Help**
        - Add processes with PID, Arrival Time, Burst Time, and Priority.
        - Use 'Add Process' to include more processes.
        - Select an algorithm (e.g., FCFS, SJF, RR) and set RR quantum if needed.
        - Click 'Run Simulation' to see results.
        - Use 'Reset' to clear inputs and results.
        - Change themes via the Theme dropdown.
        - All times must be non-negative, with Burst Time > 0.
        """
        ttk.Label(help_window, text=help_text, justify="left", wraplength=380).pack(padx=10, pady=10)

if __name__ == "__main__":
    root = ThemedTk(theme=config.DEFAULT_THEME)
    app = SchedulerGUI(root)
    root.bind("<Control-r>", lambda e: app.run_simulation())
    root.bind("<Control-g>", lambda e: print("Gantt chart not implemented here; use visualization module"))
    root.mainloop()
