import configparser
import os

from LogHandler import LogMessage

script_dir = os.path.dirname(os.path.abspath(__file__))

# FILE PATHS
CONFIG_FILE = os.path.join(script_dir, 'config.ini')
TRACK_LOG_FILE_PATH = os.path.join(script_dir, 'detected-tracks.json')

# Create a ConfigParser object
config = configparser.ConfigParser()

# Default config values
default_config = {
    'RECORDING': {
        'SAMPLE_RATE': '48000',
        'RECORD_SEC': '10'
    },
    'NOTIFICATIONS': {
        'NOTIFICATION_METHOD': '1',
        'NOTIFICATION_DURATION': '5'
    },
    'OSC': {
        'PORT': '9001',
        'IP': 'localhost',
        'PARAMETER_NAME': 'SongSearch'
    }
}

# Check if the config file exists, if not create it with default values
if not os.path.isfile(CONFIG_FILE):
    config.read_dict(default_config)

    LogMessage("Config file not found, creating a new one with default values.", logLevel="INFO", print_to_ui=False)
    
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)
    
    LogMessage(f"Config file created at {CONFIG_FILE}.", logLevel="SUCCESS", print_to_ui=False)
    config.read(CONFIG_FILE)

else:
    LogMessage(f"Config file found at {CONFIG_FILE}.", logLevel="INFO", print_to_ui=False)
    # Read the config file
    config.read(CONFIG_FILE)

def set_sample_rate(value):
    config.set('RECORDING', 'SAMPLE_RATE', str(value))
    save_config()

def set_record_sec(value):
    config.set('RECORDING', 'RECORD_SEC', str(value))
    save_config()

def set_notification_method(value):
    config.set('NOTIFICATIONS', 'NOTIFICATION_METHOD', str(value))
    save_config()

def set_notification_duration(value):
    config.set('NOTIFICATIONS', 'NOTIFICATION_DURATION', str(value))
    save_config()

def set_osc_port(value):
    config.set('OSC', 'PORT', str(value))
    save_config()

def set_osc_ip(value):
    config.set('OSC', 'IP', value)
    save_config()

def set_osc_parameter(value):
    config.set('OSC', 'PARAMETER_NAME', value)
    save_config()

def save_config():
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)