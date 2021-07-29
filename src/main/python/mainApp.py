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
from qtguistyle import GuiStyle
from Loading import LoadingScreen


class MarmaraMain(QMainWindow, GuiStyle):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        #   Default Settings
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.chain_status = False
        self.pubkey_status = False
        # paths settings
        # Menu Actions
        self.actionAbout.triggered.connect(self.show_about)
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
        self.stopchain_button.clicked.connect(self.stop_chain)
        # self.stopchain_button.setIcon(QIcon(self.icon_path + "/stop_icon.png"))
        # self.stopchain_button.setIconSize(QSize(32, 32))
        self.addaddress_page_button.clicked.connect(self.get_address_page)
        self.addresses_tableWidget.cellClicked.connect(self.itemcontext)
        self.privkey_page_button.clicked.connect(self.see_privkey_page)
        # add address page ----
        self.newaddress_button.clicked.connect(self.get_new_address)
        self.address_seed_button.clicked.connect(self.convertpassphrase)
        self.addresspage_back_button.clicked.connect(self.back_chain_widget_index)
        # private key page ----
        self.importprivkey_button.clicked.connect(self.importprivkey)
        self.privatekeypage_back_button.clicked.connect(self.back_chain_widget_index)

        # Wallet page
        self.contacts_address_comboBox.currentTextChanged.connect(self.get_selected_contact_address)
        # Credit Loops page-----------------
        self.creditloop_tabWidget.currentChanged.connect(self.credit_tab_changed)
        # -----Create credit Loop Request
        self.contactpubkey_loop_comboBox.currentTextChanged.connect(self.get_selected_contact_loop_pubkey)
        self.contactpubkey_transfer_comboBox.currentTextChanged.connect(self.get_selected_contact_transfer_pubkey)
        # ---- Loop Queries page --
        self.loopqueries_pubkey_search_button.clicked.connect(self.search_pubkeyloops)
        # Contacst Page
        self.addcontact_button.clicked.connect(self.add_contact)
        self.updatecontact_button.clicked.connect(self.update_contact)
        self.deletecontact_button.clicked.connect(self.delete_contact)
        self.contacts_tableWidget.cellClicked.connect(self.get_contact_info)
        self.clear_contact_button.clicked.connect(self.clear_contacts_line_edit)
        self.contact_editing_row = ""

        # Tread setup
        self.thread_bottom_info = QThread()
        self.thread_getinfo = QThread()
        self.thread_getchain = QThread()
        self.thread_chainpid = QThread()
        self.thread_stopchain = QThread()
        self.thread_getaddresses = QThread()
        self.thread_setpubkey = QThread()
        self.thread_getnewaddress = QThread()
        self.thread_convertpassphrase = QThread()
        self.thread_importprivkey = QThread()
        self.thread_address_privkey = QThread()
        self.thread_seeprivkey = QThread()
        self.thread_pubkeyloopsearch = QThread()
        # self.thread_validateddresses = QThread()
        # self.thread_getbalance = QThread()

        # Loading Gif
        # --------------------------------------------------
        self.loading = LoadingScreen()
        # --------------------------------------------------

    def show_about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About Marmara Connector",
            "This is a software written to carry out Marmarachain node operations on a local or remote machine."
        )

    def host_selection(self):
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)

    def local_selection(self):
        self.main_tab.setCurrentIndex(1)
        marmarachain_rpc.set_connection_local()
        self.mcl_tab.setCurrentIndex(0)
        self.chain_stackedWidget.setCurrentIndex(0)
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
        self.loading.startAnimation()
        if command:
            worker.set_command(command)
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        worker.finished.connect(self.stop_animation)
        if command:
            thread.started.connect(worker.do_execute_rpc)
        thread.start()
        return worker

    def stop_animation(self):
        self.loading.stopAnimation()

    def bottom_info(self, info):
        self.worker_bottom_info = marmarachain_rpc.RpcHandler()
        self.worker_bottom_info.set_bottom_info(self.bottom_message_label, info)
        self.worker_bottom_info.moveToThread(self.thread_bottom_info)
        self.worker_bottom_info.finished.connect(self.thread_bottom_info.quit)
        self.thread_bottom_info.started.connect(self.worker_bottom_info.write_bottom_info)
        self.thread_bottom_info.start()

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
            self.bottom_info('sending chain start command')
            marmarachain_rpc.start_chain()
        self.check_chain_pid()

    def check_chain_pid(self):
        # self.worker_chain_pid = marmarachain_rpc.RpcHandler()
        # check_pid_thread = self.worker_thread(self.thread_chainpid, self.worker_chain_pid)
        # self.thread_chainpid.started.connect(self.worker_chain_pid.chain_pid)
        # check_pid_thread.daemon_pid.connect(self.chain_check_finished)

        # def chain_check_finished(self, result_out):
        #     if not result_out:
        #         self.bottom_message_label.setText('Chain start error: No pid')
        #     if result_out:
        #         print('pid is ' + result_out)
        while True:
            marmara_pid = marmarachain_rpc.mcl_chain_status()
            if len(marmara_pid[0]) > 0:
                print('chain has pid')
                break
            time.sleep(1)
            i = i - 1
            if i == 0:
                self.bottom_info('Chain did not start')
                print('tried still no pid')
                break
            elif marmara_pid[1]:
                print('error ??')
                print(marmara_pid[1])
                break
        self.is_chain_ready()

    @pyqtSlot()
    def is_chain_ready(self):
        self.worker_getchain = marmarachain_rpc.RpcHandler()
        chain_ready_thread = self.worker_thread(self.thread_getchain, self.worker_getchain)
        self.thread_getchain.started.connect(self.worker_getchain.is_chain_ready)
        chain_ready_thread.command_out.connect(self.chain_ready_result)
        chain_ready_thread.finished.connect(self.chain_init)

    @pyqtSlot(tuple)
    def chain_ready_result(self, result_out):
        if result_out[0]:
            print('chain ready finished')
            self.bottom_info('chain ready finished')
            self.chain_status = True
        elif result_out[1]:
            print_result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = print_result.index('error message:') + 1
                self.bottom_info(print_result[index])

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

            self.bottom_message_label.setText('initialization finished')
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
            # self.addresses_tableWidget.autoScrollMargin()
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
                btn_start.clicked.connect(self.start_chain)
                if rowcount == 0:
                    break

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
        print(index.row())
        print(index.column())
        if index.isValid():
            pubkey = self.addresses_tableWidget.item(index.row(), 3).text()
            print(pubkey)
            marmarachain_rpc.start_chain(pubkey)
            time.sleep(0.5)
            self.addresses_tableWidget.setColumnHidden(0, True)
            self.check_chain_pid()

    def search_pubkeyloops(self):
        pubkey = self.loopqueries_pubkey_lineEdit.text()
        if pubkey:
            self.worker_pubkeyloopsearch = marmarachain_rpc.RpcHandler()
            command = cp.marmarainfo + ' 0 0 0 0 ' + pubkey
            pubkeyloopsearch_thread = self.worker_thread(self.thread_pubkeyloopsearch, self.worker_pubkeyloopsearch,
                                                         command)
            pubkeyloopsearch_thread.command_out.connect(self.get_search_pubkeyloops_result)
        else:
            self.bottom_message_label.setText('write pubkey to search !')

    def get_search_pubkeyloops_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
        elif result_out[1]:
            print(result_out[1])

    # ------------------
    # wallet Address Add, import
    # -------------------
    @pyqtSlot()
    def get_address_page(self):
        self.chain_stackedWidget.setCurrentIndex(1)

    @pyqtSlot()
    def get_new_address(self):
        self.worker_get_newaddress = marmarachain_rpc.RpcHandler()
        command = cp.getnewaddress
        getnewaddress_thread = self.worker_thread(self.thread_getnewaddress, self.worker_get_newaddress, command)
        getnewaddress_thread.command_out.connect(self.set_getnewaddress_result)

    @pyqtSlot(tuple)
    def set_getnewaddress_result(self, result_out):
        if result_out[0]:
            self.bottom_message_label.setText('new address = ' + str(result_out[0]))
        elif result_out[1]:
            result = str(result_out[1]).splitlines()
            print_result = ""
            for line in result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def convertpassphrase(self):
        verified = False
        seed = self.plainTextEdit.toPlainText()
        print(seed)
        verify = self.plainTextEdit_2.toPlainText()
        print(verify)
        if seed:
            if seed == verify:
                verified = True
            else:
                self.bottom_message_label.setText('seed words does not match')
        if verified:
            self.worker_convert_passphrase = marmarachain_rpc.RpcHandler()
            command = cp.convertpassphrase + ' "' + seed + '"'
            convert_passphrase_thread = self.worker_thread(self.thread_convertpassphrase,
                                                           self.worker_convert_passphrase, command)
            convert_passphrase_thread.command_out.connect(self.converpassphrase_result)
        else:
            self.bottom_message_label.setText('write some seed words !')

    @pyqtSlot(tuple)
    def converpassphrase_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            wif = result['wif']
            response = QtWidgets.QMessageBox.question(self, "Creating an Address",
                                                      "An address has been created with details below. Do you want to "
                                                      "import this address to the wallet?" +
                                                      "<br><b>Seed = </b><br>" + result['agamapassphrase'] +
                                                      "<br><b>Private Key = </b><br>" + wif +
                                                      "<br><b>Address = </b><br>" + result['address'] +
                                                      "<br><b>Pubkey = </b><br>" + result['pubkey'])
            if response == QtWidgets.QMessageBox.Yes:
                self.get_importprivkey(wif)

        # for error handling of convertpassphrase method
        elif result_out[1]:
            result = str(result_out[1]).splitlines()
            print_result = ""
            for line in result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def importprivkey(self):
        privkey = self.privkey_lineEdit.text()
        if privkey:
            self.get_importprivkey(privkey)
        else:
            self.bottom_message_label.setText('write private key first')

    def get_importprivkey(self, wif):
        self.worker_importprivkey = marmarachain_rpc.RpcHandler()
        command = cp.importprivkey + ' ' + wif
        importprivkey_thread = self.worker_thread(self.thread_importprivkey, self.worker_importprivkey, command)
        importprivkey_thread.command_out.connect(self.set_importprivkey_result)

    @pyqtSlot(tuple)
    def set_importprivkey_result(self, result_out):
        if result_out[0]:
            self.bottom_message_label.setText(str(result_out[0]))
            print(result_out[0])
        elif result_out[1]:
            result = str(result_out[1]).splitlines()
            print_result = ""
            for line in result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def back_chain_widget_index(self):
        self.chain_stackedWidget.setCurrentIndex(0)
        if self.chain_status:
            self.getaddresses()
        else:
            self.update_addresses_table()

    @pyqtSlot()
    def see_privkey_page(self):
        self.chain_stackedWidget.setCurrentIndex(2)
        self.get_privkey_table()

    def get_privkey_table(self):
        self.worker_getaddress_privkey = marmarachain_rpc.RpcHandler()
        command = cp.getaddressesbyaccount
        address_privkey_thread = self.worker_thread(self.thread_address_privkey, self.worker_getaddress_privkey,
                                                    command)
        address_privkey_thread.command_out.connect(self.set_privkey_table_result)

    @pyqtSlot(tuple)
    def set_privkey_table_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            print(len(result))
            self.addresses_privkey_tableWidget.setRowCount(len(result))
            # self.addresses_privkey_tableWidget.autoScrollMargin()
            for address in result:
                row_number = result.index(address)
                btn_seeprivkey = QPushButton('')
                btn_seeprivkey.setIcon(QIcon(self.icon_path + "/details.png"))
                self.addresses_privkey_tableWidget.setCellWidget(row_number, 1, btn_seeprivkey)
                self.addresses_privkey_tableWidget.setItem(row_number, 0, QTableWidgetItem(address))
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                           QtWidgets.QHeaderView.ResizeToContents)
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                           QtWidgets.QHeaderView.ResizeToContents)
                btn_seeprivkey.clicked.connect(self.set_seeprivkey)

        elif result_out[1]:
            result = str(result_out[1]).splitlines()
            print_result = ""
            for line in result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    @pyqtSlot()
    def set_seeprivkey(self):
        button = self.sender()
        print(button.pos())
        index = self.addresses_privkey_tableWidget.indexAt(button.pos())
        print(index.row())
        if index.isValid():
            address = self.addresses_privkey_tableWidget.item(index.row(), 0).text()
            self.worker_see_privkey = marmarachain_rpc.RpcHandler()
            command = cp.dumpprivkey + ' ' + address
            print(command)
            see_privkey_thread = self.worker_thread(self.thread_seeprivkey, self.worker_see_privkey, command)
            see_privkey_thread.command_out.connect(self.get_seeprivkey_result)

    @pyqtSlot(tuple)
    def get_seeprivkey_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            self.bottom_message_label.setText('private key = ' + result_out[0])
        elif result_out[1]:
            result = str(result_out[1]).splitlines()
            print_result = ""
            for line in result:
                print_result = print_result + ' ' + str(line)
            print(print_result)
            self.bottom_message_label.setText(print_result)

    # -------------------------------------------------------------------
    # Getting Contacts in to comboboxes
    # --------------------------------------------------------------------
    def get_contact_names_addresses(self):
        self.contacts_address_comboBox.clear()
        self.receiver_address_lineEdit.clear()
        self.contacts_address_comboBox.addItem('Contacts')
        contacts_data = configuration.ContacstSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contacts_address_comboBox.addItem(name[0])

    def get_selected_contact_address(self):
        contacts_data = configuration.ContacstSettings().read_csv_file()
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
        contacts_data = configuration.ContacstSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contactpubkey_loop_comboBox.addItem(name[0])
                self.contactpubkey_transfer_comboBox.addItem(name[0])

    def get_selected_contact_loop_pubkey(self):
        contacts_data = configuration.ContacstSettings().read_csv_file()
        selected_contactpubkey_loop = contacts_data[self.contactpubkey_loop_comboBox.currentIndex()]
        if selected_contactpubkey_loop[2] != 'Pubkey':
            self.create_receiverpubkey_lineEdit.setText(selected_contactpubkey_loop[2])
        if selected_contactpubkey_loop[2] == 'Pubkey':
            self.create_receiverpubkey_lineEdit.clear()

    def get_selected_contact_transfer_pubkey(self):
        contacts_data = configuration.ContacstSettings().read_csv_file()
        selected_contactpubkey_tranfer = contacts_data[self.contactpubkey_transfer_comboBox.currentIndex()]
        if selected_contactpubkey_tranfer[2] != 'Pubkey':
            self.transfer_receiverpubkey_lineEdit.setText(selected_contactpubkey_tranfer[2])
        if selected_contactpubkey_tranfer[2] == 'Pubkey':
            self.transfer_receiverpubkey_lineEdit.clear()

    # -------------------------------------------------------------------
    # Adding contacts editing and deleting
    # --------------------------------------------------------------------
    def add_contact(self):
        contact_name = self.contactname_lineEdit.text()
        contact_address = self.contactaddress_lineEdit.text()
        contact_pubkey = self.contactpubkey_lineEdit.text()
        new_record = [contact_name, contact_address, contact_pubkey]
        unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey)
        if unique_record:
            QtWidgets.QMessageBox.information(self, "Error Adding Contact", unique_record.get('error'))
        if not unique_record:
            configuration.ContacstSettings().add_csv_file(new_record)
            read_contacts_data = configuration.ContacstSettings().read_csv_file()
            self.update_contact_tablewidget(read_contacts_data)
            self.clear_contacts_line_edit()
            QtWidgets.QMessageBox.information(self, "Added Contact", "It is your responsibility that the information "
                                                                     "you have entered are correct and valid.")

    def unique_contacts(self, name, address, pubkey, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContacstSettings().read_csv_file()
        if name == address:
            return {'error': 'Name and Address cannot be the same!'}
        if name == pubkey:
            return {'error': 'Name and Pubkey cannot be the same!'}
        if pubkey == address:
            return {'error': 'Pubkey and Address cannot be the same!'}
        for row in contacts_data:
            if row[0] == name:
                print('same name')
                return {'error': 'Same name exists'}
            if row[1] == address:
                print('same address')
                return {'error': 'Same address exists'}
            if row[2] == pubkey:
                print('same pubkey')
                return {'error': 'Same pubkey exists'}
            if not name or not address or not pubkey:
                print('empty record')
                return {'error': 'cannot be an empty record'}
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
        self.contact_editing_row = None

    def update_contact_tablewidget(self, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContacstSettings().read_csv_file()
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
        contact_name = ""
        contact_address = ""
        contact_pubkey = ""
        if self.contacts_tableWidget.item(row, 0):
            contact_name = self.contacts_tableWidget.item(row, 0).text()
        if self.contacts_tableWidget.item(row, 1):
            contact_address = self.contacts_tableWidget.item(row, 1).text()
        if self.contacts_tableWidget.item(row, 2):
            contact_pubkey = self.contacts_tableWidget.item(row, 2).text()
        self.contactname_lineEdit.setText(contact_name)
        self.contactaddress_lineEdit.setText(contact_address)
        self.contactpubkey_lineEdit.setText(contact_pubkey)
        self.contact_editing_row = row

    def update_contact(self):
        if self.contact_editing_row is not None:
            read_contacts_data = configuration.ContacstSettings().read_csv_file()
            contact_name = self.contactname_lineEdit.text()
            contact_address = self.contactaddress_lineEdit.text()
            contact_pubkey = self.contactpubkey_lineEdit.text()
            contact_data = configuration.ContacstSettings().read_csv_file()
            del contact_data[self.contact_editing_row + 1]  # removing editing record to don't check same record
            unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey, contact_data)
            if unique_record:
                self.bottom_message_label.setText(unique_record.get('error'))
            if not unique_record:
                read_contacts_data[self.contact_editing_row + 1][0] = contact_name  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][1] = contact_address  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][2] = contact_pubkey  # +1 for exclude header
                configuration.ContacstSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
        else:
            QtWidgets.QMessageBox.information(self, "Error Updating Contact", "You didn't select a contact from table.")

    def delete_contact(self):
        print(self.contact_editing_row)
        if self.contact_editing_row is not None:
            response = QtWidgets.QMessageBox.question(self,
                                                      "Deleting Contact",
                                                      "Are you sure to delete the contact from the list?",
                                                      )
            if response == QtWidgets.QMessageBox.Yes:
                read_contacts_data = configuration.ContacstSettings().read_csv_file()
                del read_contacts_data[self.contact_editing_row + 1]  # +1 for exclude header
                configuration.ContacstSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
            else:
                self.clear_contacts_line_edit()
        else:
            QtWidgets.QMessageBox.information(self, "Error Deleting Contact", "You didn't select a contact from table.")

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
