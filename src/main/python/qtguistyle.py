from PyQt5 import QtGui, QtCore
from PyQt5.uic import loadUi
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from qtguidesign import Ui_MainWindow

class GuiStyle(ApplicationContext ,Ui_MainWindow):

    def __init__(self):
        # loadUi("qtguidesign.ui", self)  #  loadin from qtguidesign.ui
        self.setupUi(self)   # loading from qtguidesign.py
        # setting params
        self.icon_path = self.get_resource("images")
        # stop button style
        self.stopchain_button.setIcon(QtGui.QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_button.setIconSize(QtCore.QSize(32, 32))

