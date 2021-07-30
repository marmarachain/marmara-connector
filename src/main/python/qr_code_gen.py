from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5 import QtCore

import qrcode


# Image class for QR code
class Image(qrcode.image.base.BaseImage):

    # constructor
    def __init__(self, border, width, box_size):
        # assigning border
        self.border = border
        # assigning  width
        self.width = width
        # assigning box size
        self.box_size = box_size
        # creating size
        size = (width + border * 2) * box_size
        # image
        self._image = QImage(size, size, QImage.Format_RGB16)
        # initial image as white
        self._image.fill(QtCore.Qt.white)

    # pixmap method
    def pixmap(self):
        # returns image
        return QPixmap.fromImage(self._image)

    # drawrect method for drawing rectangle
    def drawrect(self, row, col):
        # creating painter object
        painter = QPainter(self._image)
        # drawing rectangle
        painter.fillRect(
            (col + self.border) * self.box_size,
            (row + self.border) * self.box_size,
            self.box_size, self.box_size,
            QtCore.Qt.black)
