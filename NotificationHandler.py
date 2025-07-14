from plyer import notification
import socket
import json

from ConfigHandler import config

def SendNotification(content, msg_type):
    
    # GET NOTIFICATION SETTINGS
    notification_method = config.getint('NOTIFICATIONS', 'NOTIFICATION_METHOD')
    notification_duration = config.getint('NOTIFICATIONS', 'NOTIFICATION_DURATION')

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