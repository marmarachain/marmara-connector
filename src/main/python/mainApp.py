from qtguidesign import Ui_MainWindow
from PyQt5 import QtWidgets
import configuration
import marmarachain_rpc as mc


class MarmaraMain(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        self.setupUi(self)
        #   Default Settings
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)

        #   Login page Server authentication
        self.home_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.connect_button
        self.serveredit_button.clicked.connect(self.server_edit_selected)
        #  Add Server Settings page
        self.add_serversave_button.clicked.connect(self.save_server_settings)
        self.servercancel_button.clicked.connect(self.add_cancel_selected)
        # Edit Server Settings page
        self.edit_serversave_button.clicked.connect(self.edit_server_settings)
        self.serverdelete_button.clicked.connect(self.delete_server_setting)

    def host_selection(self):
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)

    def local_selection(self):
        self.main_tab.setCurrentIndex(1)
        mc.set_connection_local()
        mc.getinfo()

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        mc.set_connection_remote()
        mc.getinfo()


    def server_add_selected(self):
        self.login_stackedWidget.setCurrentIndex(2)



    def add_cancel_selected(self):
        self.add_servername_lineEdit.setText("")
        self.add_serverusername_lineEdit.setText("")
        self.add_serverip_lineEdit.setText("")
        self.remote_selection()

    def server_edit_selected(self):
        self.login_stackedWidget.setCurrentIndex(3)
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        selected_server_info = selected_server_info.split(",")
        self.edit_servername_lineEdit.setText(selected_server_info[0])
        self.edit_serverusername_lineEdit.setText(selected_server_info[1])
        self.edit_serverip_lineEdit.setText(selected_server_info[2])

    def save_server_settings(self):
        if self.add_servername_lineEdit.text() != "" and self.add_serverusername_lineEdit.text() != "" and self.add_serverip_lineEdit.text() != "":
            configuration.ServerSettings().save_file(server_name=self.add_servername_lineEdit.text(),
                                                     server_username=self.add_serverusername_lineEdit.text(),
                                                     server_ip=self.add_serverip_lineEdit.text())
            self.add_servername_lineEdit.setText("")
            self.add_serverusername_lineEdit.setText("")
            self.add_serverip_lineEdit.setText("")
            self.get_server_combobox_names()
            self.login_stackedWidget.setCurrentIndex(1)
        else:
            print('write all values')

    def get_server_combobox_names(self):
        server_name_list = []
        server_settings_list = configuration.ServerSettings().read_file()
        self.server_comboBox.clear()
        for setting_list in server_settings_list:
            server_name_list.append(setting_list.split(",")[0])
        self.server_comboBox.addItems(server_name_list)

    def edit_server_settings(self):
        if self.edit_servername_lineEdit.text() != "" and self.edit_serverusername_lineEdit.text() != "" and self.edit_serverip_lineEdit.text() != "":
            server_list = configuration.ServerSettings().read_file()
            del server_list[self.server_comboBox.currentIndex()]
            configuration.ServerSettings().delete_record(server_list)
            configuration.ServerSettings().save_file(server_name=self.edit_servername_lineEdit.text(),
                                                     server_username=self.edit_serverusername_lineEdit.text(),
                                                     server_ip=self.edit_serverip_lineEdit.text())
            self.login_stackedWidget.setCurrentIndex(1)
            self.edit_servername_lineEdit.setText("")
            self.edit_serverusername_lineEdit.setText("")
            self.edit_serverip_lineEdit.setText("")
            self.get_server_combobox_names()
            self.login_stackedWidget.setCurrentIndex(1)
        else:
            print('write all values')


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
