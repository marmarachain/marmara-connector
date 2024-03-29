from PyQt5.QtWidgets import QWidget, QLabel, QDesktopWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore
import qtguistyle


class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(150, 150)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)
        self.move(QDesktopWidget().availableGeometry().center() - QtCore.QPoint(75, 75))
        self.label_animation = QLabel(self)
        # self.label_animation.setStyleSheet("background: transparent;")
        self.movie = QMovie(qtguistyle.icon_path + "/connector-loader.gif")
        self.movie.setScaledSize(QtCore.QSize(150, 150))
        self.label_animation.setMovie(self.movie)
        # self.label_animation.setStyleSheet("background-color: rgba(0,0,0,0%)")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def startAnimation(self):
        self.movie.start()
        self.show()

    def stopAnimation(self):
        self.movie.stop()
        self.close()
