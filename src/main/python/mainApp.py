import json
import time

from PyQt5.QtCore import QThread, pyqtSlot

from qtguidesign import Ui_MainWindow
from PyQt5 import QtWidgets
import configuration
import marmarachain_rpc
import remote_connection
import chain_args as cp


class MarmaraMain(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        self.setupUi(self)
        #   Default Settings
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.chain_status= False
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)

        #   Login page Server authentication
        self.home_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.connect_button.clicked.connect(self.server_connect)
        self.serverpw_lineEdit.returnPressed.connect(self.server_connect)
        self.serveredit_button.clicked.connect(self.server_edit_selected)
        #  Add Server Settings page
        self.add_serversave_button.clicked.connect(self.save_server_settings)
        self.servercancel_button.clicked.connect(self.add_cancel_selected)
        # Edit Server Settings page
        self.edit_serversave_button.clicked.connect(self.edit_server_settings)
        self.serverdelete_button.clicked.connect(self.delete_server_setting)
        # System page
        self.stopchain_Button.clicked.connect(self.stop_chain)
        # Tread setup
        self.thread_getinfo = QThread()
        self.thread_getchain = QThread()
        self.thread_chainpid = QThread()
        self.thread_stopchain = QThread()
        self.thread_getaddresses = QThread()
        self.thread_getbalance = QThread()

    def host_selection(self):
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)

    def local_selection(self):
        self.main_tab.setCurrentIndex(1)
        marmarachain_rpc.set_connection_local()
        self.chain_init()

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        marmarachain_rpc.set_connection_remote()

    @pyqtSlot()
    def server_connect(self):
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        selected_server_info = selected_server_info.split(",")
        remote_connection.set_server_connection(ip=selected_server_info[2], username=selected_server_info[1],
                                                pw=self.serverpw_lineEdit.text())
        validate = remote_connection.check_server_connection()
        if validate:
            self.login_message_label.setText(str(validate))
        else:
            self.main_tab.setCurrentIndex(1)
        self.chain_init()

    def worker_thread(self, thread, worker, command=None):
        if command:
            worker.set_command(command)
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        # thread.started.connect(worker.do_execute_rpc)
        thread.start()
        return worker

    def chain_init(self):
        print('chain_status ' + str(self.chain_status))
        if not self.chain_status:
            self.check_chain()
        if self.chain_status:
            self.get_getinfo()
            self.getaddresses()


    def check_chain(self):
        self.bottom_message_label.setText('Checking marmarachain')
        marmara_pid = marmarachain_rpc.handle_rpc(cp.marmara_pid)
        print(len(marmara_pid[0]))
        if len(marmara_pid[0]) == 0:
            print('chain is start command')
            marmarachain_rpc.start_chain()
        self.worker_chain_pid = marmarachain_rpc.RpcHandler()
        check_pid_thread = self.worker_thread(self.thread_chainpid, self.worker_chain_pid)
        self.thread_chainpid.started.connect(self.worker_chain_pid.chain_pid)
        check_pid_thread.daemon_pid.connect(self.chain_check_finished)

    def chain_check_finished(self, result_out):
        if not result_out:
            self.bottom_message_label.setText('Chain start error: No pid')
        if result_out:
            print('pid is ' + result_out)
            self.is_chain_ready()

    @pyqtSlot()
    def is_chain_ready(self):
        self.worker_getchain = marmarachain_rpc.RpcHandler()
        command = cp.getinfo
        chain_ready_thread = self.worker_thread(self.thread_getchain, self.worker_getchain, command)
        self.thread_getchain.started.connect(self.worker_getchain.is_chain_ready)
        chain_ready_thread.command_out.connect(self.chain_ready_result)
        chain_ready_thread.finished.connect(self.chain_init)

    @pyqtSlot(tuple)
    def chain_ready_result(self, result_out):
        if result_out[0]:
            print('chain ready finished')
            self.chain_status = True
        elif result_out[1]:
            time.sleep(2)
            print_result = ""
            for line in str(result_out[1]).splitlines():
                print_result = print_result + ' ' + str(line)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def stop_chain(self):
        if self.chain_status:
            self.worker_stopchain = marmarachain_rpc.RpcHandler()
            command = cp.stop
            stop_chain_thread = self.worker_thread(self.thread_stopchain, self.worker_stopchain, command)
            self.thread_stopchain.started.connect(self.worker_stopchain.stopping_chain)
            stop_chain_thread.command_out.connect(self.result_stopchain)
        else:
            self.bottom_message_label.setText('chain is not ready')

    @pyqtSlot(tuple)
    def result_stopchain(self, result_out):
        if result_out[0]:
            print_result = ""
            for line in str(result_out[0]).splitlines():
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)
        if len(result_out[0]) == 0:
            self.bottom_message_label.setText('chain stopped')
            self.chain_status = False
        elif result_out[1]:
            print_result = ""
            for line in str(result_out[1]).splitlines():
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def get_getinfo(self):
        self.worker_getinfo = marmarachain_rpc.RpcHandler()  # worker setting
        command = cp.getinfo                                 # setting command
        getinfo_thread = self.worker_thread(self.thread_getinfo, self.worker_getinfo, command)  # putting in to thread
        self.thread_getinfo.started.connect(self.worker_getinfo.do_execute_rpc)      # executing respective worker class function
        getinfo_thread.command_out.connect(self.set_getinfo_result)            # getting results from socket

    @pyqtSlot(tuple)
    def set_getinfo_result(self, result_out):
        if result_out[0]:
            getinfo_result = result_out[0]
            getinfo_result = json.loads(getinfo_result)
            self.bottom_message_label.setText('loading values')

            self.difficulty_value_label.setText(str(getinfo_result['difficulty']))
            self.currentblock_value_label.setText(str(getinfo_result['blocks']))
            self.longestchain_value_label.setText(str(getinfo_result['longestchain']))
            self.connections_value_label.setText(str(getinfo_result['connections']))

            self.bottom_message_label.setText('finished')
            if getinfo_result.get('pubkey') is None:
                self.bottom_message_label.setText('pubkey is not set')
        elif result_out[1]:
            getinfo_result = str(result_out[1]).splitlines()
            print_result = ""
            for line in getinfo_result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def getaddresses(self):
        self.worker_getaddresses = marmarachain_rpc.RpcHandler()
        command = cp.getaddressesbyaccount
        getaddresses_thread = self.worker_thread(self.thread_getaddresses, self.worker_getaddresses, command)
        self.thread_getaddresses.started.connect(self.worker_getaddresses.do_execute_rpc)
        getaddresses_thread.command_out.connect(self.set_getaddresses_result)

    @pyqtSlot(tuple)
    def set_getaddresses_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            addresses = json.loads(result_out[0])
            for address in addresses:
                print(address)
                self.getbalance(address)
            # self.getlistaddresgroup(result_out[0])
        elif result_out[1]:
            print(result_out[1])

    @pyqtSlot()
    def getbalance(self, address):
        self.worker_getbalance = marmarachain_rpc.RpcHandler()
        command = cp.getbalance + ' ' + address
        getbalance_thread = self.worker_thread(self.thread_getbalance, self.worker_getbalance, command)
        self.thread_getbalance.started.connect(self.worker_getbalance.do_execute_rpc)
        getbalance_thread.command_out.connect(self.set_getbalance_result)

    @pyqtSlot(tuple)
    def set_getbalance_result(self, result_out):
        print(result_out)
        print(result_out[0])
        print(json.loads(result_out[0]))
        if json.loads(result_out[0]) == 0.0:
            print('no balance')
        elif result_out[1]:
            print(result_out[1])

    # -------------------------------------------------------------------
    # Remote Host adding , editing, deleting and  saving in conf file
    # --------------------------------------------------------------------

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

    #----------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ui = MarmaraMain()
    ui.show()
    app.exec_()
