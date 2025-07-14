from datetime import datetime
import inspect
import os

import ui

class ansi_colours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def LogMessage(message, logLevel="INFO", print_to_ui=True):
    
    if print_to_ui:
        ui.window.print_log_message(message)
    
    match logLevel:
        case "INFO":
            message = message
        case "WARNING":
            message = f"{ansi_colours.WARNING}{message}{ansi_colours.ENDC}"
        case "ERROR":
            message = f"{ansi_colours.FAIL}{message}{ansi_colours.ENDC}"
        case "SUCCESS":
            message = f"{ansi_colours.OKGREEN}{message}{ansi_colours.ENDC}"
        case _:
            message = message
    
    caller_frame = inspect.stack()[1]
    caller_filename_full = caller_frame.filename
    caller_filename_only = os.path.splitext(os.path.basename(caller_filename_full))[0]

    message = f"{ansi_colours.OKBLUE}[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]{ansi_colours.ENDC}{ansi_colours.WARNING}[{caller_filename_only}]{ansi_colours.ENDC} {message}"
    print(message)  