from PyQt5 import QtGui, QtCore
from PyQt5.uic import loadUi
from fbs_runtime.application_context.PyQt5 import ApplicationContext

class GuiStyle(ApplicationContext):

    def __init__(self):
        loadUi("qtguidesign.ui", self)
        # setting params
        self.icon_path = self.get_resource("images")
        # stop button style
        self.stopchain_Button.setIcon(QtGui.QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_Button.setIconSize(QtCore.QSize(32, 32))

