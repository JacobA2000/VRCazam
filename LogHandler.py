import json
from datetime import datetime
import inspect
import os

from ConfigHandler import TRACK_LOG_FILE_PATH
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

def LogMessage(message, logLevel="INFO"):
    
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
    
def LogDetectedTrack(track_data):
    LogMessage(f"Logging track: {track_data['title']} - {track_data['subtitle']}")

    with open(TRACK_LOG_FILE_PATH) as track_log:
        track_log_list = json.load(track_log)
    
    needed_track_data = {
        "title": track_data["title"],
        "artist": track_data["subtitle"],
        "cover_art": track_data["images"]["coverarthq"] if "images" in track_data.keys() else None,
        "apple_music_uri": f"https://music.apple.com/us/song/{track_data['hub']['actions'][0]['id']}" if 'hub' in track_data and 'actions' in track_data['hub'] and track_data['hub']['actions'][0]['id'] else None,
        "track_providers": [{"platform": item["type"], "uri": item["actions"][0]["uri"]} for item in track_data["hub"]["providers"]],
        "time_detected": int(datetime.now().timestamp())
    }
    
    track_log_list.append(needed_track_data)

    with open(TRACK_LOG_FILE_PATH, "w+") as track_log:
        json.dump(track_log_list, track_log, indent=4, separators=(',',': '))

    print("Finished logging track.")
    ui.window.print_log_message("Finished logging track.")