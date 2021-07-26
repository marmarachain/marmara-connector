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
from qtguistyle import GuiStyle


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
        # MCL tabwidget
        self.mcl_tab.currentChanged.connect(self.mcl_tab_changed)
        # System page
        self.stopchain_Button.clicked.connect(self.stop_chain)
        self.stopchain_Button.setIcon(QIcon(self.icon_path + "/stop_icon.png"))
        self.stopchain_Button.setIconSize(QSize(32, 32))
        self.addaddress_page_Button.clicked.connect(self.add_address)
        self.addresspage_back_Button.clicked.connect(self.back_chain_widget_index)
        self.privkey_page_Button.clicked.connect(self.see_privkey_page)
        self.privatekeypage_back_Button.clicked.connect(self.back_chain_widget_index)
        self.addresses_tableWidget.cellClicked.connect(self.itemcontext)
        # Wallet page
        self.contacts_address_comboBox.currentTextChanged.connect(self.get_selected_contact_address)
        # Credit Loops page-----------------
        self.creditloop_tabWidget.currentChanged.connect(self.credit_tab_changed)
        # -----Create credit Loop Request
        self.contactpubkey_loop_comboBox.currentTextChanged.connect(self.get_selected_contact_loop_pubkey)
        self.contactpubkey_transfer_comboBox.currentTextChanged.connect(self.get_selected_contact_transfer_pubkey)
        # Contacs Page
        self.addcontact_Button.clicked.connect(self.add_contact)
        self.updatecontact_Button.clicked.connect(self.update_contact)
        self.deletecontact_Button.clicked.connect(self.delete_contact)
        self.contacts_tableWidget.cellClicked.connect(self.get_contact_info)
        self.clear_contact_Button.clicked.connect(self.clear_contacts_line_edit)
        self.contact_editing_row = ""

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
        self.mcl_tab.setCurrentIndex(0)
        self.chain_init()

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        marmarachain_rpc.set_connection_remote()

    @pyqtSlot(int)
    def mcl_tab_changed(self, index):
        if self.mcl_tab.tabText(index) == 'Contacts':
            print('update contacts table')
            self.update_contact_tablewidget()
        if self.mcl_tab.tabText(index) == 'Wallet':
            self.get_contact_names_addresses()
        if self.mcl_tab.tabText(index) == 'Credit Loops':
            self.creditloop_tabWidget.setCurrentIndex(0)

    @pyqtSlot(int)
    def credit_tab_changed(self, index):
        if self.creditloop_tabWidget.tabText(index) == 'Create Loop Request':
            self.get_contact_names_pubkeys()

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
            self.mcl_tab.setCurrentIndex(0)

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
                self.current_pubkey_value.setText(str(getinfo_result['pubkey']))
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
                self.addresses_tableWidget.setCellWidget(row_number, 0, btn_setpubkey)
                self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                   QtWidgets.QHeaderView.ResizeToContents)
                self.addresses_tableWidget.setItem(row_number, (row.index(item) + 1), QTableWidgetItem(str(item)))
                self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(row.index(item) + 1,
                                                                                   QtWidgets.QHeaderView.ResizeToContents)
                btn_setpubkey.clicked.connect(self.set_pubkey)
        self.update_addresses_table()

    @pyqtSlot(int, int)
    def itemcontext(self, row, column):
        item = self.addresses_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_message_label.setText("Copied  " + str(item))

    def update_addresses_table(self):
        if self.pubkey_status:
            self.addresses_tableWidget.setColumnHidden(0, True)
            current_pubkey = self.current_pubkey_value.text()
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                if current_pubkey == self.addresses_tableWidget.item(rowcount, 3).text():
                    self.currentaddress_value.setText(self.addresses_tableWidget.item(rowcount, 2).text())
                if rowcount == 0:
                    break
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
                rowcount = rowcount - 1
                self.addresses_tableWidget.setCellWidget(rowcount, 0, btn_start)
                if rowcount == 0:
                    break
                btn_start.clicked.connect(self.start_chain)

    @pyqtSlot()
    def set_pubkey(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        if index.isValid():
            self.worker_setpubkey = marmarachain_rpc.RpcHandler()
            command = cp.setpubkey + ' ' + self.addresses_tableWidget.item(index.row(), 3).text()
            setpubkey_thread = self.worker_thread(self.thread_setpubkey, self.worker_setpubkey, command)
            setpubkey_thread.command_out.connect(self.set_pubkey_result)

    @pyqtSlot(tuple)
    def set_pubkey_result(self, result_out):
        if result_out[0]:
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
    # Getting Contacts in to comboboxes
    # --------------------------------------------------------------------
    def get_contact_names_addresses(self):
        self.contacts_address_comboBox.clear()
        self.receiver_address_lineEdit.clear()
        self.contacts_address_comboBox.addItem('Contacts')
        contacts_data = configuration.ContacsSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contacts_address_comboBox.addItem(name[0])

    def get_selected_contact_address(self):
        contacts_data = configuration.ContacsSettings().read_csv_file()
        selected_contact_address = contacts_data[self.contacts_address_comboBox.currentIndex()]
        if selected_contact_address[1] != 'Address':
            self.receiver_address_lineEdit.setText(selected_contact_address[1])
        if selected_contact_address[1] == 'Address':
            self.receiver_address_lineEdit.clear()

    def get_contact_names_pubkeys(self):
        self.contactpubkey_loop_comboBox.clear()
        self.contactpubkey_transfer_comboBox.clear()
        self.create_receiverpubkey_lineEdit.clear()
        self.transfer_receiverpubkey_lineEdit.clear()
        self.contactpubkey_loop_comboBox.addItem('Contacts')
        self.contactpubkey_transfer_comboBox.addItem('Contacts')
        contacts_data = configuration.ContacsSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contactpubkey_loop_comboBox.addItem(name[0])
                self.contactpubkey_transfer_comboBox.addItem(name[0])

    def get_selected_contact_loop_pubkey(self):
        contacts_data = configuration.ContacsSettings().read_csv_file()
        selected_contactpubkey_loop = contacts_data[self.contactpubkey_loop_comboBox.currentIndex()]
        if selected_contactpubkey_loop[2] != 'Pubkey':
            self.create_receiverpubkey_lineEdit.setText(selected_contactpubkey_loop[2])
        if selected_contactpubkey_loop[2] == 'Pubkey':
            self.create_receiverpubkey_lineEdit.clear()


    def get_selected_contact_transfer_pubkey(self):
        contacts_data = configuration.ContacsSettings().read_csv_file()
        selected_contactpubkey_tranfer = contacts_data[self.contactpubkey_transfer_comboBox.currentIndex()]
        if selected_contactpubkey_tranfer[2] != 'Pubkey':
            self.transfer_receiverpubkey_lineEdit.setText(selected_contactpubkey_tranfer[2])
        if selected_contactpubkey_tranfer[2] == 'Pubkey':
            self.transfer_receiverpubkey_lineEdit.clear()

    # -------------------------------------------------------------------
    # Adding contacts editing and  deleting
    # --------------------------------------------------------------------
    def add_contact(self):
        contact_name = self.contactname_lineEdit.text()
        contact_address = self.contactaddress_lineEdit.text()
        contact_pubkey = self.contactpubkey_lineEdit.text()
        row = [contact_name, contact_address, contact_pubkey]
        unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey)
        if unique_record:
            self.bottom_message_label.setText(unique_record.get('error'))
        if not unique_record:
            configuration.ContacsSettings().add_csv_file(row)
            read_contacts_data = configuration.ContacsSettings().read_csv_file()
            self.update_contact_tablewidget(read_contacts_data)
            self.clear_contacts_line_edit()

    def unique_contacts(self, name, address, pubkey, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContacsSettings().read_csv_file()
        for row in contacts_data:
            if row[0] == name:
                print('same name')
                return {'error': 'same name exist'}
            if row[1] == address:
                print('same address')
                return {'error': 'same address exist'}
            if row[2] == pubkey:
                print('same pubkey')
                return {'error': 'same pubkey exist'}
            if not name or not address or not pubkey:
                print('empty record')
                return {'error': 'cannot be empty record'}
            # is_valid_address = row[1] # check if address is valid
            # if is_valid_address == False:
            #     return {'error': 'address is not valid'}
            # is_valid_pubkey = row[2] #  check if pubkey is valid
            # if is_valid_pubkey == False:
            #     return {'error': 'pubkey is not valid'}

    def clear_contacts_line_edit(self):
        self.contactname_lineEdit.clear()
        self.contactaddress_lineEdit.clear()
        self.contactpubkey_lineEdit.clear()

    def update_contact_tablewidget(self, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContacsSettings().read_csv_file()
        self.contacts_tableWidget.setRowCount(len(contacts_data) - 1)  # -1 for exclude header
        self.contacts_tableWidget.autoScrollMargin()
        for row in contacts_data:
            if not row[0] == 'Name':
                row_number = contacts_data.index(row) - 1  # -1 for exclude header
                for item in row:
                    self.contacts_tableWidget.setItem(row_number, row.index(item), QTableWidgetItem(str(item)))
                    self.contacts_tableWidget.horizontalHeader().setSectionResizeMode(row.index(item),
                                                                                      QtWidgets.QHeaderView.ResizeToContents)

    def get_contact_info(self, row, column):
        contact_name = self.contacts_tableWidget.item(row, 0).text()
        contact_address = self.contacts_tableWidget.item(row, 1).text()
        contact_pubkey = self.contacts_tableWidget.item(row, 2).text()
        self.contactname_lineEdit.setText(contact_name)
        self.contactaddress_lineEdit.setText(contact_address)
        self.contactpubkey_lineEdit.setText(contact_pubkey)
        self.contact_editing_row = row

    def update_contact(self):
        read_contacts_data = configuration.ContacsSettings().read_csv_file()
        contact_name = self.contactname_lineEdit.text()
        contact_address = self.contactaddress_lineEdit.text()
        contact_pubkey = self.contactpubkey_lineEdit.text()
        contact_data = configuration.ContacsSettings().read_csv_file()
        del contact_data[self.contact_editing_row + 1]  # removing editing record to don't check same record
        unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey, contact_data)
        if unique_record:
            self.bottom_message_label.setText(unique_record.get('error'))
        if not unique_record:
            read_contacts_data[self.contact_editing_row + 1][0] = contact_name  # +1 for exclude header
            read_contacts_data[self.contact_editing_row + 1][1] = contact_address  # +1 for exclude header
            read_contacts_data[self.contact_editing_row + 1][2] = contact_pubkey  # +1 for exclude header
            configuration.ContacsSettings().update_csv_file(read_contacts_data)
            self.update_contact_tablewidget()
            self.clear_contacts_line_edit()

    def delete_contact(self):
        read_contacts_data = configuration.ContacsSettings().read_csv_file()
        del read_contacts_data[self.contact_editing_row + 1]  # +1 for exclude header
        configuration.ContacsSettings().update_csv_file(read_contacts_data)
        self.update_contact_tablewidget()
        self.clear_contacts_line_edit()

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
