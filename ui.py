import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QListWidgetItem, QLabel, QVBoxLayout, QFrame
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Create the main layout
        main_layout = QHBoxLayout()

        # Create the list view
        list_view = QListWidget()
        list_view.setDisabled(True)

        # Create a vertical layout for the widget items
        widget_layout = QVBoxLayout()

        # Load widget names from JSON file
        with open("detected-tracks.json") as json_file:
            data = json.load(json_file)
            tracks = data

        for track in tracks:
            # Create a frame for each widget item
            widget_frame = QFrame()
            widget_frame.setFrameShape(QFrame.StyledPanel)

            # Create a horizontal layout for the widget
            widget_horizontal_layout = QHBoxLayout(widget_frame)

            # Create an image label
            image_label = QLabel()
            image_data = requests.get(track["cover_art"]).content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            pixmap = pixmap.scaled(75, 75)  # Set maximum size to 75x75 pixels
            image_label.setPixmap(pixmap)
            widget_horizontal_layout.addWidget(image_label)

            # Create a vertical layout for the widget
            widget_vertical_layout = QVBoxLayout()
            widget_horizontal_layout.addLayout(widget_vertical_layout)

            # Add label to the vertical layout
            song_name_label = QLabel(track["title"])
            song_name_label.setFont(QFont("Arial", 10, QFont.Bold))
            widget_vertical_layout.addWidget(song_name_label)

            # Add label to the vertical layout
            song_artist_label = QLabel(track["artist"])
            widget_vertical_layout.addWidget(song_artist_label)

            # Add the widget frame to the layout
            widget_layout.addWidget(widget_frame)

        # Add the list view and the widget layout to the main layout
        main_layout.addWidget(list_view)
        main_layout.addLayout(widget_layout)

        # Set the main layout for the window
        self.setLayout(main_layout)

        self.setGeometry(100, 100, 500, 300)
        self.setWindowTitle('PyQt5 Widget Example')
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    sys.exit(app.exec_())
