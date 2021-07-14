import json
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSlot, QSize
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem
import configuration
import marmarachain_rpc
import remote_connection
import chain_args as cp
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from qtguidesign import Ui_MainWindow

class MarmaraMain(QMainWindow, Ui_MainWindow, ApplicationContext):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        self.setupUi(self)
        #   Default Settings
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.chain_status = False
        self.pubkey_status = False
        # paths settings
        self.icon_path = self.get_resource("images")

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
        self.stopchain_Button.setIcon(QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_Button.setIconSize(QSize(32, 32))
        self.addaddress_page_Button.clicked.connect(self.add_address)
        self.addresspage_back_Button.clicked.connect(self.back_chain_widget_index)
        self.privkey_page_Button.clicked.connect(self.see_privkey_page)
        self.privatekeypage_back_Button.clicked.connect(self.back_chain_widget_index)
        # Tread setup
        self.thread_getinfo = QThread()
        self.thread_getchain = QThread()
        self.thread_chainpid = QThread()
        self.thread_stopchain = QThread()
        self.thread_getaddresses = QThread()
        self.thread_setpubkey = QThread()
        # self.thread_validateddresses = QThread()
        # self.thread_getbalance = QThread()

        # Loading Gif
        # --------------------------------------------------
        # --------------------------------------------------

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
        if command:
            thread.started.connect(worker.do_execute_rpc)
        thread.start()
        return worker

    def chain_init(self):
        print('chain_status ' + str(self.chain_status))
        if not self.chain_status:
            self.check_chain()
        if self.chain_status:
            self.get_getinfo()
            time.sleep(0.3)
            self.getaddresses()

    def check_chain(self):
        self.bottom_message_label.setText('Checking marmarachain')
        marmara_pid = marmarachain_rpc.mcl_chain_status()
        print(len(marmara_pid[0]))
        if len(marmara_pid[0]) == 0:
            print('sending chain start command')
            marmarachain_rpc.start_chain()
        self.check_chain_pid()

    def check_chain_pid(self):
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
        self.worker_getchain.set_command(command)
        chain_ready_thread = self.worker_thread(self.thread_getchain, self.worker_getchain)
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
            stop_chain_thread = self.worker_thread(self.thread_stopchain, self.worker_stopchain)
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
            self.update_addresses_table()
        elif result_out[1]:
            print_result = ""
            for line in str(result_out[1]).splitlines():
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def get_getinfo(self):
        self.worker_getinfo = marmarachain_rpc.RpcHandler()  # worker setting
        command = cp.getinfo  # setting command
        getinfo_thread = self.worker_thread(self.thread_getinfo, self.worker_getinfo, command)  # putting in to thread
        # self.thread_getinfo.started.connect(self.worker_getinfo.do_execute_rpc)  # executing respective worker class function
        getinfo_thread.command_out.connect(self.set_getinfo_result)  # getting results from socket

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
            if getinfo_result.get('pubkey'):
                self.pubkey_status = True
            if getinfo_result.get('pubkey') is None:
                self.bottom_message_label.setText('pubkey is not set')
                self.pubkey_status = False
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
        getaddresses_thread = self.worker_thread(self.thread_getaddresses, self.worker_getaddresses)
        self.thread_getaddresses.started.connect(self.worker_getaddresses.get_addresses)
        getaddresses_thread.walletlist_out.connect(self.set_getaddresses_result)

    @pyqtSlot(list)
    def set_getaddresses_result(self, result_out):
        for row in result_out:
            row_number = result_out.index(row)
            self.addresses_tableWidget.setRowCount(len(result_out))
            self.addresses_tableWidget.autoScrollMargin()

            if self.pubkey_status:
                self.addresses_tableWidget.setColumnHidden(0, True)
            for item in row:
                btn_setpubkey = QPushButton('Set pubkey')
                print(item)
                self.addresses_tableWidget.setCellWidget(row_number, 0, btn_setpubkey)
                self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                self.addresses_tableWidget.setItem(row_number, (row.index(item) + 1), QTableWidgetItem(str(item)))
                self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(row.index(item) + 1, QtWidgets.QHeaderView.ResizeToContents)
                btn_setpubkey.clicked.connect(self.set_pubkey)


    def update_addresses_table(self):
        if self.pubkey_status:
            self.addresses_tableWidget.setColumnHidden(0, True)
        if not self.chain_status:
            self.addresses_tableWidget.setColumnHidden(0, False)
            rowcount = self.addresses_tableWidget.rowCount()
            self.addresses_tableWidget.setRowCount(rowcount)
            while True:
                btn_start = QPushButton('Start')
                btn_start.setIcon(QIcon(self.icon_path + "/start_icon.png"))
                # btn_start.setStyleSheet(
                #     "QPushButton {image: url(" + self.icon_path + "/start_icon.png); border: 0; width: 30px; height: 30px;}"
                #     "QPushButton::hover   {image: url(" + self.icon_path + "/start_icon_hover.png);border:0px}"
                #     "QPushButton::pressed {image: url(" + self.icon_path + "/start_icon_press.png);border:0px}"
                #    )
                self.addresses_tableWidget.setCellWidget(rowcount-1, 0, btn_start)
                if rowcount == 0:
                    break
                rowcount = rowcount - 1
                btn_start.clicked.connect(self.start_chain)

    @pyqtSlot()
    def set_pubkey(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        if index.isValid():
            print(self.addresses_tableWidget.item(index.row(), 3).text())
            self.worker_setpubkey = marmarachain_rpc.RpcHandler()
            command = cp.setpubkey + ' ' + self.addresses_tableWidget.item(index.row(), 3).text()
            print(command)
            setpubkey_thread = self.worker_thread(self.thread_setpubkey, self.worker_setpubkey, command)
            setpubkey_thread.command_out.connect(self.set_pubkey_result)

    @pyqtSlot(tuple)
    def set_pubkey_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            self.pubkey_status = True
            if str(json.loads(result_out[0])).rfind('error') > -1:
                pubkey = json.loads(result_out[0])['pubkey']
                print('this pubkey: ' + pubkey + ' already set')
                self.bottom_message_label.setText(result_out[0])
            self.bottom_message_label.setText('this pubkey set ' + str(json.loads(result_out[0])['pubkey']))
            self.update_addresses_table()
        elif result_out[1]:
            print(result_out[1])
            self.bottom_message_label.setText(result_out[1])

    @pyqtSlot()
    def start_chain(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        if index.isValid():
            pubkey = self.addresses_tableWidget.item(index.row(), 3).text()
            marmarachain_rpc.start_chain(pubkey)
            time.sleep(0.5)
            self.addresses_tableWidget.setColumnHidden(0, True)
            self.check_chain_pid()





    def add_address(self):
        self.chain_stackedWidget.setCurrentIndex(1)

    def back_chain_widget_index(self):
        self.chain_stackedWidget.setCurrentIndex(0)
        self.update_addresses_table()



    def see_privkey_page(self):
        self.chain_stackedWidget.setCurrentIndex(2)
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

    # ----------------------------------------------------------------------------


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ui = MarmaraMain()
    ui.show()
    app.exec_()
