import sys
import platform
import qtawesome as qta
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt5.QtCore import pyqtSlot, QTranslator
from qtguistyle import GuiStyle
from settings import *
from file_operations import *



class MainApp(QMainWindow, GuiStyle):

    def __init__(self, parent=None):
        super(MainApp, self).__init__(parent)
        restore_geometry(self)
        # mainApp attributes
        self.os_name = platform.system()
        print(self.os_name)
        self.trans = QTranslator(self)
        self.is_local = None
        self.selected_styleSheet = ""
        self.current_language = 'EN'
        self.current_font_size = int(get_setting("font_size", 12))
        # Load from settings
        self.load_from_settings()
        # Connect signal & slot
        #    Menu Actions
        self.actionToolbar.triggered.connect(self.toggleToolbar)
        self.toolBar.visibilityChanged.connect(self.syncActionToolbar)
        self.actionLogout.triggered.connect(self.logout_host)
        self.actionSettings.triggered.connect(self.open_settings)
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)
        self.home_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.serveredit_button.clicked.connect(self.server_edit_selected)
        self.connect_button.clicked.connect(self.server_connect)
        self.serverpw_lineEdit.returnPressed.connect(self.server_connect)
        ##  Add Server Settings page
        self.servercancel_button.clicked.connect(self.add_cancel_selected)


        self.home_button.setVisible(False)
        #   Side Panel
        self.fontsize_plus_button.clicked.connect(self.increase_fontsize)
        self.fontsize_minus_button.clicked.connect(self.decrease_fontsize)

    def load_from_settings(self):
        style = str(get_setting("style", 'light'))
        icon_color = 'black'
        if style != 'light':
            icon_color = '#eff0f1'
            self.selected_styleSheet = get_style(style + '.qss')
        else:
            self.selected_styleSheet = ""
        self.set_icon_color(str(icon_color))
        self.setStyleSheet(self.selected_styleSheet)
        if get_setting("font_size") is not None:
            if int(get_setting("font_size")) != self.current_font_size:
                self.current_font_size = int(get_setting("font_size"))
        self.set_font_size(self.current_font_size)
        if self.current_language != get_setting('language', 'EN'):
            self.change_language(get_setting('language'))

    def change_language(self, lang_name):
        language_files = {file.stem: file for file in language_path.iterdir() if file.suffix == '.qm'}
        if lang_name in language_files:
            self.trans.load(str(language_files[lang_name]))
            QApplication.instance().installTranslator(self.trans)
            self.retranslateUi(self)
            self.current_language = lang_name

    def closeEvent(self, event):
        """Save settings when the window is closed."""
        save_geometry(self)
        set_setting("font_size", self.current_font_size)
        super().closeEvent(event)

    @pyqtSlot()
    def increase_fontsize(self):
        if self.current_font_size <= 20:
            self.current_font_size += 1
            self.set_font_size(self.current_font_size)
            set_setting('font_size', self.current_font_size)

    @pyqtSlot()
    def decrease_fontsize(self):
        if self.current_font_size >= 9:
            self.current_font_size -= 1
            self.set_font_size(self.current_font_size)
            set_setting('font_size', self.current_font_size)

    @pyqtSlot()
    def local_selection(self):
        self.main_tab.setCurrentIndex(1)
        self.is_local = True
        self.host_name_label.setText(self.tr('LOCAL'))
        print(f"is_local : {self.is_local}")

    @pyqtSlot()
    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.home_button.setVisible(True)
        self.is_local = False
        print(f"is_local : {self.is_local}")

    def host_selection(self):
        self.main_tab.setCurrentIndex(0)
        self.login_stackedWidget.setCurrentIndex(0)
        self.login_message_label.clear()
        self.host_name_label.clear()
        self.home_button.setVisible(False)

    @pyqtSlot()
    def logout_host(self):
        self.current_pubkey_value.clear()
        self.currentaddress_value.clear()
        self.host_selection()

    def syncActionToolbar(self, visible):
        self.actionToolbar.setChecked(visible)

    def toggleToolbar(self):
        self.toolBar.setVisible(self.actionToolbar.isChecked())

    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.setWindowIcon(qta.icon('ph.gear-six'))
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.load_from_settings()

    @pyqtSlot()
    def server_connect(self):
        print('use pw and connect via ssh')

    @pyqtSlot()
    def server_add_selected(self):
        self.login_stackedWidget.setCurrentIndex(2)

    @pyqtSlot()
    def add_cancel_selected(self):
        self.add_servername_lineEdit.setText("")
        self.add_serverusername_lineEdit.setText("")
        self.add_serverip_lineEdit.setText("")
        self.remote_selection()

    @pyqtSlot()
    def server_edit_selected(self):
        self.login_stackedWidget.setCurrentIndex(3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
