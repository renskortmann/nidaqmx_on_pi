"""Simple CLI for nidaqmx_on_pi scaffold."""

import argparse
import nidaqmx
from nidaqmx.constants import AcquisitionType, TerminalConfiguration
from . import greet
from .gui import main as gui_main


def main() -> None:
    parser = argparse.ArgumentParser(prog="nidaqmx_on_pi")
    parser.add_argument("name", nargs="?", default="world")
    parser.add_argument("--gui", action="store_true", help="Launch the tkinter GUI")
    args = parser.parse_args()
    
    if args.gui:
        gui_main()
    else:
        print(greet(args.name))


def start_continuous_ai_task(device: str = "dev3", channel: str = "ai0", rate: float = 1000.0, min_val: float = -10.0, max_val: float = 10.0) -> nidaqmx.Task:
    """Create and start a continuous analog-input task for `device/channel`.

    The function returns a started `nidaqmx.Task` instance. Caller is
    responsible for reading from the task (for example using a
    `nidaqmx.stream_readers.AnalogSingleChannelReader`) and for calling
    `task.close()` when finished.

    Args:
        device: NI device name (default "dev3").
        channel: Analog channel on the device (default "ai0").
        rate: Sample clock rate in samples per second.
        min_val: Minimum expected voltage.
        max_val: Maximum expected voltage.

    Returns:
        A started `nidaqmx.Task` configured for continuous acquisition.
    """
    task = nidaqmx.Task()
    physical_channel = f"{device}/{channel}"
    task.ai_channels.add_ai_voltage_chan(physical_channel,
                                         terminal_config=TerminalConfiguration.RSE,
                                         min_val=min_val,
                                         max_val=max_val)
    task.timing.cfg_samp_clk_timing(rate, sample_mode=AcquisitionType.CONTINUOUS)
    task.start()
    return task


if __name__ == "__main__":
    main()
