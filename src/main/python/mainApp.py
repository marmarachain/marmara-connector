from qtguidesign import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import configuration


class MarmaraMain(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        self.setupUi(self)
        #   Default Settings
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.loginback_button.setVisible(False)
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)

        #   Login page Server authentication
        self.loginback_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.connect_button
        self.serveredit_button.clicked.connect(self.edit_server_settings)
        #  Server Settings page
        self.serversave_button.clicked.connect(self.save_server_settings)
        self.serverdelete_button.clicked.connect(self.delete_server_setting)

    def host_selection(self):
        self.login_stackedWidget.setCurrentIndex(0)
        self.login_label.setText('Select Host')
        self.loginback_button.setVisible(False)

    def local_selection(self):
        self.main_tab.setCurrentIndex(1)

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.login_label.setText('Select Server')
        self.get_server_combobox_names()
        self.loginback_button.setVisible(True)

    def server_add_selected(self):
        self.login_stackedWidget.setCurrentIndex(2)
        self.login_label.setText('Server Settings')

    def save_server_settings(self):
        if self.servername_lineEdit.text() != "" and self.serverusername_lineEdit.text() != "" and self.serverip_lineEdit.text() != "":
            configuration.ServerSettings().save_file(server_name=self.servername_lineEdit.text(),
                                                     server_username=self.serverusername_lineEdit.text(),
                                                     server_ip=self.serverip_lineEdit.text())
            self.login_stackedWidget.setCurrentIndex(1)
            self.servername_lineEdit.setText("")
            self.serverusername_lineEdit.setText("")
            self.serverip_lineEdit.setText("")
            self.get_server_combobox_names()

    def get_server_combobox_names(self):
        server_name_list = []
        server_settings_list = configuration.ServerSettings().read_file()
        self.server_comboBox.clear()
        for setting_list in server_settings_list:
            server_name_list.append(setting_list.split(",")[0])
        self.server_comboBox.addItems(server_name_list)

    def edit_server_settings(self):
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        self.login_stackedWidget.setCurrentIndex(2)
        selected_server_info = selected_server_info.split(",")
        self.servername_lineEdit.setText(selected_server_info[0])
        self.serverusername_lineEdit.setText(selected_server_info[1])
        self.serverip_lineEdit.setText(selected_server_info[2])

    def delete_server_setting(self):
        server_list = configuration.ServerSettings().read_file()
        del server_list[self.server_comboBox.currentIndex()]
        configuration.ServerSettings().delete_record(server_list)
        self.remote_selection()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ui = MarmaraMain()
    ui.show()
    app.exec_()
