from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie
from PyQt5 import QtCore
from fbs_runtime.application_context.PyQt5 import ApplicationContext



class LoadingScreen(QWidget,ApplicationContext):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 200)
        self.setWindowFlags(
           Qt.SplashScreen
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowModality(Qt.ApplicationModal)

        self.label_animation = QLabel(self)
        self.label_animation.setStyleSheet("background: transparent;")
        self.movie = QMovie(self.get_resource("images")+"/fluid-loader.gif")
        self.movie.setScaledSize(QtCore.QSize(200, 200))
        self.label_animation.setMovie(self.movie)
        self.label_animation.setStyleSheet("background-color: rgba(0,0,0,0%)")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def startAnimation(self):
        self.movie.start()
        self.show()

    def stopAnimotion(self):
        self.movie.stop()
        self.close()

