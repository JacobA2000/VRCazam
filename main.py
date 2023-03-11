from ShazamAPI import Shazam
import soundcard as sc
import soundfile as sf
import io
from pythonosc import dispatcher, osc_server

SAMPLE_RATE = 48000              # [Hz]. sampling rate.
RECORD_SEC = 10                  # [sec]. duration recording audio.

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
                print(f"{track_data['title']} - {track_data['subtitle']}")
                break

        except:
            StopIteration
            print("Couldn't identify song!")
            break

def SongSearchInit(address, *args):

    if args[0] == True:
        print(f"OSC Message Recieved on address {address}.")
        audio_bytes = RecordAudioBytes(SAMPLE_RATE, RECORD_SEC)
        RecognizeSong(audio_bytes)

# Set up the dispatcher to route messages to the function
dispatcher = dispatcher.Dispatcher()
dispatcher.map("/avatar/parameters/SongSearch", SongSearchInit)

# Set up the OSC server to listen on port 8000
server = osc_server.ThreadingOSCUDPServer(("localhost", 9001), dispatcher)
print(f"Listening for OSC messages on port {9001}...")

# Start the OSC server
server.serve_forever()