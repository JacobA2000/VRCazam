import sys
import os
import json
from pythonosc import dispatcher, osc_server
import threading
from PyQt5.QtCore import pyqtSlot

from ui import window, app
from ConfigHandler import TRACK_LOG_FILE_PATH, config
from TrackRecognitionHandler import TrackSearchInit
from LogHandler import LogMessage

def run_osc_server():
    global osc_thread

    # Get OSC port, IP and parameter from the config file
    osc_port = config.getint('OSC', 'PORT')
    osc_ip = config.get('OSC', 'IP')
    osc_parameter = config.get('OSC', 'PARAMETER_NAME')

    # Set up the dispatcher to route messages to the function
    osc_dispatcher = dispatcher.Dispatcher()
    osc_dispatcher.map(f"/avatar/parameters/{osc_parameter}", TrackSearchInit)

    # Set up the OSC server to listen on port 9001
    osc_thread = osc_server.ThreadingOSCUDPServer((osc_ip, osc_port), osc_dispatcher)
    LogMessage(f"Listening for OSC messages on port {osc_port}...", logLevel="INFO")
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