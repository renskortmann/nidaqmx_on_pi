"""Tkinter GUI for nidaqmx API exploration and testing."""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
import threading
from typing import Optional, List, Dict, Any


class NidaqmxGUI:
    """Main GUI application for nidaqmx control and exploration."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("nidaqmx API Explorer")
        self.root.geometry("800x600")
        
        self.current_task: Optional[nidaqmx.Task] = None
        self.acquisition_running = False
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the main GUI layout."""
        # Main frame with notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Device & System Info
        system_frame = ttk.Frame(notebook)
        notebook.add(system_frame, text="System")
        self._create_system_tab(system_frame)
        
        # Tab 2: Task Management
        task_frame = ttk.Frame(notebook)
        notebook.add(task_frame, text="Task Management")
        self._create_task_tab(task_frame)
        
        # Tab 3: Channels
        channel_frame = ttk.Frame(notebook)
        notebook.add(channel_frame, text="Channels")
        self._create_channel_tab(channel_frame)
        
        # Tab 4: Data Acquisition
        acq_frame = ttk.Frame(notebook)
        notebook.add(acq_frame, text="Acquisition")
        self._create_acquisition_tab(acq_frame)
        
        # Tab 5: Log
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Log")
        self._create_log_tab(log_frame)
    
    def _create_system_tab(self, parent: ttk.Frame) -> None:
        """System information tab."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="List Devices", command=self._list_devices).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="List Channels", command=self._list_channels).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="List Tasks", command=self._list_tasks).pack(side=tk.LEFT, padx=5)
        
        # Output area
        self.system_output = scrolledtext.ScrolledText(parent, height=20, width=80, state=tk.DISABLED)
        self.system_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_task_tab(self, parent: ttk.Frame) -> None:
        """Task management tab."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Create Task", command=self._create_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close Task", command=self._close_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Task Status", command=self._task_status).pack(side=tk.LEFT, padx=5)
        
        # Task status display
        self.task_output = scrolledtext.ScrolledText(parent, height=20, width=80, state=tk.DISABLED)
        self.task_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_channel_tab(self, parent: ttk.Frame) -> None:
        """Channel creation tab."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add AI Voltage Channel", command=self._add_ai_voltage).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add AO Voltage Channel", command=self._add_ao_voltage).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add DI Channel", command=self._add_di_channel).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Add DO Channel", command=self._add_do_channel).pack(side=tk.LEFT, padx=5)
        
        self.channel_output = scrolledtext.ScrolledText(parent, height=20, width=80, state=tk.DISABLED)
        self.channel_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_acquisition_tab(self, parent: ttk.Frame) -> None:
        """Data acquisition tab."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Configure Timing", command=self._configure_timing).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Start Task", command=self._start_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop Task", command=self._stop_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Read Samples", command=self._read_samples).pack(side=tk.LEFT, padx=5)
        
        self.acq_output = scrolledtext.ScrolledText(parent, height=20, width=80, state=tk.DISABLED)
        self.acq_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_log_tab(self, parent: ttk.Frame) -> None:
        """Log display tab."""
        self.log_output = scrolledtext.ScrolledText(parent, height=25, width=80, state=tk.DISABLED)
        self.log_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _log(self, message: str) -> None:
        """Append message to log."""
        self.log_output.config(state=tk.NORMAL)
        self.log_output.insert(tk.END, message + "\n")
        self.log_output.see(tk.END)
        self.log_output.config(state=tk.DISABLED)
    
    def _output(self, widget: scrolledtext.ScrolledText, message: str) -> None:
        """Write to a scrolled text widget."""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, message)
        widget.config(state=tk.DISABLED)
    
    # System functions
    def _select_device_name(self) -> str:
        """Prompt user to select a device name from available devices."""
        try:
            devices = nidaqmx.system.System.local().devices
            device_names = [device.name for device in devices]
            
            if not device_names:
                messagebox.showwarning("Warning", "No devices found.")
                return ""
            
            # Create a simple dialog with dropdown
            dialog = tk.Toplevel(self.root)
            dialog.title("Select Device")
            dialog.geometry("300x100")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Select a device:").pack(pady=5)
            device_var = tk.StringVar(value=device_names[0])
            dropdown = ttk.Combobox(dialog, textvariable=device_var, values=device_names, state="readonly")
            dropdown.pack(pady=5, padx=5, fill=tk.X)
            
            device_name = None
            
            def confirm():
                nonlocal device_name
                device_name = device_var.get()
                dialog.destroy()
            
            ttk.Button(dialog, text="OK", command=confirm).pack(pady=5)
            dialog.wait_window()
            
            return device_name if device_name else ""
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get devices: {e}")
            return ""
        
    def _list_devices(self) -> None:
        """List all available NI devices."""
        try:
            devices = nidaqmx.system.System.local().devices
            output = "Available Devices:\n" + "-" * 40 + "\n"
            for device in devices:
                output += f"Device: {device.name}\n"
                output += f"  Product Type: {device.product_type}\n"
                # Use correct attribute name; fall back if unavailable
                try:
                    serial = getattr(device, "serial_num")
                except Exception:
                    serial = "N/A"
                output += f"  Serial Number: {serial}\n\n"
            self._output(self.system_output, output)
            self._log("Listed devices successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list devices: {e}")
            self._log(f"Error listing devices: {e}")
    
    def _list_channels(self) -> None:
        """List all available channels on devices."""
        device_name = self._select_device_name()
        # try:
        #     devices = nidaqmx.system.System.local().devices
        #     device_names = [device.name for device in devices]
        #     
        #     if not device_names:
        #         messagebox.showwarning("Warning", "No devices found.")
        #         return
        #     
        #     # Create a simple dialog with dropdown
        #     dialog = tk.Toplevel(self.root)
        #     dialog.title("Select Device")
        #     dialog.geometry("300x100")
        #     dialog.transient(self.root)
        #     dialog.grab_set()
        #     
        #     ttk.Label(dialog, text="Select a device:").pack(pady=5)
        #     device_var = tk.StringVar(value=device_names[0])
        #     dropdown = ttk.Combobox(dialog, textvariable=device_var, values=device_names, state="readonly")
        #     dropdown.pack(pady=5, padx=5, fill=tk.X)
        #     
        #     device_name = None
        #     
        #     def confirm():
        #         nonlocal device_name
        #         device_name = device_var.get()
        #         dialog.destroy()
        #     
        #     ttk.Button(dialog, text="OK", command=confirm).pack(pady=5)
        #     dialog.wait_window()
        #     
        #     if not device_name:
        #         return
        # except Exception as e:
        #     messagebox.showerror("Error", f"Failed to get devices: {e}")
        #     return
        # if not device_name:
        #     return
        
        try:
            device = nidaqmx.system.System.local().devices[device_name]
            output = f"Channels on {device_name}:\n" + "-" * 40 + "\n"
            try:
                ai_chans = device.ai_physical_chans
                output += f"AI Channels: {', '.join([ch.name for ch in ai_chans]) if ai_chans else 'None'}\n"
            except Exception:
                output += "AI Channels: N/A\n"
            
            try:
                ao_chans = device.ao_physical_chans
                output += f"AO Channels: {', '.join([ch.name for ch in ao_chans]) if ao_chans else 'None'}\n"
            except Exception:
                output += "AO Channels: N/A\n"
            
            try:
                di_lines = device.di_lines
                output += f"DI Channels: {', '.join([line.name for line in di_lines]) if di_lines else 'None'}\n"
            except Exception:
                output += "DI Channels: N/A\n"
            
            try:
                do_lines = device.do_lines
                output += f"DO Channels: {', '.join([line.name for line in do_lines]) if do_lines else 'None'}\n"
            except Exception:
                output += "DO Channels: N/A\n"
            self._output(self.system_output, output)
            self._log(f"Listed channels for {device_name}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list channels: {e}")
            self._log(f"Error listing channels: {e}")
    
    def _list_tasks(self) -> None:
        """List all active tasks."""
        try:
            tasks = nidaqmx.system.System.local().tasks
            output = f"Active Tasks: {len(tasks)}\n" + "-" * 40 + "\n"
            for i, task in enumerate(tasks):
                output += f"Task {i+1}: {task.name}\n"
                output += f"  Number of channels: {len(task.channels)}\n"
                output += f"  Is task done: {task.is_task_done()}\n\n"
            if not tasks:
                output += "No active tasks.\n"
            self._output(self.system_output, output)
            self._log(f"Listed tasks: {len(tasks)} active.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list tasks: {e}")
            self._log(f"Error listing tasks: {e}")
    
    # Task management
    def _create_task(self) -> None:
        """Create a new task."""
        try:
            self.current_task = nidaqmx.Task()
            messagebox.showinfo("Success", "Task created successfully!")
            self._log("Created new task.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create task: {e}")
            self._log(f"Error creating task: {e}")
    
    def _close_task(self) -> None:
        """Close the current task."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open.")
            return
        
        try:
            self.current_task.close()
            self.current_task = None
            self.acquisition_running = False
            messagebox.showinfo("Success", "Task closed successfully!")
            self._log("Closed current task.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to close task: {e}")
            self._log(f"Error closing task: {e}")
    
    def _task_status(self) -> None:
        """Show status of current task."""
        if not self.current_task:
            output = "No task is currently open."
        else:
            try:
                output = f"Task Status:\n" + "-" * 40 + "\n"
                output += f"Task Name: {self.current_task.name}\n"
                output += f"Number of Channels: {len(self.current_task.channels)}\n"
                output += f"Is Task Done: {self.current_task.is_task_done()}\n"
                output += f"Channels:\n"
                for ch in self.current_task.channels:
                    output += f"  - {ch.name}\n"
            except Exception as e:
                output = f"Error reading task status: {e}"
                self._log(f"Error reading task status: {e}")
        
        self._output(self.task_output, output)
    
    # Channel management
    def _add_ai_voltage(self) -> None:
        """Add an analog input voltage channel."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
#        device = simpledialog.askstring("Input", "Device name (e.g., dev3):")
        device = self._select_device_name()
        if not device:
            return
        channel = simpledialog.askstring("Input", "Channel name (e.g., ai0):")
        if not channel:
            return
        
        try:
            physical_channel = f"{device}/{channel}"
            self.current_task.ai_channels.add_ai_voltage_chan(
                physical_channel,
                terminal_config=TerminalConfiguration.RSE,
                min_val=-10.0,
                max_val=10.0
            )
            output = f"Added AI voltage channel: {physical_channel}\n"
            output += f"Range: -10.0 to 10.0 V\n"
            output += f"Terminal Config: RSE\n"
            self._output(self.channel_output, output)
            self._log(f"Added AI channel: {physical_channel}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add AI channel: {e}")
            self._log(f"Error adding AI channel: {e}")
    
    def _add_ao_voltage(self) -> None:
        """Add an analog output voltage channel."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
        device = simpledialog.askstring("Input", "Device name (e.g., dev3):")
        if not device:
            return
        channel = simpledialog.askstring("Input", "Channel name (e.g., ao0):")
        if not channel:
            return
        
        try:
            physical_channel = f"{device}/{channel}"
            self.current_task.ao_channels.add_ao_voltage_chan(
                physical_channel,
                min_val=-10.0,
                max_val=10.0
            )
            output = f"Added AO voltage channel: {physical_channel}\n"
            output += f"Range: -10.0 to 10.0 V\n"
            self._output(self.channel_output, output)
            self._log(f"Added AO channel: {physical_channel}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add AO channel: {e}")
            self._log(f"Error adding AO channel: {e}")
    
    def _add_di_channel(self) -> None:
        """Add a digital input channel."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
        device = simpledialog.askstring("Input", "Device name (e.g., dev3):")
        if not device:
            return
        channel = simpledialog.askstring("Input", "Channel name (e.g., port0/line0):")
        if not channel:
            return
        
        try:
            physical_channel = f"{device}/{channel}"
            self.current_task.di_channels.add_di_chan(physical_channel)
            output = f"Added DI channel: {physical_channel}\n"
            self._output(self.channel_output, output)
            self._log(f"Added DI channel: {physical_channel}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add DI channel: {e}")
            self._log(f"Error adding DI channel: {e}")
    
    def _add_do_channel(self) -> None:
        """Add a digital output channel."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
        device = simpledialog.askstring("Input", "Device name (e.g., dev3):")
        if not device:
            return
        channel = simpledialog.askstring("Input", "Channel name (e.g., port0/line0):")
        if not channel:
            return
        
        try:
            physical_channel = f"{device}/{channel}"
            self.current_task.do_channels.add_do_chan(physical_channel)
            output = f"Added DO channel: {physical_channel}\n"
            self._output(self.channel_output, output)
            self._log(f"Added DO channel: {physical_channel}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add DO channel: {e}")
            self._log(f"Error adding DO channel: {e}")
    
    # Acquisition functions
    def _configure_timing(self) -> None:
        """Configure timing for the task."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
        rate_str = simpledialog.askstring("Input", "Sample rate (S/s) [default: 1000]:", initialvalue="1000")
        if not rate_str:
            return
        
        try:
            rate = float(rate_str)
            self.current_task.timing.cfg_samp_clk_timing(
                rate,
                sample_mode=AcquisitionType.CONTINUOUS
            )
            output = f"Configured timing:\n"
            output += f"Sample Rate: {rate} S/s\n"
            output += f"Mode: Continuous\n"
            self._output(self.acq_output, output)
            self._log(f"Configured timing: {rate} S/s, continuous mode.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to configure timing: {e}")
            self._log(f"Error configuring timing: {e}")
    
    def _start_task(self) -> None:
        """Start the task."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open. Create a task first.")
            return
        
        try:
            self.current_task.start()
            self.acquisition_running = True
            output = "Task started successfully.\n"
            self._output(self.acq_output, output)
            self._log("Task started.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start task: {e}")
            self._log(f"Error starting task: {e}")
    
    def _stop_task(self) -> None:
        """Stop the task."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open.")
            return
        
        try:
            self.current_task.stop()
            self.acquisition_running = False
            output = "Task stopped successfully.\n"
            self._output(self.acq_output, output)
            self._log("Task stopped.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop task: {e}")
            self._log(f"Error stopping task: {e}")
    
    def _read_samples(self) -> None:
        """Read samples from the task."""
        if not self.current_task:
            messagebox.showwarning("Warning", "No task is open.")
            return
        
        if not self.acquisition_running:
            messagebox.showwarning("Warning", "Task is not running. Start the task first.")
            return
        
        num_samples_str = simpledialog.askstring("Input", "Number of samples to read [default: 10]:", initialvalue="10")
        if not num_samples_str:
            return
        
        try:
            num_samples = int(num_samples_str)
            data = self.current_task.read(num_samples)
            
            output = f"Read {num_samples} samples:\n" + "-" * 40 + "\n"
            if isinstance(data, list):
                for i, sample in enumerate(data[:20]):  # Show first 20
                    output += f"Sample {i}: {sample}\n"
                if len(data) > 20:
                    output += f"... and {len(data) - 20} more samples.\n"
            else:
                output += f"Data: {data}\n"
            
            self._output(self.acq_output, output)
            self._log(f"Read {num_samples} samples.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read samples: {e}")
            self._log(f"Error reading samples: {e}")


def main() -> None:
    """Launch the GUI application."""
    root = tk.Tk()
    app = NidaqmxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
