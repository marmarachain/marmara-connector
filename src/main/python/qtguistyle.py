from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from qtguidesign import Ui_MainWindow
from PyQt5.uic import loadUi
import qtawesome as qta

icon_path = ApplicationContext().get_resource("images")


class GuiStyle(Ui_MainWindow):

    def __init__(self):
        # loadUi("qtguidesign.ui", self)  #  loadin from qtguidesign.ui
        self.setupUi(self)  # loading from qtguidesign.py
        # setting params
        self.icon_path = icon_path
        # stop button style
        self.stopchain_button.setIcon(QtGui.QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_button.setIconSize(QtCore.QSize(32, 32))
        # menubar
        self.actionQuit.setIcon(QtGui.QIcon(self.icon_path + '/exit_icon.png'))
        # mcl tab
        self.mcl_tab.setTabIcon(0, QtGui.QIcon(self.icon_path + '/chain_icon.png'))
        self.mcl_tab.setTabIcon(1, QtGui.QIcon(self.icon_path + '/wallet_icon.png'))
        self.mcl_tab.setTabIcon(2, QtGui.QIcon(self.icon_path + '/credit.png'))
        self.mcl_tab.setTabIcon(3, QtGui.QIcon(qta.icon('fa5b.hornbill')))
        self.mcl_tab.setTabIcon(4, QtGui.QIcon(self.icon_path + '/persons.png'))
        # Side panel
        self.getinfo_refresh_button.setIcon(QtGui.QIcon(self.icon_path + '/refresh_icon.png'))
        self.getinfo_refresh_button.setIconSize(QtCore.QSize(32, 32))
        self.chainstatus_button.setIcon(QtGui.QIcon(self.icon_path + '/circle-inactive.png'))
        self.chainstatus_button.setStyleSheet("border-color: red;border-radius: 10px")
        self.chainstatus_button.setIconSize(QtCore.QSize(24, 24))
        self.chainsync_button.setIcon(QtGui.QIcon(self.icon_path + '/circle-inactive.png'))
        self.chainsync_button.setStyleSheet("border-color: red;border-radius: 10px")
        self.chainsync_button.setIconSize(QtCore.QSize(24, 24))
        self.staking_button.setVisible(False)
        self.staking_button = ToggleSwitch(self.miningstatus_frame)
        self.staking_button.setObjectName("staking_button")
        self.gridLayout_17.addWidget(self.staking_button, 1, 1, 1, 1)
        self.mining_button.setVisible(False)
        self.mining_button = ToggleSwitch(self.miningstatus_frame)
        self.mining_button.setObjectName("mining_button")
        self.gridLayout_17.addWidget(self.mining_button, 3, 1, 1, 1)
        self.copyaddress_button.setIcon(QtGui.QIcon(self.icon_path + '/copy_wallet_icon_.png'))
        self.copyaddress_button.setIconSize(QtCore.QSize(24, 24))
        self.copypubkey_button.setIcon(QtGui.QIcon(self.icon_path + '/copy_key_icon.png'))
        self.copypubkey_button.setIconSize(QtCore.QSize(24, 24))
        # Wallet page button icons
        self.lock_button.setIcon(QtGui.QIcon(qta.icon('fa5s.lock')))
        self.lock_button.setIconSize(QtCore.QSize(32, 32))
        self.unlock_button.setIcon(QtGui.QIcon(qta.icon('fa5s.unlock-alt')))
        self.unlock_button.setIconSize(QtCore.QSize(32, 32))
        self.addressamount_refresh_button.setIcon(QtGui.QIcon(self.icon_path + '/refresh_icon.png'))
        self.addressamount_refresh_button.setIconSize(QtCore.QSize(24, 24))
        # Coin Send-Receive page
        self.coinsend_button.setIcon(QtGui.QIcon(self.icon_path + '/send_coin_icon.png'))
        self.coinsend_button.setIconSize(QtCore.QSize(24, 24))
        self.transaction_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search')))
        self.transaction_search_button.setIconSize(QtCore.QSize(24, 24))
        # Credit loops page
        self.looprequest_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search')))
        self.looprequest_search_button.setIconSize(QtCore.QSize(24, 24))

        self.lq_pubkey_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search')))
        self.lq_pubkey_search_button.setIconSize(QtCore.QSize(24, 24))

        self.lq_txid_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search')))
        self.lq_txid_search_button.setIconSize(QtCore.QSize(24, 24))

        self.activeloops_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search')))
        self.activeloops_search_button.setIconSize(QtCore.QSize(24, 24))
        self.transferableloops_search_button.setIcon(qta.icon('fa.search'))
        self.transferableloops_search_button.setIconSize(QtCore.QSize(24, 24))
        # line edit cursor focus
        self.serverpw_lineEdit.setFocus()
        self.add_serverip_lineEdit.setFocus()
        self.add_servername_lineEdit.setFocus()
        self.add_serverusername_lineEdit.setFocus()
        self.edit_serverip_lineEdit.setFocus()
        self.edit_servername_lineEdit.setFocus()
        self.edit_serverusername_lineEdit.setFocus()


class ToggleSwitch(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setCheckable(True)
        self.setMinimumWidth(66)
        self.setMinimumHeight(22)

    def paintEvent(self, event):
        label = "ON" if self.isChecked() else "OFF"
        bg_color = Qt.green if self.isChecked() else Qt.red

        radius = 10
        width = 32
        center = self.rect().center()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.translate(center)
        painter.setBrush(QtGui.QColor(0, 0, 0))

        pen = QtGui.QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)

        painter.drawRoundedRect(QRect(-width, -radius, 2 * width, 2 * radius), radius, radius)
        painter.setBrush(QtGui.QBrush(bg_color))
        sw_rect = QRect(-radius, -radius, width + radius, 2 * radius)
        if not self.isChecked():
            sw_rect.moveLeft(-width)
        painter.drawRoundedRect(sw_rect, radius, radius)
        painter.drawText(sw_rect, Qt.AlignCenter, label)
