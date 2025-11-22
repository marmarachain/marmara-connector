import sys
import platform
import qtawesome as qta
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt5.QtCore import pyqtSlot, QTranslator
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / "ui" / "generated"))

from ui.generated.ui_mainwindow import Ui_MainWindow
from styles.mainwindow_style import MainWindowStyle
from preferences_dialog import PreferencesDialog
from settings_manager import SettingsManager


class MainApp(QMainWindow):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        # UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.style = MainWindowStyle(self.ui)
        self.settings = SettingsManager()
        self.settings.restore_geometry(self)
        # mainApp attributes
        self.os_name = platform.system()
        self.trans = QTranslator(self)
        self.is_local = None
        self.selected_styleSheet = ""
        self.current_language = 'EN'
        self.current_font_size = int(self.settings.get_font_size())
        # Load from settings
        self.load_from_settings()
        # Connect signal & slot
        #    Menu Actions
        self.ui.actionToolbar.triggered.connect(self.toggleToolbar)
        self.ui.toolBar.visibilityChanged.connect(self.syncActionToolbar)
        self.ui.actionLogout.triggered.connect(self.logout_host)
        self.ui.actionPreferences.triggered.connect(self.open_settings)
        #   Login page Host Selection
        self.ui.local_button.clicked.connect(self.local_selection)
        self.ui.remote_button.clicked.connect(self.remote_selection)
        self.ui.home_button.clicked.connect(self.host_selection)
        self.ui.serveradd_button.clicked.connect(self.server_add_selected)
        self.ui.serveredit_button.clicked.connect(self.server_edit_selected)
        self.ui.connect_button.clicked.connect(self.server_connect)
        self.ui.serverpw_lineEdit.returnPressed.connect(self.server_connect)
        ##  Add Server Settings page
        self.ui.servercancel_button.clicked.connect(self.add_cancel_selected)
        self.ui.home_button.setVisible(False)
        #   Side Panel
        self.ui.fontsize_plus_button.clicked.connect(self.increase_fontsize)
        self.ui.fontsize_minus_button.clicked.connect(self.decrease_fontsize)

    def load_from_settings(self):
        style = str(self.settings.get_style())
        icon_color = 'black' if style == 'light' else '#eff0f1'
        self.selected_styleSheet = "" if style == "light" else self.settings.read_style(style + '.qss')
        self.style.set_icon_color(str(icon_color))
        self.setStyleSheet(self.selected_styleSheet)
        self.style.set_font_size(self.current_font_size)
        if self.current_language != self.settings.get_language():
            self.change_language(self.settings.get_language())

    def change_language(self, lang_name):
        language_files = self.settings.language_files()
        if lang_name in language_files:
            self.trans.load(str(language_files[lang_name]))
            QApplication.instance().installTranslator(self.trans)
            self.ui.retranslateUi(self)
            self.current_language = lang_name

    def closeEvent(self, event):
        """Save settings when the window is closed."""
        self.settings.save_geometry(self)
        super().closeEvent(event)

    @pyqtSlot()
    def increase_fontsize(self):
        if self.current_font_size <= 20:
            self.current_font_size += 1
            self.style.set_font_size(self.current_font_size)
            self.settings.set_font_size(self.current_font_size)

    @pyqtSlot()
    def decrease_fontsize(self):
        if self.current_font_size >= 9:
            self.current_font_size -= 1
            self.style.set_font_size(self.current_font_size)
            self.settings.set_font_size(self.current_font_size)

    @pyqtSlot()
    def local_selection(self):
        self.ui.main_tab.setCurrentIndex(1)
        self.is_local = True
        self.ui.host_name_label.setText(self.tr('LOCAL'))
        print(f"is_local : {self.is_local}")

    @pyqtSlot()
    def remote_selection(self):
        self.ui.login_stackedWidget.setCurrentIndex(1)
        self.ui.home_button.setVisible(True)
        self.is_local = False

    def host_selection(self):
        self.ui.main_tab.setCurrentIndex(0)
        self.ui.login_stackedWidget.setCurrentIndex(0)
        self.ui.login_message_label.clear()
        self.ui.host_name_label.clear()
        self.ui.home_button.setVisible(False)

    @pyqtSlot()
    def logout_host(self):
        self.ui.current_pubkey_value.clear()
        self.ui.currentaddress_value.clear()
        self.host_selection()

    def syncActionToolbar(self, visible):
        self.ui.actionToolbar.setChecked(visible)

    def toggleToolbar(self):
        self.ui.toolBar.setVisible(self.actionToolbar.isChecked())

    def open_settings(self):
        dialog = PreferencesDialog(self.settings)
        dialog.setWindowIcon(qta.icon('ph.gear-six'))
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.load_from_settings()

    @pyqtSlot()
    def server_connect(self):
        print('use pw and connect via ssh')

    @pyqtSlot()
    def server_add_selected(self):
        self.ui.login_stackedWidget.setCurrentIndex(2)

    @pyqtSlot()
    def add_cancel_selected(self):
        self.ui.add_servername_lineEdit.setText("")
        self.ui.add_serverusername_lineEdit.setText("")
        self.ui.add_serverip_lineEdit.setText("")
        self.remote_selection()

    @pyqtSlot()
    def server_edit_selected(self):
        self.ui.login_stackedWidget.setCurrentIndex(3)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
