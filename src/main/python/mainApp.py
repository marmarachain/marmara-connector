import json
import time

from qtguidesign import Ui_MainWindow
from PyQt5 import QtWidgets
import configuration
import marmarachain_rpc
import remote_connection

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
        self.connect_button.clicked.connect(self.server_connect)
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
        marmarachain_rpc.set_connection_local()
        self.chain_initilazation()

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        marmarachain_rpc.set_connection_remote()

    def server_connect(self):
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        selected_server_info = selected_server_info.split(",")
        remote_connection.set_server_connection(ip=selected_server_info[2], username=selected_server_info[1], pw=self.serverpw_lineEdit.text())
        validate = remote_connection.check_server_connection()
        if validate:
            self.login_message_label.setText(str(validate))
        else:
            self.main_tab.setCurrentIndex(1)
        self.chain_initilazation()

    def chain_initilazation(self):
        self.bottom_message_label.setText('Checking marmarachain')
        if not marmarachain_rpc.mcl_chain_status().read():
            marmarachain_rpc.start_chain()
        while True:
            if marmarachain_rpc.mcl_chain_status().read():
                break
            time.sleep(2)
            self.bottom_message_label.setText('Chain is not started')
        while True:
            if marmarachain_rpc.mcl_chain_status().read():
                break
            print('Chain not started')
            time.sleep(1)

        while True:
            getinfo = marmarachain_rpc.getinfo()
            getinfo_result = getinfo[0].read()  # getting result of stdout
            if getinfo_result:
                getinfo_result = json.loads(getinfo_result)
                print(getinfo_result)
                self.bottom_message_label.setText('loading values')

                self.difficulty_value_label.setText(str(getinfo_result['difficulty']))
                self.currentblock_value_label.setText(str(getinfo_result['blocks']))
                self.longestchain_value_label.setText(str(getinfo_result['longestchain']))
                self.connections_value_label.setText(str(getinfo_result['connections']))

                self.bottom_message_label.setText('finished')
                if getinfo_result.get('pubkey') is None:
                    self.bottom_message_label.setText('pubkey is not set')
                marmarachain_rpc.rpc_close(getinfo)
                break
            getinfo_result = getinfo[1].read()   # getting result of stderr
            if getinfo_result:
                getinfo_result = str(getinfo_result).replace("b'", ' ').replace("\\n", " ")
                print(getinfo_result)
                self.bottom_message_label.setText(str(getinfo_result))
                self.login_message_label.setText(str(getinfo_result))
                marmarachain_rpc.rpc_close(getinfo)
                time.sleep(2)



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
