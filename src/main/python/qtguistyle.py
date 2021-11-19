from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPixmap
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from qtguidesign import Ui_MainWindow
from PyQt5.uic import loadUi
import qtawesome as qta

icon_path = ApplicationContext().get_resource("images")
style_path = ApplicationContext().get_resource("styles")


class GuiStyle(Ui_MainWindow):

    def __init__(self):
        # loadUi("qtguidesign.ui", self)  #  loadin from qtguidesign.ui
        self.setupUi(self)  # loading from qtguidesign.py
        # setting params
        self.icon_path = icon_path
        self.stopchain_button.setIcon(QtGui.QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_button.setIconSize(QtCore.QSize(32, 32))
        self.inactive_icon_pixmap = QPixmap(self.icon_path + '/circle-inactive.png')
        self.active_icon_pixmap = QPixmap(self.icon_path + '/circle-active.png')
        self.chainstatus_label_value.setPixmap(self.inactive_icon_pixmap)
        self.chainsync_label_value.setPixmap(self.inactive_icon_pixmap)
        self.coffee_pixmap = QPixmap(self.icon_path + '/Coffee-icon.png')
        self.coffee_icon_label.setPixmap(self.coffee_pixmap)
        self.staking_button.setVisible(False)
        self.staking_button = ToggleSwitch(self.miningstatus_frame)
        self.staking_button.setObjectName("staking_button")
        self.gridLayout_17.addWidget(self.staking_button, 1, 1, 1, 1)
        self.mining_button.setVisible(False)
        self.mining_button = ToggleSwitch(self.miningstatus_frame)
        self.mining_button.setObjectName("mining_button")
        self.gridLayout_17.addWidget(self.mining_button, 3, 1, 1, 1)
        self.stats_pie_frame.setContentsMargins(0, 0, 0, 0)
        self.stats_layout = QtWidgets.QHBoxLayout(self.stats_pie_frame)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        self.cal_exchange_icon_button.setIcon(QtGui.QIcon(self.icon_path + '/send_recive_icon.png'))
        self.cal_exchange_icon_button.setIconSize(QtCore.QSize(24, 24))
        self.cal_exchange_icon_button.setStyleSheet("border-color: black; border-radius: 10px")
        self.set_icon_color('black')

    def set_icon_color(self, color):
        # Chain page
        self.download_blocks_button.setIcon(qta.icon('mdi.cloud-download-outline', color=color))
        self.download_blocks_button.setIconSize(QtCore.QSize(24, 24))
        self.refresh_walletaddresses_button.setIcon(qta.icon('mdi.refresh', color=color))
        self.refresh_walletaddresses_button.setIconSize(QtCore.QSize(24, 24))
        self.check_fork_button.setIcon(qta.icon('mdi.directions-fork', color=color))
        self.check_fork_button.setIconSize(QtCore.QSize(24, 24))
        # menubar
        self.actionQuit.setIcon(qta.icon('mdi.exit-to-app', color=color))
        # mcl tab
        self.mcl_tab.setTabIcon(0, qta.icon('fa.chain', color=color))
        self.mcl_tab.setTabIcon(1, qta.icon('fa5s.wallet', color=color))
        self.mcl_tab.setTabIcon(2, qta.icon('fa5s.coins', color=color))
        self.mcl_tab.setTabIcon(3, qta.icon('fa5b.hornbill', color=color))
        self.mcl_tab.setTabIcon(4, qta.icon('fa5.address-card', color=color))
        self.mcl_tab.setTabIcon(5, qta.icon("mdi.chart-areaspline", color=color))
        self.mcl_tab.setTabIcon(6, qta.icon("mdi.bulletin-board", color=color))
        # self.mcl_tab.setIconSize(QtCore.QSize(24,24))
        # Side panel
        self.getinfo_refresh_button.setIcon(qta.icon('ei.refresh', color=color))
        self.getinfo_refresh_button.setIconSize(QtCore.QSize(24, 24))

        self.copyaddress_button.setIcon(qta.icon('fa5.copy', color=color))
        self.copyaddress_button.setIconSize(QtCore.QSize(24, 24))
        self.copypubkey_button.setIcon(qta.icon('mdi.key-change', color=color))
        self.copypubkey_button.setIconSize(QtCore.QSize(24, 24))
        self.support_pushButton.setText('Support')
        self.support_pushButton.setEnabled(False)

        # Wallet page button icons
        self.lock_button.setIcon(QtGui.QIcon(qta.icon('fa5s.lock', color=color)))
        self.lock_button.setIconSize(QtCore.QSize(32, 32))
        self.unlock_button.setIcon(QtGui.QIcon(qta.icon('fa5s.unlock-alt', color=color)))
        self.unlock_button.setIconSize(QtCore.QSize(32, 32))
        self.addressamount_refresh_button.setIcon(qta.icon('mdi.refresh', color=color))
        self.addressamount_refresh_button.setIconSize(QtCore.QSize(24, 24))
        # Coin Send-Receive page
        self.coinsend_button.setIcon(qta.icon('mdi.database-export', color=color))
        self.coinsend_button.setIconSize(QtCore.QSize(24, 24))
        self.transaction_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search', color=color)))
        self.transaction_search_button.setIconSize(QtCore.QSize(24, 24))
        # Credit loops page
        self.looprequest_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search', color=color)))
        self.looprequest_search_button.setIconSize(QtCore.QSize(24, 24))

        self.lq_pubkey_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search', color=color)))
        self.lq_pubkey_search_button.setIconSize(QtCore.QSize(24, 24))

        self.lq_txid_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search', color=color)))
        self.lq_txid_search_button.setIconSize(QtCore.QSize(24, 24))

        self.activeloops_search_button.setIcon(QtGui.QIcon(qta.icon('fa.search', color=color)))
        self.activeloops_search_button.setIconSize(QtCore.QSize(24, 24))
        self.holderloops_search_button.setIcon(qta.icon('fa.search', color=color))
        self.holderloops_search_button.setIconSize(QtCore.QSize(24, 24))
        # Stats
        self.stats_refresh_pushButton.setIcon(qta.icon('mdi.refresh', color=color))
        self.stats_refresh_pushButton.setIconSize(QtCore.QSize(24, 24))
        self.stats_calculate_pushButton.setIcon(qta.icon('mdi.calculator-variant-outline', color=color))
        self.stats_calculate_pushButton.setIconSize(QtCore.QSize(24, 24))
        # Market
        self.exchange_market_request_button.setIcon(qta.icon('mdi.arrow-bottom-left-thick', color=color))
        self.exchange_market_request_button.setIconSize(QtCore.QSize(24, 24))

    def get_style(self, s_type):
        file = open(style_path + '/' + s_type, "r")
        style = file.read()
        file.close()
        return style


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
