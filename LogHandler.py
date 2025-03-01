import json
from datetime import datetime

from ConfigHandler import TRACK_LOG_FILE_PATH
from ui import window

def LogMessage(message):
    print(message)
    window.print_log_message(message)

def LogDetectedTrack(track_data):
    print("Logging Track...")
    window.print_log_message("Logging Track...")

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
    window.print_log_message("Finished logging track.")