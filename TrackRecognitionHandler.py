from ShazamAPI import Shazam
import soundcard as sc
import soundfile as sf
import io
from datetime import datetime
import json

import ui
from NotificationHandler import SendNotification
from LogHandler import LogMessage
from ConfigHandler import config, TRACK_LOG_FILE_PATH

def RecordAudioBytes(sr, rs):
    LogMessage(f"Recording for {rs} seconds at {sr} Hz.", logLevel="INFO")    
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sr) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=sr*rs)

        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        with io.BytesIO() as f:
            sf.write(file=f, data=data[:, 0], samplerate=sr, format='wav')
            audio_bytes = f.getvalue()

    LogMessage("Finished recording.", logLevel="INFO")

    return audio_bytes

def RecognizeSong(audio_bytes):
    shazam = Shazam(audio_bytes)
    recognize_generator = shazam.recognizeSong()

    while True:
        try:
            shazam_data = next(recognize_generator)
            
            if "track" in shazam_data[1]:
                track_data = shazam_data[1]["track"]
                # LOG SONG
                LogDetectedTrack(track_data)
                track_msg = f"{track_data['title']} - {track_data['subtitle']}"
                LogMessage(f"Song Recognized - {track_msg}", logLevel="SUCCESS")
                return (track_msg, "Song Recognized")

        except StopIteration:
            LogMessage("Couldn't identify song!", logLevel="WARNING")

            return ("Shazam couldn't identify the song, please try again.", "Couldn't identify song!")

def TrackSearchInit(address, *args):
    if args[0] == True:

        if address != "ButtonPress":
            LogMessage(f"OSC Message Received on address {address}.", logLevel="INFO")

        # Get up to date settings values from the config file
        sample_rate = config.getint('RECORDING', 'SAMPLE_RATE')
        record_sec = config.getint('RECORDING', 'RECORD_SEC')   

        audio_bytes = RecordAudioBytes(sample_rate, record_sec)
        track_msg = RecognizeSong(audio_bytes)
        ui.window.updateUI.emit()
        SendNotification(
            content=track_msg[0], 
            msg_type=track_msg[1], 
        )

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

    LogMessage("Finished logging track.", logLevel="INFO")