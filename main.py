from ShazamAPI import Shazam
import soundcard as sc
import soundfile as sf
import io
from pythonosc import dispatcher, osc_server
import socket
import json
from os import path
from datetime import datetime
import configparser
from plyer import notification

# FILE PATHS
CONFIG_FILE = "./config.cfg"
TRACK_LOG_FILE_PATH = "./detected-tracks.json"

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the config file
config.read('config.ini')

# Access the variables under the [RECORDING] section
sample_rate = config.getint('RECORDING', 'SAMPLE_RATE')
record_sec = config.getint('RECORDING', 'RECORD_SEC')

# Access the variables under the [NOTIFICATIONS] section
notification_method = config.getint('NOTIFICATIONS', 'NOTIFICATION_METHOD')
notification_duration = config.getint('NOTIFICATIONS', 'NOTIFICATION_DURATION')

def RecordAudioBytes(sr, rs):
    print("Recording...")
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sr) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=sr*rs)

        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        with io.BytesIO() as f:
            sf.write(file=f, data=data[:, 0], samplerate=sr, format='wav')
            audio_bytes = f.getvalue()

    print("Finished recording.")

    return audio_bytes

def RecognizeSong(audio_bytes):
    shazam = Shazam(audio_bytes)
    recognize_generator = shazam.recognizeSong()

    while True:
        try:
            shazam_data = next(recognize_generator)
            
            if shazam_data[1]["track"] != "":
                track_data = shazam_data[1]["track"]
                #LOG SONG
                LogDetectedTrack(track_data)
                track_msg = f"{track_data['title']} - {track_data['subtitle']}"
                print(f"Song Recognized - {track_msg}")
                return (track_msg, "Song Recognized")

        except:
            StopIteration
            print("Couldn't identify song!")
            return ("Shazam couldn't identify the song, please try again.", "Couldn't identify song!")

def SongSearchInit(address, *args):

    if args[0] == True:
        print(f"OSC Message Recieved on address {address}.")
        audio_bytes = RecordAudioBytes(sample_rate, record_sec)
        track_msg = RecognizeSong(audio_bytes)

        SendNotification(content=track_msg[0], msg_type=track_msg[1])


def SendNotification(content, msg_type):

    match notification_method:
        case 0:
            notification.notify(
                title=f"VRCazam - {msg_type}",
                message=content,
                app_name="VRCazam",
                app_icon=None,  # You can specify an icon file path here
                timeout=notification_duration,     # Duration in seconds for the notification to stay on the screen
            )

        case 1:
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

    with open(TRACK_LOG_FILE_PATH) as track_log:
        track_log_list = json.load(track_log)
    
    needed_track_data = {
        "title": track_data["title"],
        "artist": track_data["subtitle"],
        "cover_art": track_data["images"]["coverarthq"],
        "apple_music_uri": f"https://music.apple.com/us/song/{track_data['hub']['actions'][0]['id']}" if 'hub' in track_data and 'actions' in track_data['hub'] and track_data['hub']['actions'][0]['id'] else None,
        "track_providers": [{"platform": item["type"], "uri": item["actions"][0]["uri"]} for item in track_data["hub"]["providers"]],
        "time_detected": int(datetime.now().timestamp())
    }
    
    track_log_list.append(needed_track_data)

    with open(TRACK_LOG_FILE_PATH, "w+") as track_log:
        json.dump(track_log_list, track_log, indent=4, separators=(',',': '))

    print("Finished logging track.")

# Check if the track log exists if not create an empty one.
if path.isfile(TRACK_LOG_FILE_PATH) is False:
    with open(TRACK_LOG_FILE_PATH, "w") as track_log:
        json.dump([], track_log, indent=4, separators=(',',': '))

# Set up the dispatcher to route messages to the function
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/avatar/parameters/SongSearch", SongSearchInit)

# Set up the OSC server to listen on port 8000
server = osc_server.ThreadingOSCUDPServer(("localhost", 9001), dispatcher)
print(f"Listening for OSC messages on port {9001}...")

# Start the OSC server
server.serve_forever()