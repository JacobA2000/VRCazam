import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QFrame, QSizePolicy, QPushButton
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import pyqtSignal, QObject, Qt, QThread
import os

import TrackRecognitionHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
detected_tracks_file_path = os.path.join(script_dir, 'detected-tracks.json')
assets_file_path = os.path.join(script_dir, 'assets')

class TrackSearchThread(QThread):
    log_message = pyqtSignal(str)

    def run(self):
        TrackRecognitionHandler.TrackSearchInit("test", True)

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
        # Temporary just open the json file
        os.system(f"start {detected_tracks_file_path}")

        # Todo open a new window with the history

    def openSettings(self):
        print("Settings clicked")

    def print_log_message(self, message):
        item = QListWidgetItem(message)  # Create a list item with the message
        self.list_view.addItem(item)  # Add the item to the list view

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

app = QApplication(sys.argv)
# Create the main window
window = MyWindow()

if __name__ == '__main__':
    app = QApplication([])
    window = MyWindow()
    sys.exit(app.exec_())
