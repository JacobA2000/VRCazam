import sys
import os
import json
from datetime import datetime
import configparser
from PyQt5.QtWidgets import QApplication
from plyer import notification
from ShazamAPI import Shazam
import soundcard as sc
import soundfile as sf
import io
from pythonosc import dispatcher, osc_server
import socket
import threading
from PyQt5.QtCore import pyqtSlot
from ui import MyWindow

app = QApplication(sys.argv)
# Create the main window
window = MyWindow()

script_dir = os.path.dirname(os.path.abspath(__file__))

# FILE PATHS
CONFIG_FILE = os.path.join(script_dir, 'config.ini')
TRACK_LOG_FILE_PATH = os.path.join(script_dir, 'detected-tracks.json')

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the config file
config.read(CONFIG_FILE)

# Access the variables under the [RECORDING] section
sample_rate = config.getint('RECORDING', 'SAMPLE_RATE')
record_sec = config.getint('RECORDING', 'RECORD_SEC')

# Access the variables under the [NOTIFICATIONS] section
notification_method = config.getint('NOTIFICATIONS', 'NOTIFICATION_METHOD')
notification_duration = config.getint('NOTIFICATIONS', 'NOTIFICATION_DURATION')

# Access the variables under the [OSC] section
osc_port = config.getint('OSC', 'PORT')
osc_ip = config.get('OSC', 'IP')
osc_parameter = config.get('OSC', 'PARAMETER_NAME')

def RecordAudioBytes(sr, rs):
    print("Recording...")
    window.print_log_message("Recording...")
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sr) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=sr*rs)

        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        with io.BytesIO() as f:
            sf.write(file=f, data=data[:, 0], samplerate=sr, format='wav')
            audio_bytes = f.getvalue()

    print("Finished recording.")
    window.print_log_message("Finished recording.")

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
                print(f"Song Recognized - {track_msg}")
                window.print_log_message(f"Song Recognized - {track_msg}")
                return (track_msg, "Song Recognized")

        except StopIteration:
            print("Couldn't identify song!")
            window.print_log_message("Couldn't identify song!")

            return ("Shazam couldn't identify the song, please try again.", "Couldn't identify song!")

def SongSearchInit(address, *args):
    if args[0] == True:
        print(f"OSC Message Received on address {address}.")
        window.print_log_message(f"OSC Message Received on address {address}.")
        audio_bytes = RecordAudioBytes(sample_rate, record_sec)
        track_msg = RecognizeSong(audio_bytes)
        window.updateUI.emit()
        SendNotification(content=track_msg[0], msg_type=track_msg[1])

def SendNotification(content, msg_type):
    if notification_method == 0:
        notification.notify(
            title=f"VRCazam - {msg_type}",
            message=content,
            app_name="VRCazam",
            app_icon=None,  # You can specify an icon file path here
            timeout=notification_duration,     # Duration in seconds for the notification to stay on the screen
        )
    elif notification_method == 1:
        ip = "127.0.0.1"
        port = 42069

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        msg = {
            "messageType": 1,
            "index": 0,
            "title": f"VRCazam - {msg_type}",
            "content": content,
            "height": 175.0,
            "sourceApp": "VRCazam",
            "timeout": notification_duration,
            "volume": 0.7,
            "audioPath": "default",
            "useBase64Icon": False,
            "icon": "default",
            "opacity": 1.0
        }

        msgdata = json.dumps(msg)
        byte = msgdata.encode()

        sock.sendto(byte, (ip, port))
        sock.close()

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

def run_osc_server():
    global osc_thread
    # Set up the dispatcher to route messages to the function
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map(f"/avatar/parameters/{osc_parameter}", SongSearchInit)

    # Set up the OSC server to listen on port 9001
    osc_thread = osc_server.ThreadingOSCUDPServer((osc_ip, osc_port), osc_dispatcher)
    print(f"Listening for OSC messages on port {osc_port}...")
    window.print_log_message(f"Listening for OSC messages on port {osc_port}...")

    # Start the OSC server
    osc_thread.serve_forever()

def stop_osc_server():
    global osc_thread
    if osc_thread is not None:
        osc_thread.shutdown()

def close_event_handler(event):
    stop_osc_server()
    event.accept()

@pyqtSlot()
def updateWidgetsSig():
    window.updateWidgets()

window.updateUI.connect(updateWidgetsSig)

if __name__ == '__main__':
    # Check if the track log exists if not create an empty one.
    if not os.path.isfile(TRACK_LOG_FILE_PATH):
        with open(TRACK_LOG_FILE_PATH, "w") as track_log:
            json.dump([], track_log, indent=4, separators=(',',': '))
     
    # Start the OSC server thread
    osc_thread = None
    osc_thread = threading.Thread(target=run_osc_server)
    osc_thread.start()

    window.closeEvent = close_event_handler
    window.show()

    # Start the PyQt application event loop
    sys.exit(app.exec_())