# cpu_scheduler_gui.py
# Defines the graphical user interface for the CPU Scheduler Simulator with a modern design and fixes.

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from ttkbootstrap import Style, Window, Frame, Label, Button, Entry, Checkbutton, Radiobutton, Scrollbar, Toplevel
from ttkbootstrap.tooltip import ToolTip
import random
import json
import logging
from cpu_scheduler_algorithms import *
from cpu_scheduler_visualization import SchedulerVisualizer
from performance_metrics import PerformanceMetrics
from ai_scheduler import AIScheduler

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)

class SchedulerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced CPU Scheduler Simulator")
        self.root.geometry("1400x900")
        self.style = Style(theme="superhero")
        self.style.configure("TButton", font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12))
        self.style.configure("TEntry", font=("Helvetica", 12))
        self.style.configure("TRadiobutton", font=("Helvetica", 12))

        self.processes = []
        self.process_entries = []
        self.step_mode = False
        self.current_step = 0
        self.step_timeline = []
        self.current_processes = []
        self.current_algo_name = "N/A"
        self.timeline = []
        self.num_cores = 1
        self.ai_scheduler = AIScheduler()
        self.drag_index = None

        # Main container
        self.main_frame = Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar for navigation
        self.sidebar = Frame(self.main_frame, width=200, bootstyle="dark")
        self.sidebar.pack(side="left", fill="y", padx=5, pady=5)

        # Theme toggle
        self.theme_var = tk.BooleanVar(value=True)
        Checkbutton(self.sidebar, text="Dark Mode", variable=self.theme_var, command=self.toggle_theme,
                    bootstyle="round-toggle-success").pack(pady=10)

        # Navigation buttons with modern styling
        self.nav_buttons = []
        nav_items = [
            ("Process Management", self.show_process_management),
            ("Scheduling", self.show_scheduling),
            ("Results", self.show_results),
            ("Metrics", self.show_metrics),
            ("About", self.show_about)
        ]
        for text, cmd in nav_items:
            btn = Button(self.sidebar, text=text, command=cmd, bootstyle="outline-light")
            btn.pack(fill="x", pady=5, padx=5)
            self.nav_buttons.append(btn)
            ToolTip(btn, text=f"Go to {text} section")
        self.nav_buttons[0].configure(bootstyle="success")

        # Content area
        self.content_frame = Frame(self.main_frame, bootstyle="dark")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = Label(self.root, textvariable=self.status_var, bootstyle="inverse-dark", font=("Helvetica", 10), anchor="w", padding=5)
        self.status_bar.pack(side="bottom", fill="x")

        # Initialize sections
        self.process_management_frame = Frame(self.content_frame)
        self.scheduling_frame = Frame(self.content_frame)
        self.results_frame = Frame(self.content_frame)
        self.metrics_frame = Frame(self.content_frame)
        self.about_frame = Frame(self.content_frame)

        # Show process management by default
        self.show_process_management()

    def toggle_theme(self):
        theme = "superhero" if self.theme_var.get() else "flatly"
        self.style.theme_use(theme)
        self.status_var.set("Theme changed")

    def highlight_nav_button(self, active_index):
        for i, btn in enumerate(self.nav_buttons):
            btn.configure(bootstyle="outline-light" if i != active_index else "success")

    def show_process_management(self):
        self.clear_content()
        self.process_management_frame.pack(fill="both", expand=True)
        self.build_process_management()
        self.highlight_nav_button(0)
        self.status_var.set("Process Management section loaded")

    def show_scheduling(self):
        self.clear_content()
        self.scheduling_frame.pack(fill="both", expand=True)
        self.build_scheduling()
        self.highlight_nav_button(1)
        self.status_var.set("Scheduling section loaded")

    def show_results(self):
        self.clear_content()
        self.results_frame.pack(fill="both", expand=True)
        self.build_results()
        self.highlight_nav_button(2)
        self.status_var.set("Results section loaded")

    def show_metrics(self):
        self.clear_content()
        self.metrics_frame.pack(fill="both", expand=True)
        self.build_metrics()
        self.highlight_nav_button(3)
        self.status_var.set("Metrics section loaded")

    def show_about(self):
        self.clear_content()
        self.about_frame.pack(fill="both", expand=True)
        self.build_about()
        self.highlight_nav_button(4)
        self.status_var.set("About section loaded")

    def clear_content(self):
        for frame in [self.process_management_frame, self.scheduling_frame, self.results_frame, self.metrics_frame, self.about_frame]:
            frame.pack_forget()

    def build_process_management(self):
        input_frame = ttk.LabelFrame(self.process_management_frame, text="Process Configuration", padding=15, bootstyle="primary")
        input_frame.pack(fill="x", pady=10)

        listbox_frame = Frame(input_frame)
        listbox_frame.pack(fill="both", expand=True, pady=5)
        self.process_listbox = tk.Listbox(listbox_frame, height=10, font=("Helvetica", 12), bg="#2b2b2b", fg="white", selectbackground="#4a4a4a")
        self.process_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(listbox_frame, orient="vertical", command=self.process_listbox.yview, bootstyle="round")
        scrollbar.pack(side="right", fill="y")
        self.process_listbox.configure(yscrollcommand=scrollbar.set)
        self.process_listbox.bind("<B1-Motion>", self.on_drag)
        self.process_listbox.bind("<ButtonRelease-1>", self.on_drop)

        input_subframe = Frame(input_frame, padding=10)
        input_subframe.pack(fill="x", pady=10)

        headers = ["PID", "Arrival", "Burst", "Priority"]
        self.new_process_entries = []
        for i, header in enumerate(headers):
            Label(input_subframe, text=header, font=("Helvetica", 12, "bold"), bootstyle="light").grid(row=0, column=i, padx=15, pady=5)
            entry = Entry(input_subframe, width=10, bootstyle="secondary")
            entry.grid(row=1, column=i, padx=15, pady=5)
            entry.insert(0, "0" if header != "PID" else f"P{len(self.processes) + 1}")
            self.new_process_entries.append(entry)

        button_frame = Frame(input_frame)
        button_frame.pack(pady=10)
        btn_configs = [
            ("Add Process", self.add_process, "success", "Add a new process"),
            ("Random Processes", self.add_random_processes, "info", "Generate random processes"),
            ("Clear All", self.clear_all, "danger", "Clear all processes"),
            ("Save Config", self.save_config, "warning", "Save process configuration"),
            ("Load Config", self.load_config, "warning", "Load process configuration")
        ]
        for text, cmd, style, tooltip in btn_configs:
            btn = Button(button_frame, text=text, command=cmd, bootstyle=style)
            btn.pack(side="left", padx=5)
            ToolTip(btn, text=tooltip)

    def on_drag(self, event):
        self.process_listbox.selection_clear(0, tk.END)
        index = self.process_listbox.nearest(event.y)
        self.process_listbox.selection_set(index)
        self.drag_index = index

    def on_drop(self, event):
        index = self.process_listbox.nearest(event.y)
        if self.drag_index is not None and index != self.drag_index:
            item = self.processes.pop(self.drag_index)
            self.processes.insert(index, item)
            self.update_process_listbox()
        self.drag_index = None

    def update_process_listbox(self):
        self.process_listbox.delete(0, tk.END)
        for p in self.processes:
            self.process_listbox.insert(tk.END, f"{p.pid}: Arrival={p.arrival_time}, Burst={p.burst_time}, Priority={p.priority}")
        self.status_var.set(f"Updated process list: {len(self.processes)} processes")

    def add_process(self):
        try:
            pid = self.new_process_entries[0].get()
            arrival = int(self.new_process_entries[1].get())
            burst = int(self.new_process_entries[2].get())
            priority = int(self.new_process_entries[3].get())
            if arrival < 0 or burst <= 0:
                raise ValueError("Arrival must be >= 0, Burst must be > 0")
            process = Process(pid, arrival, burst, priority)
            self.processes.append(process)
            self.update_process_listbox()
            self.new_process_entries[0].delete(0, tk.END)
            self.new_process_entries[0].insert(0, f"P{len(self.processes) + 1}")
            self.status_var.set(f"Added process {pid}")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            self.status_var.set("Error adding process")

    def add_random_processes(self):
        num_processes = random.randint(3, 10)
        for _ in range(num_processes):
            pid = f"P{len(self.processes) + 1}"
            arrival = random.randint(0, 10)
            burst = random.randint(1, 10)
            priority = random.randint(0, 5)
            self.processes.append(Process(pid, arrival, burst, priority))
        self.update_process_listbox()
        self.status_var.set(f"Added {num_processes} random processes")

    def clear_all(self):
        self.processes.clear()
        self.update_process_listbox()
        self.status_var.set("Cleared all processes")

    def save_config(self):
        config = [{"pid": p.pid, "arrival": p.arrival_time, "burst": p.burst_time, "priority": p.priority} 
                  for p in self.processes]
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(config, f)
            self.status_var.set(f"Saved configuration to {file}")

    def load_config(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file:
            with open(file, "r") as f:
                config = json.load(f)
            self.processes.clear()
            for proc in config:
                self.processes.append(Process(proc["pid"], proc["arrival"], proc["burst"], proc["priority"]))
            self.update_process_listbox()
            self.status_var.set(f"Loaded configuration from {file}")

    def build_scheduling(self):
        algo_frame = ttk.LabelFrame(self.scheduling_frame, text="Algorithm & Settings", padding=15, bootstyle="primary")
        algo_frame.pack(fill="x", pady=10)

        self.algo_var = tk.StringVar(value="Intelligent")
        algos = [
            ("FCFS", "FCFS"), ("SJF (NP)", "SJF-NP"), ("SJF (P)", "SJF-P"),
            ("Round Robin", "RR"), ("Priority (NP)", "PR-NP"), ("Priority (P)", "PR-P"),
            ("MLFQ", "MLFQ"), ("Intelligent", "Intelligent"), ("Custom", "Custom")
        ]
        algo_subframe = Frame(algo_frame)
        algo_subframe.pack(fill="x", pady=5)
        for i, (text, value) in enumerate(algos):
            btn = Radiobutton(algo_subframe, text=text, variable=self.algo_var, value=value, bootstyle="info-toolbutton")
            btn.grid(row=0, column=i, padx=10, pady=5)
            ToolTip(btn, text=f"Select {text} algorithm")

        settings_frame = Frame(algo_frame)
        settings_frame.pack(fill="x", pady=10)

        Label(settings_frame, text="Quantum:", font=("Helvetica", 12), bootstyle="light").grid(row=0, column=0, padx=15)
        self.quantum_var = tk.StringVar(value="2")
        Entry(settings_frame, textvariable=self.quantum_var, width=5, bootstyle="secondary").grid(row=0, column=1, padx=15)

        Label(settings_frame, text="Number of Cores:", font=("Helvetica", 12), bootstyle="light").grid(row=0, column=2, padx=15)
        self.cores_var = tk.StringVar(value="1")
        Entry(settings_frame, textvariable=self.cores_var, width=5, bootstyle="secondary").grid(row=0, column=3, padx=15)

        self.custom_algo_frame = Frame(algo_frame)
        self.custom_algo_frame.pack(fill="x", pady=10)
        Label(self.custom_algo_frame, text="Custom Algorithm (Python Code):", font=("Helvetica", 12), bootstyle="light").pack(anchor="w")
        self.custom_algo_text = tk.Text(self.custom_algo_frame, height=5, width=50, font=("Helvetica", 12), bg="#2b2b2b", fg="white")
        self.custom_algo_text.pack(fill="x", pady=5)
        self.custom_algo_text.insert(tk.END, "# Define your custom scheduling algorithm here\ndef custom_scheduler(processes, quantum):\n    return processes, 'Custom', []")
        ToolTip(self.custom_algo_text, text="Enter a custom scheduling algorithm in Python")

        # Add a "Test Code" button for custom algorithm
        test_code_btn = Button(self.custom_algo_frame, text="Test Code", command=self.test_custom_code, bootstyle="warning")
        test_code_btn.pack(anchor="e", pady=5)
        ToolTip(test_code_btn, text="Test the custom algorithm code for syntax errors")

        control_frame = Frame(algo_frame)
        control_frame.pack(pady=10)
        btn_configs = [
            ("Run Simulation ▶", self.run_simulation, "success", "Run the simulation with the selected algorithm"),
            ("Step Simulation", self.start_step_mode, "info", "Run the simulation step-by-step"),
            ("View Gantt", self.view_gantt, "primary", "View the Gantt chart of the simulation")
        ]
        for text, cmd, style, tooltip in btn_configs:
            btn = Button(control_frame, text=text, command=cmd, bootstyle=style)
            btn.pack(side="left", padx=5)
            ToolTip(btn, text=tooltip)

    def test_custom_code(self):
        try:
            custom_code = self.custom_algo_text.get("1.0", tk.END)
            local_vars = {"processes": [], "quantum": 2}
            exec(custom_code, globals(), local_vars)
            if "custom_scheduler" not in local_vars:
                raise ValueError("Custom algorithm must define a 'custom_scheduler' function")
            messagebox.showinfo("Success", "Custom algorithm code is valid!")
            self.status_var.set("Custom algorithm code validated")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid custom algorithm code: {str(e)}")
            self.status_var.set("Custom algorithm code validation failed")

    def run_simulation(self):
        if not self.processes:
            if not messagebox.askyesno("Warning", "No processes added. Do you want to add random processes and continue?"):
                self.status_var.set("Simulation cancelled: No processes")
                return
            self.add_random_processes()

        # Show loading indicator
        loading_window = Toplevel(self.root)
        loading_window.title("Running Simulation")
        loading_window.geometry("300x100")
        loading_window.transient(self.root)
        loading_window.grab_set()
        Label(loading_window, text="Running simulation, please wait...", font=("Helvetica", 12), bootstyle="light").pack(pady=20)
        self.root.update()

        try:
            self.status_var.set("Running simulation...")
            self.num_cores = int(self.cores_var.get())
            if self.num_cores < 1:
                raise ValueError("Number of cores must be at least 1")
            algo = self.algo_var.get()
            quantum = int(self.quantum_var.get())
            if algo == "Custom":
                custom_code = self.custom_algo_text.get("1.0", tk.END)
                processes, algo_name, timeline = self.run_custom_algorithm(custom_code, self.processes[:], quantum)
            elif algo == "Intelligent":
                predicted_algo = self.ai_scheduler.predict_best_algorithm(self.processes)
                processes, algo_name, timeline = self.run_algorithm(predicted_algo, self.processes[:], quantum)
                algo_name = f"Intelligent ({predicted_algo})"
            else:
                processes, algo_name, timeline = self.run_algorithm(algo, self.processes[:], quantum)
            self.current_processes = processes
            self.current_algo_name = algo_name
            self.timeline = timeline
            avg_wait, avg_turn, cpu_util, throughput = calculate_metrics(processes)
            
            # Ensure the Results section is built before displaying results
            self.show_results()
            self.display_results(processes, algo_name, avg_wait, avg_turn, cpu_util, throughput)
            self.status_var.set("Simulation completed")
        except Exception as e:
            messagebox.showerror("Error", f"Simulation failed: {str(e)}")
            self.status_var.set("Simulation failed")
        finally:
            loading_window.destroy()

    def run_algorithm(self, algo, processes, quantum):
        if algo == "FCFS":
            return multi_core_scheduler(processes, self.num_cores, fcfs_scheduler)
        elif algo == "SJF-NP":
            return multi_core_scheduler(processes, self.num_cores, sjf_non_preemptive)
        elif algo == "SJF-P":
            return multi_core_scheduler(processes, self.num_cores, sjf_preemptive)
        elif algo == "RR":
            return multi_core_scheduler(processes, self.num_cores, lambda p: rr_scheduler(p, quantum))
        elif algo == "PR-NP":
            return multi_core_scheduler(processes, self.num_cores, priority_non_preemptive)
        elif algo == "PR-P":
            return multi_core_scheduler(processes, self.num_cores, priority_preemptive)
        elif algo == "MLFQ":
            return multi_core_scheduler(processes, self.num_cores, lambda p: mlfq_scheduler(p, [quantum, quantum * 2, quantum * 4]))
        else:
            return multi_core_scheduler(processes, self.num_cores, lambda p: intelligent_scheduler(p, quantum))

    def run_custom_algorithm(self, code, processes, quantum):
        local_vars = {"processes": processes, "quantum": quantum}
        exec(code, globals(), local_vars)
        return local_vars.get("custom_scheduler", lambda p, q: (p, "Custom", []))(processes, quantum)

    def start_step_mode(self):
        if not self.processes:
            if not messagebox.askyesno("Warning", "No processes added. Do you want to add random processes and continue?"):
                self.status_var.set("Step mode cancelled: No processes")
                return
            self.add_random_processes()

        try:
            self.status_var.set("Starting step mode...")
            self.num_cores = int(self.cores_var.get())
            algo = self.algo_var.get()
            quantum = int(self.quantum_var.get())
            if algo == "Custom":
                custom_code = self.custom_algo_text.get("1.0", tk.END)
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_custom_algorithm(custom_code, self.processes[:], quantum)
            elif algo == "Intelligent":
                predicted_algo = self.ai_scheduler.predict_best_algorithm(self.processes)
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_algorithm(predicted_algo, self.processes[:], quantum)
                self.current_algo_name = f"Intelligent ({predicted_algo})"
            else:
                self.step_processes, self.current_algo_name, self.step_timeline = self.run_algorithm(algo, self.processes[:], quantum)
            self.step_mode = True
            self.current_step = 0
            self.timeline = self.step_timeline
            self.show_results()  # Ensure Results section is built
            self.step_simulation()
            self.status_var.set("Step mode started")
        except Exception as e:
            messagebox.showerror("Error", f"Step mode failed: {str(e)}")
            self.status_var.set("Step mode failed")

    def step_simulation(self):
        if not self.step_mode or self.current_step >= len(self.step_timeline):
            self.step_mode = False
            self.display_results(self.step_processes, self.current_algo_name, *calculate_metrics(self.step_processes))
            self.status_var.set("Step mode completed")
            return
        self.current_step += 1
        self.timeline = self.step_timeline[:self.current_step]
        self.display_results(self.step_processes, self.current_algo_name, *calculate_metrics(self.step_processes))
        self.status_var.set(f"Step {self.current_step} of {len(self.step_timeline)}")

    def build_results(self):
        # Clear any existing widgets in the results frame
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        result_frame = ttk.LabelFrame(self.results_frame, text="Simulation Results", padding=15, bootstyle="primary")
        result_frame.pack(fill="both", expand=True, pady=10)

        self.algo_label = Label(result_frame, text="Algorithm: N/A", font=("Helvetica", 14, "bold"), bootstyle="success")
        self.algo_label.pack(anchor="w", pady=5)

        self.wait_label = Label(result_frame, text="Avg Waiting Time: N/A", font=("Helvetica", 12), bootstyle="light")
        self.wait_label.pack(anchor="w", padx=15, pady=5)

        self.turn_label = Label(result_frame, text="Avg Turnaround Time: N/A", font=("Helvetica", 12), bootstyle="light")
        self.turn_label.pack(anchor="w", padx=15, pady=5)

        self.cpu_label = Label(result_frame, text="CPU Utilization: N/A", font=("Helvetica", 12), bootstyle="light")
        self.cpu_label.pack(anchor="w", padx=15, pady=5)

        self.throughput_label = Label(result_frame, text="Throughput: N/A", font=("Helvetica", 12), bootstyle="light")
        self.throughput_label.pack(anchor="w", padx=15, pady=5)

        self.result_tree = ttk.Treeview(result_frame, columns=("PID", "Start", "End", "Waiting", "Turnaround"), show="headings", height=10)
        for col in ("PID", "Start", "End", "Waiting", "Turnaround"):
            self.result_tree.heading(col, text=col)
            self.result_tree.column(col, width=120, anchor="center")
        self.result_tree.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview, bootstyle="round")
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def display_results(self, processes, algo_name, avg_wait, avg_turn, cpu_util, throughput):
        # Ensure the Results section is built
        if not hasattr(self, 'algo_label'):
            self.show_results()

        self.algo_label.config(text=f"Algorithm: {algo_name}")
        self.wait_label.config(text=f"Avg Waiting Time: {avg_wait:.2f}")
        self.turn_label.config(text=f"Avg Turnaround Time: {avg_turn:.2f}")
        self.cpu_label.config(text=f"CPU Utilization: {cpu_util:.2f}%")
        self.throughput_label.config(text=f"Throughput: {throughput:.4f}")

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for i, p in enumerate(processes):
            start = p.start_time if p.start_time is not None else "N/A"
            self.result_tree.insert("", "end", values=(p.pid, start, p.end_time, p.waiting_time, p.turnaround_time))
        self.status_var.set("Results updated")

    def view_gantt(self):
        if not self.timeline:
            messagebox.showwarning("Warning", "No timeline available for Gantt chart. Please run a simulation first.")
            self.status_var.set("No timeline available")
            return
        visualizer = SchedulerVisualizer()
        visualizer.display_gantt_chart(self.current_algo_name, self.current_processes, self.timeline)
        self.status_var.set("Gantt chart opened")

    def build_metrics(self):
        for widget in self.metrics_frame.winfo_children():
            widget.destroy()

        metrics_frame = ttk.LabelFrame(self.metrics_frame, text="Performance Metrics", padding=15, bootstyle="primary")
        metrics_frame.pack(fill="both", expand=True, pady=10)

        if self.current_processes:
            PerformanceMetrics(self.current_processes, metrics_frame)
            self.status_var.set("Metrics displayed")
        else:
            Label(metrics_frame, text="No metrics available. Run a simulation first.", font=("Helvetica", 12), bootstyle="warning").pack(pady=20)
            self.status_var.set("No metrics available")

    def build_about(self):
        for widget in self.about_frame.winfo_children():
            widget.destroy()

        about_frame = ttk.LabelFrame(self.about_frame, text="About", padding=15, bootstyle="primary")
        about_frame.pack(fill="both", expand=True, pady=10)

        Label(about_frame, text="Enhanced CPU Scheduler Simulator", font=("Helvetica", 16, "bold"), bootstyle="success").pack(anchor="w", pady=5)
        Label(about_frame, text="Version: 1.0", font=("Helvetica", 12), bootstyle="light").pack(anchor="w", pady=5)
        Label(about_frame, text="Developed by: xAI Team", font=("Helvetica", 12), bootstyle="light").pack(anchor="w", pady=5)
        Label(about_frame, text="This application simulates various CPU scheduling algorithms with a modern GUI.", font=("Helvetica", 12), bootstyle="light").pack(anchor="w", pady=5)
        Label(about_frame, text="Features:\n- Multiple scheduling algorithms\n- Multi-core support\n- Gantt chart visualization\n- Performance metrics\n- Custom algorithm support", font=("Helvetica", 12), bootstyle="light").pack(anchor="w", pady=5)
