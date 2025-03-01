import configparser
import os

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