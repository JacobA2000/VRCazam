from ShazamAPI import Shazam
import soundcard as sc
import soundfile as sf
import io

from ui import window
from NotificationHandler import SendNotification
from LogHandler import LogDetectedTrack, LogMessage
from ConfigHandler import sample_rate, record_sec, notification_method, notification_duration

def RecordAudioBytes(sr, rs):
    LogMessage("Recording...")
    with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=sr) as mic:
        # record audio with loopback from default speaker.
        data = mic.record(numframes=sr*rs)

        # change "data=data[:, 0]" to "data=data", if you would like to write audio as multiple-channels.
        with io.BytesIO() as f:
            sf.write(file=f, data=data[:, 0], samplerate=sr, format='wav')
            audio_bytes = f.getvalue()

    LogMessage("Finished recording.")

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
                LogMessage(f"Song Recognized - {track_msg}")
                return (track_msg, "Song Recognized")

        except StopIteration:
            LogMessage("Couldn't identify song!")

            return ("Shazam couldn't identify the song, please try again.", "Couldn't identify song!")

def TrackSearchInit(address, *args):
    if args[0] == True:
        LogMessage(f"OSC Message Received on address {address}.")
        audio_bytes = RecordAudioBytes(sample_rate, record_sec)
        track_msg = RecognizeSong(audio_bytes)
        window.updateUI.emit()
        SendNotification(
            content=track_msg[0], 
            msg_type=track_msg[1], 
            notification_method=notification_method, 
            notification_duration=notification_duration
        )