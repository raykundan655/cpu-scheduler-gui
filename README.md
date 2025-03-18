# Intelligent CPU Scheduler Simulator (GUI)

## Overview
This project is a graphical user interface (GUI) for simulating various CPU scheduling algorithms. It allows users to input processes, choose a scheduling algorithm, and visualize the results.

## Features
- Add and remove processes dynamically.
- Supports multiple scheduling algorithms:
  - First Come First Serve (FCFS)
  - Shortest Job First (SJF) - Non-Preemptive & Preemptive
  - Round Robin (RR) with configurable quantum
  - Priority Scheduling - Non-Preemptive & Preemptive
  - Intelligent scheduling (custom algorithm)
- Handles process dependencies for advanced scheduling scenarios.
- Real-time input validation.
- Displays key performance metrics:
  - Average Waiting Time
  - Average Turnaround Time
  - CPU Utilization
  - Throughput
- Interactive Gantt charts with hover tooltips showing process details.
- Animated Gantt charts for real-time scheduling visualization.
- UI theme customization with multiple theme options.
- Export results as CSV files for further analysis.

## Contributors
- **Gaurav Tiwari**: Developed and optimized the scheduling algorithms.
- **Kundan Kr Ray**: Built the interactive GUI with usability enhancements.
- **Harshit Kumar Verma**: Added visualization capabilities, including Gantt charts and comparisons.

## Installation
### Prerequisites
- Python 3.x
- Required Python packages:
  ```sh
  pip install tkinter ttkthemes matplotlib mplcursors numpy pandas
  ```

## Usage
1. Run the application:
   ```sh
   python gui_scheduler.py
   ```
2. Add processes by entering values for Process ID, Arrival Time, Burst Time, and Priority.
3. Select a scheduling algorithm from the available options.
4. (Optional) If using Round Robin, set the time quantum.
5. Click `Run Simulation` to execute the algorithm and display results.
6. Visualize schedules using static and animated Gantt charts.
7. Compare algorithm performance across multiple metrics.
8. Export results using the `Export Results` button.
9. Reset the inputs using `Reset` if needed.
10. Change the UI theme using the dropdown menu.

## File Structure
- `gui_scheduler.py` - Main GUI implementation.
- `scheduler_algorithms.py` - Implementation of scheduling algorithms.
- `scheduler_visualization.py` - Visualization module for Gantt charts and comparisons.
- `config.py` - Configuration constants.

## Shortcuts
- `Ctrl + R`: Run simulation.
- `Ctrl + G`: Display Gantt chart.

## Notes
- This GUI provides an interactive way to visualize CPU scheduling algorithms.
- Ensure valid inputs: Arrival time ≥ 0, Burst time > 0.
- Future enhancements may include performance optimizations for large process sets and dynamic theme updates for all widgets.

## License
This is Project 

## Acknowledgements
- **Gaurav Tiwari**: Core algorithms in `scheduler_algorithms.py`.
- **Harshit Kumar Verma**: Visualizations in `scheduler_visualization.py`.
- **Kundan Kr Ray**: GUI interface.

