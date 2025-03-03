import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QFrame, QSizePolicy, QPushButton, QScrollArea, QFormLayout, QLineEdit, QRadioButton, QButtonGroup, QSlider, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread
import os
from datetime import datetime

import TrackRecognitionHandler
from ConfigHandler import config, set_sample_rate, set_record_sec, set_notification_method, set_notification_duration, set_osc_port, set_osc_ip, set_osc_parameter
from LogHandler import LogMessage

sample_rate = config.getint('RECORDING', 'SAMPLE_RATE')
record_sec = config.getint('RECORDING', 'RECORD_SEC')
notification_method = config.getint('NOTIFICATIONS', 'NOTIFICATION_METHOD')
notification_duration = config.getint('NOTIFICATIONS', 'NOTIFICATION_DURATION')
osc_port = config.getint('OSC', 'PORT')
osc_ip = config.get('OSC', 'IP')
osc_parameter = config.get('OSC', 'PARAMETER_NAME')

script_dir = os.path.dirname(os.path.abspath(__file__))
detected_tracks_file_path = os.path.join(script_dir, 'detected-tracks.json')
assets_file_path = os.path.join(script_dir, 'assets')

class TrackSearchThread(QThread):
    log_message = pyqtSignal(str)

    def run(self):
        TrackRecognitionHandler.TrackSearchInit("ButtonPress", True)

class SettingsWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        self.setMinimumSize(400, 300)

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create form layout for settings
        form_layout = QFormLayout()

        # Sample rate setting
        self.sample_rate_input = QLineEdit(str(config.getint('RECORDING', 'SAMPLE_RATE')))
        form_layout.addRow('Sample Rate:', self.sample_rate_input)

        # Record seconds setting
        self.record_sec_slider = QSlider(Qt.Horizontal)
        self.record_sec_slider.setMinimum(5)
        self.record_sec_slider.setMaximum(30)
        self.record_sec_slider.setValue(config.getint('RECORDING', 'RECORD_SEC'))
        self.record_sec_slider.setTickPosition(QSlider.TicksBelow)
        self.record_sec_slider.setTickInterval(1)
        self.record_sec_slider.valueChanged.connect(self.update_record_sec_label)
        self.record_sec_label = QLabel(str(self.record_sec_slider.value()))
        record_sec_layout = QHBoxLayout()
        record_sec_layout.addWidget(self.record_sec_slider)
        record_sec_layout.addWidget(self.record_sec_label)
        form_layout.addRow('Record Seconds:', record_sec_layout)

        # Notification method setting
        self.notification_method_group = QButtonGroup(self)
        self.windows_toast_radio = QRadioButton("Windows Toast")
        self.xsoverlay_radio = QRadioButton("XSOverlay")
        self.notification_method_group.addButton(self.windows_toast_radio, 0)
        self.notification_method_group.addButton(self.xsoverlay_radio, 1)
        notification_method_layout = QHBoxLayout()
        notification_method_layout.addWidget(self.windows_toast_radio)
        notification_method_layout.addWidget(self.xsoverlay_radio)
        form_layout.addRow('Notification Method:', notification_method_layout)

        # Set the initial state of the radio buttons based on the config
        if config.getint('NOTIFICATIONS', 'NOTIFICATION_METHOD') == 0:
            self.windows_toast_radio.setChecked(True)
        else:
            self.xsoverlay_radio.setChecked(True)

        # Notification duration setting
        self.notification_duration_slider = QSlider(Qt.Horizontal)
        self.notification_duration_slider.setMinimum(1)
        self.notification_duration_slider.setMaximum(10)
        self.notification_duration_slider.setValue(config.getint('NOTIFICATIONS', 'NOTIFICATION_DURATION'))
        self.notification_duration_slider.setTickPosition(QSlider.TicksBelow)
        self.notification_duration_slider.setTickInterval(1)
        self.notification_duration_slider.valueChanged.connect(self.update_notification_duration_label)
        self.notification_duration_label = QLabel(str(self.notification_duration_slider.value()))
        notification_duration_layout = QHBoxLayout()
        notification_duration_layout.addWidget(self.notification_duration_slider)
        notification_duration_layout.addWidget(self.notification_duration_label)
        form_layout.addRow('Notification Duration:', notification_duration_layout)

        # OSC port setting
        self.osc_port_input = QLineEdit(str(config.getint('OSC', 'PORT')))
        form_layout.addRow('OSC Port:', self.osc_port_input)

        # OSC IP setting
        self.osc_ip_input = QLineEdit(config.get('OSC', 'IP'))
        form_layout.addRow('OSC IP:', self.osc_ip_input)

        # OSC parameter setting
        self.osc_parameter_input = QLineEdit(config.get('OSC', 'PARAMETER_NAME'))
        form_layout.addRow('OSC Parameter:', self.osc_parameter_input)

        # Save button
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_settings)
        form_layout.addRow(save_button)

        # Clear detected tracks button
        clear_tracks_button = QPushButton('Clear Detected Tracks')
        clear_tracks_button.clicked.connect(self.clear_detected_tracks)
        form_layout.addRow(clear_tracks_button)

        # Add form layout to main layout
        main_layout.addLayout(form_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

    def update_record_sec_label(self, value):
        self.record_sec_label.setText(str(value))

    def update_notification_duration_label(self, value):
        self.notification_duration_label.setText(str(value))

    def save_settings(self):
        try:
            sample_rate = int(self.sample_rate_input.text())
            osc_port = int(self.osc_port_input.text())
            osc_ip = self.osc_ip_input.text()
            osc_parameter = self.osc_parameter_input.text()

            set_sample_rate(sample_rate)
            set_record_sec(self.record_sec_slider.value())
            set_notification_method(self.notification_method_group.checkedId())
            set_notification_duration(self.notification_duration_slider.value())
            set_osc_port(osc_port)
            set_osc_ip(osc_ip)
            set_osc_parameter(osc_parameter)
            self.close()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid values for all fields.")

    def clear_detected_tracks(self):
        with open(detected_tracks_file_path, 'w') as track_log:
            json.dump([], track_log, indent=4, separators=(',', ': '))
        LogMessage("Detected tracks cleared.", logLevel="INFO")
        self.main_window.updateWidgets()

# Main window class
class MyWindow(QWidget):
    
    updateUI = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()
        self.track_search_thread = TrackSearchThread()

    def initUI(self):
        # Create the main layout
        main_layout = QVBoxLayout()  # Change to QVBoxLayout to stack vertically
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create a horizontal layout for the list and widgets
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)
        
        # Create the list view
        self.list_view = QListWidget()
        self.list_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a vertical layout for the widget items
        self.widget_layout = QVBoxLayout()
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(10)

        # Add the list view and the widget layout to the content layout
        content_layout.addWidget(self.list_view)
        content_layout.addLayout(self.widget_layout)

        # Add the content layout to the main layout
        main_layout.addLayout(content_layout)

        # Create a horizontal layout for the buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        # Create buttons
        button1 = QPushButton('Start Track Search')
        button2 = QPushButton('View History')
        button3 = QPushButton('Settings')

        # Set size policy for buttons
        button1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        button3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Connect buttons to functions
        button1.clicked.connect(self.TrackSearchClick)
        button2.clicked.connect(self.viewHistory)
        button3.clicked.connect(self.openSettings)

        # Add buttons to the button layout
        button_layout.addWidget(button1)
        button_layout.addWidget(button2)
        button_layout.addWidget(button3)

        # Add the button layout to the main layout
        main_layout.addLayout(button_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

        self.setMinimumSize(800, 600)
        self.setWindowTitle('VRCazam')
        self.updateWidgets()
        self.show()

    def TrackSearchClick(self):
        self.track_search_thread.start()

    def viewHistory(self):
        self.history_window = HistoryWindow()
        self.history_window.show()

    def openSettings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def print_log_message(self, message):
        item = QListWidgetItem(message)  # Create a list item with the message
        self.list_view.addItem(item)  # Add the item to the list view
        self.list_view.scrollToBottom()  # Scroll to the bottom

    def updateWidgets(self):
        #self.updateUI.emit()
        # Clear the existing widget layout
        while self.widget_layout.count():
            item = self.widget_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Load widget names from JSON file
        with open(detected_tracks_file_path) as json_file:
            data = json.load(json_file)
            tracks = data

        tracks.reverse()

        for i, track in enumerate(tracks):
            if i == 5:
                break

            # Create a frame for each widget item
            widget_frame = QFrame()
            widget_frame.setFrameShape(QFrame.StyledPanel)
            widget_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set the size policy

            # Create a horizontal layout for the widget
            widget_horizontal_layout = QHBoxLayout(widget_frame)
            widget_horizontal_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            # Create an image label
            image_label = QLabel() 
            pixmap = QPixmap()

            if track["cover_art"] is not None:
                image_data = requests.get(track["cover_art"]).content
                pixmap.loadFromData(image_data)
            else:
                pixmap.load(f"{assets_file_path}/placeholderambart.png")
                
            pixmap = pixmap.scaled(75, 75)  # Set maximum size to 75x75 pixels
            image_label.setPixmap(pixmap)
            widget_horizontal_layout.addWidget(image_label)

            # Create a vertical layout for the widget
            widget_vertical_layout = QVBoxLayout()
            widget_horizontal_layout.addLayout(widget_vertical_layout)
            widget_vertical_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            # Add label to the vertical layout
            song_name_label = QLabel(track["title"])
            song_name_label.setFont(QFont("Arial", 10, QFont.Bold))
            widget_vertical_layout.addWidget(song_name_label)

            # Add label to the vertical layout
            song_artist_label = QLabel(track["artist"])
            widget_vertical_layout.addWidget(song_artist_label)

            # Add clickable URLs as labels with images
            provider_layout = QHBoxLayout()  # Create horizontal layout for provider images
            provider_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            if track["apple_music_uri"] is not None:
                url_label = QLabel()
                url_label.setOpenExternalLinks(True)
                url_label.setTextFormat(Qt.RichText)

                url_label.setText("<a href='{0}'><img src='{1}' width='37' height='37'></a>".format(track["apple_music_uri"], f"{assets_file_path}/apple-music.svg"))
                provider_layout.addWidget(url_label)

            for provider in track["track_providers"]:
                url_label = QLabel()
                url_label.setOpenExternalLinks(True)
                url_label.setTextFormat(Qt.RichText)

                provider_image = ""
                if provider["platform"] == "SPOTIFY":
                    provider_image = f"{assets_file_path}/spotify.svg"
                elif provider["platform"] == "DEEZER":
                    provider_image = f"{assets_file_path}/deezer.svg"

                url_label.setText("<a href='{0}'><img src='{1}' width='37' height='37'></a>".format(provider["uri"], provider_image))
                provider_layout.addWidget(url_label)

            widget_vertical_layout.addLayout(provider_layout)  # Add provider layout to the widget layout

            # Add the widget frame to the layout
            self.widget_layout.addWidget(widget_frame)

class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Track History')
        self.setMinimumSize(800, 600)

        # Create the main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        # Create a widget for the scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(10)

        # Load widget names from JSON file
        with open(detected_tracks_file_path) as json_file:
            data = json.load(json_file)
            tracks = data

        tracks.reverse()

        for track in tracks:
            # Create a frame for each widget item
            widget_frame = QFrame()
            widget_frame.setFrameShape(QFrame.StyledPanel)
            widget_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # Set the size policy

            # Create a horizontal layout for the widget
            widget_horizontal_layout = QHBoxLayout(widget_frame)
            widget_horizontal_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            # Create an image label
            image_label = QLabel()
            pixmap = QPixmap()

            if track["cover_art"] is not None:
                image_data = requests.get(track["cover_art"]).content
                pixmap.loadFromData(image_data)
            else:
                pixmap.load(f"{assets_file_path}/placeholderambart.png")

            pixmap = pixmap.scaled(75, 75)  # Set maximum size to 75x75 pixels
            image_label.setPixmap(pixmap)
            widget_horizontal_layout.addWidget(image_label)

            # Create a vertical layout for the widget
            widget_vertical_layout = QVBoxLayout()
            widget_horizontal_layout.addLayout(widget_vertical_layout)
            widget_vertical_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            # Add label to the vertical layout
            song_name_label = QLabel(track["title"])
            song_name_label.setFont(QFont("Arial", 10, QFont.Bold))
            widget_vertical_layout.addWidget(song_name_label)

            # Add label to the vertical layout
            song_artist_label = QLabel(track["artist"])
            widget_vertical_layout.addWidget(song_artist_label)

            # Add datetime detected to the vertical layout
            datetime_detected = datetime.fromtimestamp(track["time_detected"]).strftime('%Y-%m-%d %H:%M:%S')
            datetime_label = QLabel(f"Detected on: {datetime_detected}")
            widget_vertical_layout.addWidget(datetime_label)

            # Add clickable URLs as labels with images
            provider_layout = QHBoxLayout()  # Create horizontal layout for provider images
            provider_layout.setAlignment(Qt.AlignLeft)  # Align the content to the left

            if track["apple_music_uri"] is not None:
                url_label = QLabel()
                url_label.setOpenExternalLinks(True)
                url_label.setTextFormat(Qt.RichText)

                url_label.setText("<a href='{0}'><img src='{1}' width='37' height='37'></a>".format(track["apple_music_uri"], f"{assets_file_path}/apple-music.svg"))
                provider_layout.addWidget(url_label)

            for provider in track["track_providers"]:
                url_label = QLabel()
                url_label.setOpenExternalLinks(True)
                url_label.setTextFormat(Qt.RichText)

                provider_image = ""
                if provider["platform"] == "SPOTIFY":
                    provider_image = f"{assets_file_path}/spotify.svg"
                elif provider["platform"] == "DEEZER":
                    provider_image = f"{assets_file_path}/deezer.svg"

                url_label.setText("<a href='{0}'><img src='{1}' width='37' height='37'></a>".format(provider["uri"], provider_image))
                provider_layout.addWidget(url_label)

            widget_vertical_layout.addLayout(provider_layout)  # Add provider layout to the widget layout

            # Add the widget frame to the layout
            scroll_layout.addWidget(widget_frame)

        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Set the main layout for the window
        self.setLayout(main_layout)

app = QApplication(sys.argv)
# Create the main window
window = MyWindow()

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    sys.exit(app.exec_())
