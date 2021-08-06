import json
import time

import qrcode
from datetime import datetime
from qr_code_gen import Image
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread, pyqtSlot, QDateTime
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QMessageBox, QDesktopWidget
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
        self.center_ui()
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
        # side panel
        self.copyaddress_button.clicked.connect(self.copyaddress_clipboard)
        self.copypubkey_button.clicked.connect(self.copypubkey_clipboard)
        self.staking_button.setChecked(False)
        self.staking_button.clicked.connect(self.toggle_staking)
        self.mining_button.setChecked(False)
        self.cpu_core_selection_off()
        self.cpu_core_set_button.clicked.connect(self.setmining_cpu_core)
        self.mining_button.clicked.connect(self.toggle_mining)
        self.getinfo_refresh_button.clicked.connect(self.refresh_side_panel)
        # Chain page
        self.stopchain_button.clicked.connect(self.stop_chain)
        self.addaddress_page_button.clicked.connect(self.get_address_page)
        self.addresses_tableWidget.cellClicked.connect(self.itemcontext)
        self.privkey_page_button.clicked.connect(self.see_privkey_page)
        self.hide_address_checkBox.clicked.connect(self.hide_addresses)
        # - add address page ----
        self.newaddress_button.clicked.connect(self.get_new_address)
        self.address_seed_button.clicked.connect(self.convertpassphrase)
        self.addresspage_back_button.clicked.connect(self.back_chain_widget_index)
        # - private key page ----
        self.importprivkey_button.clicked.connect(self.importprivkey)
        self.privatekeypage_back_button.clicked.connect(self.back_chain_widget_index)
        # Wallet page
        self.contacts_address_comboBox.currentTextChanged.connect(self.get_selected_contact_address)
        self.qrcode_button.clicked.connect(self.create_currentaddress_qrcode)
        self.lock_button.clicked.connect(self.marmaralock_amount)
        self.unlock_button.clicked.connect(self.marmaraunlock_amount)
        # Coin send-receive page
        self.coinsend_button.clicked.connect(self.sendtoaddress)

        # Credit Loops page-----------------
        self.creditloop_tabWidget.currentChanged.connect(self.credit_tab_changed)
        # ---- Received Loop Requests page ----
        self.looprequest_search_button.clicked.connect(self.search_marmarareceivelist)
        self.request_date_checkBox.clicked.connect(self.set_request_date_state)
        self.request_dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        # -----Create credit Loop Request
        self.contactpubkey_makeloop_comboBox.currentTextChanged.connect(self.get_selected_contact_loop_pubkey)
        self.contactpubkey_transferrequest_comboBox.currentTextChanged.connect(self.get_selected_contact_transfer_pubkey)
        self.make_credit_loop_matures_dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        self.send_loop_request_button.clicked.connect(self.marmarareceive)
        self.send_transfer_request_button.clicked.connect(self.marmararecieve_transfer)
        # -----Total Credit Loops page -----
        self.activeloops_search_button.clicked.connect(self.search_active_loops)
        # ---- Loop Queries page --
        self.lq_pubkey_search_button.clicked.connect(self.search_pubkeyloops)
        self.lq_txid_search_button.clicked.connect(self.marmaracreditloop)

        # Contacts Page
        self.addcontact_button.clicked.connect(self.add_contact)
        self.updatecontact_button.clicked.connect(self.update_contact)
        self.deletecontact_button.clicked.connect(self.delete_contact)
        self.contacts_tableWidget.cellClicked.connect(self.get_contact_info)
        self.clear_contact_button.clicked.connect(self.clear_contacts_line_edit)
        self.contact_editing_row = ""

        # Thread setup
        self.thread_bottom_info = QThread()
        self.thread_getinfo = QThread()
        self.thread_getchain = QThread()
        self.thread_stopchain = QThread()
        self.thread_getaddresses = QThread()
        self.thread_setpubkey = QThread()
        self.thread_getnewaddress = QThread()
        self.thread_convertpassphrase = QThread()
        self.thread_importprivkey = QThread()
        self.thread_address_privkey = QThread()
        self.thread_seeprivkey = QThread()
        self.thread_pubkeyloopsearch = QThread()
        self.thread_marmaralock = QThread()
        self.thread_marmaraunlock = QThread()
        self.thread_sendrawtransaction = QThread()
        self.thread_marmarareceivelist = QThread()
        self.thread_sendtoaddress = QThread()
        self.thread_marmaracreditloop = QThread()
        self.thread_marmarareceive = QThread()
        self.thread_getgenerate = QThread()
        self.thread_setgenerate = QThread()
        self.thread_sidepanel = QThread()
        self.thread_marmarareceive_transfer = QThread()
        self.thread_search_active_loops = QThread()

        # Loading Gif
        # --------------------------------------------------
        self.loading = LoadingScreen()
        # --------------------------------------------------

    def center_ui(self):
        qr = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center_point)
        self.move(qr.topLeft())


    def show_about(self):
        QMessageBox.about(
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
        if self.creditloop_tabWidget.tabText(index) == 'Make Loop Request':
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
        self.start_animation()
        if command:
            worker.set_command(command)
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        worker.finished.connect(self.stop_animation)
        if command:
            thread.started.connect(worker.do_execute_rpc)

        thread.start()
        return worker

    @pyqtSlot()
    def start_animation(self):
        self.loading.startAnimation()

    @pyqtSlot()
    def stop_animation(self):
        self.loading.stopAnimation()

    def bottom_info(self, info):
        self.bottom_message_label.setText(info)

    def bottom_err_info(self, err_msg):
        err_result = ""
        for line in str(err_msg).splitlines():
            err_result = err_result + ' ' + str(line)
        print(err_result)
        self.bottom_message_label.setText(err_result)

    # ---------------------------------------
    #  Chain initialization
    # ---------------------------------------
    @pyqtSlot()
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
        i = 5
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


    def is_chain_ready(self):
        self.worker_getchain = marmarachain_rpc.RpcHandler()  # worker setting
        chain_ready_thread = self.worker_thread(self.thread_getchain, self.worker_getchain)  # putting in to thread
        self.thread_getchain.started.connect(
            self.worker_getchain.is_chain_ready)  # executing respective worker class function
        chain_ready_thread.command_out.connect(self.chain_ready_result)  # getting results and connecting to socket
        chain_ready_thread.finished.connect(self.chain_init)  # chain_status is True go back continue to init

    @pyqtSlot(tuple)
    def chain_ready_result(self, result_out):
        if result_out[0]:
            print('chain ready finished')
            self.bottom_info('chain ready finished')
            self.chain_status = True
            self.chainstatus_button.setStyleSheet(
                "QPushButton {image: url(" + self.icon_path + "/circle-active.png); border: 0; width: 30px; height: 30px;}")
        elif result_out[1]:
            print_result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = print_result.index('error message:') + 1
                self.bottom_info(print_result[index])

    # --------------------------------------
    # Stopping Chain
    # --------------------------------------
    @pyqtSlot()
    def stop_chain(self):
        if self.chain_status:
            self.worker_stopchain = marmarachain_rpc.RpcHandler()  # worker setting
            stop_chain_thread = self.worker_thread(self.thread_stopchain, self.worker_stopchain)  # putting in to thread
            self.thread_stopchain.started.connect(
                self.worker_stopchain.stopping_chain)  # executing respective worker class function
            stop_chain_thread.command_out.connect(self.result_stopchain)  # getting results and connecting to socket
        else:
            self.bottom_info('chain is not ready')

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
            self.chainstatus_button.setStyleSheet(
                "QPushButton {image: url(" + self.icon_path + "/circle-inactive.png); border: 0; width: 30px; height: 30px;}")
            self.update_addresses_table()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # -------------------------------------------------------
    # Getting getinfo command
    # -------------------------------------------------------
    @pyqtSlot()
    def get_getinfo(self):
        self.worker_getinfo = marmarachain_rpc.RpcHandler()  # worker setting
        command = cp.getinfo  # setting command
        getinfo_thread = self.worker_thread(self.thread_getinfo, self.worker_getinfo, command)  # putting in to thread
        getinfo_thread.command_out.connect(self.getinfo_result)  # getting results and connecting to socket

    @pyqtSlot(tuple)
    def getinfo_result(self, result_out):
        if result_out[0]:
            getinfo_result = result_out[0]
            getinfo_result = json.loads(getinfo_result)
            self.bottom_message_label.setText('loading getinfo values')
            self.set_getinfo_result(getinfo_result)
            print('getinfo finished')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def set_getinfo_result(self, getinfo_result):
        if getinfo_result.get('synced'):
            self.chainsync_button.setStyleSheet(
                "QPushButton {image: url(" + self.icon_path + "/circle-active.png); border: 0; width: 30px; height: 30px;}")
        elif not getinfo_result.get('synced'):
            self.chainsync_button.setStyleSheet(
                "QPushButton {image: url(" + self.icon_path + "/circle-inactive.png); border: 0; width: 30px; height: 30px;}")
        if getinfo_result.get('pubkey'):
            self.pubkey_status = True
            self.current_pubkey_value.setText(str(getinfo_result['pubkey']))
        if getinfo_result.get('pubkey') is None:
            self.bottom_info('pubkey is not set')
            self.pubkey_status = False
            self.current_pubkey_value.setText("")
        self.difficulty_value_label.setText(str(int(getinfo_result['difficulty'])))
        self.currentblock_value_label.setText(str(getinfo_result['blocks']))
        self.longestchain_value_label.setText(str(getinfo_result['longestchain']))
        self.connections_value_label.setText(str(getinfo_result['connections']))
        self.totalnormal_value_label.setText(str(getinfo_result['balance']))
        self.bottom_info('getinfo finished')

    # -----------------------------------------------------------
    # Side panel functions
    # -----------------------------------------------------------
    @pyqtSlot()
    def refresh_side_panel(self):
        self.worker_sidepanel = marmarachain_rpc.RpcHandler()
        sidepanel_thread = self.worker_thread(self.thread_sidepanel, self.worker_sidepanel)
        self.thread_sidepanel.started.connect(self.worker_sidepanel.refresh_sidepanel)
        sidepanel_thread.command_out.connect(self.refresh_side_panel_result)
        last_update = self.tr('Last Update: ')
        date = (str(datetime.now().date()))
        hour = (str(datetime.now().hour))
        minute = (str(datetime.now().minute))
        self.last_update_label.setText(last_update + date + ' ' + hour + ':' + minute)


    @pyqtSlot(tuple)
    def refresh_side_panel_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            if result.get('version'):
                self.set_getinfo_result(result)
            else:
                self.setgenerate_result(result_out)
                self.bottom_info('Refresh done.')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def copyaddress_clipboard(self):
        address = self.currentaddress_value.text()
        if address != "":
            QtWidgets.QApplication.clipboard().setText(address)
            self.bottom_info('copied ' + address)
        else:
            self.bottom_info('no address value set')

    @pyqtSlot()
    def copypubkey_clipboard(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey != "":
            QtWidgets.QApplication.clipboard().setText(pubkey)
            self.bottom_info('copied ' + pubkey)
        else:
            self.bottom_info('no pubkey value set')

    @pyqtSlot()
    def toggle_staking(self):
        if self.staking_button.isChecked():  # Staking button status is True.
            if self.mining_button.isChecked():  # Checking mining is  also active
                response = QMessageBox.question(self, 'Turnoff Mining', 'Mining is active it will be closed')
                if response == QMessageBox.Yes:
                    self.mining_button.setChecked(False)  # Close mining and set staking mode
                    self.cpu_core_selection_off()
                    print('setgenerate True 0')
                    self.setgenerate('true 0')
                if response == QMessageBox.No:  # Abort selecting staking and continue mining
                    self.staking_button.setChecked(False)
            else:  # set staking mode
                print('setgenerate True 0')
                self.setgenerate('true 0')
        else:  # Staking button status is False
            response = QMessageBox.question(self, 'Turnoff Staking', ' You are about to close staking. Are you sure?')
            if response == QMessageBox.Yes:
                print('setgenerate False')
                self.setgenerate('false')
            if response == QMessageBox.No:
                self.staking_button.setChecked(True)  # Abort selecting staking button

    @pyqtSlot()
    def toggle_mining(self):
        if self.mining_button.isChecked():  # Mining button status is True.
            if self.staking_button.isChecked():  # Checking staking is also active
                response = QMessageBox.question(self, 'Turnoff Staking', 'Staking is active it will be closed')
                if response == QMessageBox.Yes:
                    self.staking_button.setChecked(False)  # Close staking and turn on mining
                    print('setgenerate True 1')
                    self.setgenerate('true 1')
                    self.cpu_core_selection_on()
                if response == QMessageBox.No:  # Abort selecting mining and continue staking
                    self.mining_button.setChecked(False)
            else:  # Staking is off turn on Mining mode
                print('setgenerate True 1')
                self.cpu_core_selection_on()
                self.setgenerate('true 1')
        else:  # Mining button status is False.
            response = QMessageBox.question(self, 'Turnoff Mining', ' You are about to close mining. Are you sure?')
            if response == QMessageBox.Yes:
                print('setgenerate False')
                self.cpu_core_selection_off()
                self.setgenerate('false')
            if response == QMessageBox.No:
                self.mining_button.setChecked(True)  # Abort selecting mining button

    def cpu_core_selection_on(self):
        self.cpu_label.setVisible(True)
        self.cpu_core_lineEdit.setVisible(True)
        self.cpu_core_set_button.setVisible(True)

    def cpu_core_selection_off(self):
        self.cpu_label.setVisible(False)
        self.cpu_core_lineEdit.setVisible(False)
        self.cpu_core_set_button.setVisible(False)

    def setgenerate(self, arg):
        self.worker_setgenerate = marmarachain_rpc.RpcHandler()
        self.worker_setgenerate.set_command(cp.setgenerate + ' ' + arg)
        setgenerate_thread = self.worker_thread(self.thread_setgenerate, self.worker_setgenerate)
        self.thread_setgenerate.started.connect(self.worker_setgenerate.setgenerate)
        setgenerate_thread.command_out.connect(self.setgenerate_result)

    @pyqtSlot(tuple)
    def setgenerate_result(self, result_out):
        if result_out[0]:
            print(json.loads(result_out[0]))
            result = json.loads(result_out[0])
            if result.get('staking') is True and result.get('generate') is False:
                self.bottom_info('Staking ON')
                self.staking_button.setChecked(True)
                self.mining_button.setChecked(False)
            if result.get('staking') is False and result.get('generate') is False:
                self.bottom_info('Mining status is OFF')
                self.staking_button.setChecked(False)
                self.mining_button.setChecked(False)
            if result.get('generate') is True and result.get('staking') is False:
                self.bottom_info('Mining ON with ' + str(result.get('numthreads')))
                self.staking_button.setChecked(False)
                self.mining_button.setChecked(True)
        if result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def setmining_cpu_core(self):
        cpu_no = self.cpu_core_lineEdit.text()
        # print(int(cpu_no))
        try:
            int(cpu_no)
            if int(cpu_no) == 0:
                cpu_no = 1
                self.cpu_core_lineEdit.setText('1')
                self.bottom_info('for mining cpu core cannot be 0')
            self.setgenerate('true ' + str(cpu_no))
        except Exception:
            self.bottom_info('CPU core should be integer!')


    # -----------------------------------------------------------
    # Chain page functions
    # -----------------------------------------------------------

    # getting addresses for address table widget
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

    @pyqtSlot()
    def hide_addresses(self):
        if self.hide_address_checkBox.checkState():
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                if self.addresses_tableWidget.item(rowcount, 1).text() == "0":
                    self.addresses_tableWidget.setRowHidden(rowcount, True)
                if rowcount == 0:
                    break
        else:
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                if self.addresses_tableWidget.item(rowcount, 1).text() == "0":
                    self.addresses_tableWidget.setRowHidden(rowcount, False)
                if rowcount == 0:
                    break

    @pyqtSlot(int, int)
    def itemcontext(self, row, column):
        item = self.addresses_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_message_label.setText("Copied  " + str(item))

    def update_addresses_table(self):
        if self.pubkey_status:
            self.addresses_tableWidget.setColumnHidden(0, True)
            if self.current_pubkey_value.text() == "":
                self.get_getinfo()
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
            self.get_getinfo()
            if str(json.loads(result_out[0])).rfind('error') > -1:
                pubkey = json.loads(result_out[0])['pubkey']
                print('this pubkey: ' + pubkey + ' already set')
                self.bottom_message_label.setText(result_out[0])
            QtWidgets.QMessageBox.information(self, 'Pubkey set', str(json.loads(result_out[0])['pubkey']))
            if QtWidgets.QMessageBox.Ok:
                self.update_addresses_table()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

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

    # ------------------
    # Chain  --- wallet Address Add, import
    # -------------------
    @pyqtSlot()
    def get_address_page(self):
        self.chain_stackedWidget.setCurrentIndex(1)
        self.passphrase_TextEdit.clear()
        self.verify_passphrase_TextEdit.clear()

    @pyqtSlot()
    def get_new_address(self):
        response = QMessageBox.question(self, "Creating New Address",
                                        "You are about to create a new address. Are you sure?")
        if response == QMessageBox.Yes:
            self.worker_get_newaddress = marmarachain_rpc.RpcHandler()
            command = cp.getnewaddress
            getnewaddress_thread = self.worker_thread(self.thread_getnewaddress, self.worker_get_newaddress, command)
            getnewaddress_thread.command_out.connect(self.set_getnewaddress_result)

    @pyqtSlot(tuple)
    def set_getnewaddress_result(self, result_out):
        if result_out[0]:
            self.bottom_message_label.setText('new address = ' + str(result_out[0]))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def convertpassphrase(self):
        verified = False
        seed = self.passphrase_TextEdit.toPlainText()
        print(seed)
        verify = self.verify_passphrase_TextEdit.toPlainText()
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
            response = QMessageBox.question(self, "Creating an Address",
                                            "An address has been created with details below. Do you want to "
                                            "import this address to the wallet?" +
                                            "<br><b>Seed = </b><br>" + result['agamapassphrase'] +
                                            "<br><b>Private Key = </b><br>" + wif +
                                            "<br><b>Address = </b><br>" + result['address'] +
                                            "<br><b>Pubkey = </b><br>" + result['pubkey'])
            if response == QMessageBox.Yes:
                self.get_importprivkey(wif)

        # for error handling of convertpassphrase method
        elif result_out[1]:
            self.bottom_err_info(result_out[1])


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
            self.bottom_err_info(result_out[1])

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
            self.bottom_err_info(result_out[1])

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
            see_privkey_thread = self.worker_thread(self.thread_seeprivkey, self.worker_see_privkey, command)
            see_privkey_thread.command_out.connect(self.get_seeprivkey_result)

    @pyqtSlot(tuple)
    def get_seeprivkey_result(self, result_out):
        if result_out[0]:
            # self.bottom_message_label.setText('private key = ' + result_out[0])
            QMessageBox.information(self, 'Private key', result_out[0])
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # --------------------------------------------------------------------
    # Wallet page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def create_currentaddress_qrcode(self):
        # creating a pix map of qr code
        # qr_image = qrcode.make(self.currentaddress_value.text(), image_factory=Image).pixmap()
        # set image to the Icon
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=7, border=1)
        qr.add_data(self.currentaddress_value.text())
        qr_image = qr.make_image(image_factory=Image).pixmap()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(qr_image)
        msg.setWindowTitle('Qr Code')
        msg.exec_()

    @pyqtSlot()
    def marmaralock_amount(self):
        if not self.lock_amount_value.text() == "":
            self.worker_marmaralock = marmarachain_rpc.RpcHandler()
            command = cp.marmaralock + ' ' + self.lock_amount_value.text()
            marmarlock_thread = self.worker_thread(self.thread_marmaralock, self.worker_marmaralock, command)
            marmarlock_thread.command_out.connect(self.marmaralock_amount_result)

    @pyqtSlot(tuple)
    def marmaralock_amount_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            print(result)
            if result['result'] == 'success':
                response = QMessageBox.question(self,
                                                'Confirm Transaction' f'You are about to activate {self.lock_amount_value.text()}')
                if response == QMessageBox.Yes:
                    self.sendrawtransaction(result['hex'])
                if response == QMessageBox.No:
                    self.bottom_info('Transaction aborted')
            if result.get('error'):

                self.bottom_info(str(result['error']))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
            result = str(result_out[1]).splitlines()
            print(result)
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])

    @pyqtSlot()
    def marmaraunlock_amount(self):
        if not self.unlock_amount_value.text() == "":
            self.worker_marmaraunlock = marmarachain_rpc.RpcHandler()
            command = cp.marmaraunlock + ' ' + self.unlock_amount_value.text()
            marmarunlock_thread = self.worker_thread(self.thread_marmaraunlock, self.worker_marmaraunlock, command)
            marmarunlock_thread.command_out.connect(self.marmaraunlock_amount_result)

    @pyqtSlot(tuple)
    def marmaraunlock_amount_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            print(result)
            if result.get('result') == "success":
                response = QMessageBox.question(self,
                                                'Confirm Transaction' f'You are about to activate {self.unlock_amount_value.text()}')
                if response == QMessageBox.Yes:
                    self.sendrawtransaction(result['hex'])
                if response == QMessageBox.No:
                    self.bottom_info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
            result = str(result_out[1]).splitlines()
            print(result)
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])

    # --------------------------------------------------------------------
    # sending raw transaction
    # --------------------------------------------------------------------

    def sendrawtransaction(self, hex):
        self.worker_sendrawtransaction = marmarachain_rpc.RpcHandler()
        command = cp.sendrawtransaction + ' ' + hex
        sendrawtransaction_thread = self.worker_thread(self.thread_sendrawtransaction, self.worker_sendrawtransaction,
                                                       command)
        sendrawtransaction_thread.command_out.connect(self.sendrawtransaction_result)

    @pyqtSlot(tuple)
    def sendrawtransaction_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # --------------------------------------------------------------------
    # Coin Send-Receive  page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def sendtoaddress(self):
        if self.receiver_address_lineEdit.text() == "":
            self.bottom_info('write a receiver address')
        else:
            if self.sending_amount_lineEdit.text() == "":
                self.bottom_info('write some amount')
            else:
                response = QMessageBox.question(self, 'Confirm Transaction',
                                                f'You are about to send {self.sending_amount_lineEdit.text()} MCL to {self.receiver_address_lineEdit.text()}')
                if response == QMessageBox.Yes:
                    self.worker_sendtoaddress = marmarachain_rpc.RpcHandler()
                    command = cp.sendtoaddress + ' ' + self.receiver_address_lineEdit.text() + ' ' + self.sending_amount_lineEdit.text()
                    print(command)
                    sendtoaddress_thread = self.worker_thread(self.thread_sendtoaddress, self.worker_sendtoaddress,
                                                              command)
                    sendtoaddress_thread.command_out.connect(self.sendtoaddress_result)
                if response == QMessageBox.No:
                    self.bottom_info('Transaction aborted')

    @pyqtSlot(tuple)
    def sendtoaddress_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
            result = str(result_out[1]).splitlines()
            print(result)
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])

    # -------------------------------------------------------------------
    # Credit loops functions
    # --------------------------------------------------------------------

    # function name: change_datetime_to_block_age
    # purpose: changes datetime to block age with given args date and begin_height=False set as default
    # usage: Calling function without providing begin_height, calculates the block_age between current datetime and date
    # arg. Calling function with begin_Height=True calculates the block_age from start of Marmarachain to the date arg
    # return: absolute value of block_age
    def change_datetime_to_block_age(self, date, begin_height=False):
        minute_ = date.toPyDateTime().minute
        hour_ = date.toPyDateTime().hour
        day_ = date.toPyDateTime().day
        month_ = date.toPyDateTime().month
        year_ = date.toPyDateTime().year
        if begin_height:
            now = datetime.fromtimestamp(1579278200)
        else:
            now = datetime.now()
        minute_ = now.minute - minute_
        hour_ = now.hour - hour_
        day_ = now.day - day_
        month_ = now.month - month_
        year_ = now.year - year_

        block_age = minute_ + (hour_ * 60) + (day_ * 1440) + (month_ * 30 * 1440) + (year_ * 365 * 1440)
        return abs(block_age)

    @pyqtSlot()
    def set_request_date_state(self):
        if self.request_date_checkBox.checkState():
            self.request_dateTimeEdit.setEnabled(False)
        else:
            self.request_dateTimeEdit.setEnabled(True)
            self.request_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
            self.request_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())

    @pyqtSlot()
    def search_marmarareceivelist(self):
        if self.request_date_checkBox.checkState():
            maxage = '1440'
        else:
            date = self.request_dateTimeEdit.dateTime()
            maxage = self.change_datetime_to_block_age(date)
            print('maxage ' + str(maxage))
        self.worker_marmarareceivelist = marmarachain_rpc.RpcHandler()
        command = cp.marmarareceivelist + ' ' + self.current_pubkey_value.text() + ' ' + str(maxage)
        marmarareceivelist_thread = self.worker_thread(self.thread_marmarareceivelist, self.worker_marmarareceivelist,
                                                       command)
        marmarareceivelist_thread.command_out.connect(self.search_marmarareceivelist_result)

    @pyqtSlot(tuple)
    def search_marmarareceivelist_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot(list)
    def set_transfer_request_result(self, transfer_result):
        for row in transfer_result:
            row_number = transfer_result.index(row)
            self.transferrequests_tableWidget.setRowCount(len(transfer_result))

    @pyqtSlot(list)
    def set_credit_request_result(self, credit_request_result):
        for row in credit_request_result:
            row_number = credit_request_result.index(row)
            self.loop_request_tableWidget.setRowCount(len(credit_request_result))

    # --- Create Loop Request page functions ----

    @pyqtSlot()
    def marmarareceive(self):
        amount = self.make_credit_loop_amount_lineEdit.text()
        senderpk = self.make_credit_loop_senderpubkey_lineEdit.text()
        matures_date = self.make_credit_loop_matures_dateTimeEdit.dateTime()
        matures = self.change_datetime_to_block_age(matures_date)
        if amount and senderpk and matures:
            self.worker_marmarareceive = marmarachain_rpc.RpcHandler()
            command = cp.marmarareceive + ' ' + senderpk + ' ' + amount + ' ' + \
                      self.make_credit_loop_currency_value_label.text() + ' ' + \
                      str(matures) + " '" + '{"avalcount":"0"}' + "'"
            print(command)
            marmarareceive_thread = self.worker_thread(self.thread_marmarareceive, self.worker_marmarareceive, command)
            marmarareceive_thread.command_out.connect(self.marmarareceive_result)
        else:
            self.bottom_info('cannot make a credit loop request with empty fields')

    @pyqtSlot(tuple)
    def marmarareceive_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            result = json.loads(result_out[0])
            # if result.get('result') == "success":
            #     print(result)
            #     response = QMessageBox.question(self, 'Confirm Transaction', 'You are about to make a credit loop request')
            #     if response == QMessageBox.Yes:
            #         self.sendrawtransaction(result.get('hex'))
            #     if response == QMessageBox.No:
            #         self.bottom_info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # function name: marmararecieve_transfer
    # purpose:  holder makes a marmarareceive request to the endorser to get the credit for selling the goods/services
    @pyqtSlot()
    def marmararecieve_transfer(self):
        senderpk = self.transfer_senderpubkey_lineEdit.text()
        baton = self.transfer_baton_lineEdit.text()
        if senderpk and baton:
            self.worker_marmarareceive_transfer = marmarachain_rpc.RpcHandler()
            command = cp.marmarareceive + ' ' + senderpk + ' ' + baton + " '" + '{"avalcount":"0"}' + "'"
            print(command)
            marmarareceive_transfer_thread = self.worker_thread(self.thread_marmarareceive_transfer,
                                                                self.worker_marmarareceive_transfer, command)
            marmarareceive_transfer_thread.command_out.connect(self.marmararecieve_transfer_result)
        else:
            self.bottom_info('cannot make a receive transfer request with empty fields')

    @pyqtSlot(tuple)
    def marmararecieve_transfer_result(self, result_out):
        if result_out[0]:
            # print(result_out[0])
            result = json.loads(result_out[0])
            # if result.get('result') == "success":
            #     print(result)
            #     response = QMessageBox.question(self, 'Confirm Transaction', 'You are about to make a request to the endorser')
            #     if response == QMessageBox.Yes:
            #         self.sendrawtransaction(result.get('hex'))
            #     if response == QMessageBox.No:
            #         self.bottom_info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
            result = str(result_out[1]).splitlines()
            print(result)
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])

    # -------------------------------------------------------------------
    # Total Credit Loops page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def search_active_loops(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey:
            self.bottom_message_label.setText('getting marmarainfo, please wait')
            self.worker_search_active_loops = marmarachain_rpc.RpcHandler()
            command = cp.marmarainfo + ' 0 0 0 0 ' + pubkey
            search_active_loops_thread = self.worker_thread(self.thread_search_active_loops,
                                                            self.worker_search_active_loops, command)
            search_active_loops_thread.command_out.connect(self.get_search_active_loops_result)
        else:
            self.bottom_info('pubkey not set!')
            self.clear_search_active_loops_result()

    @pyqtSlot(tuple)
    def get_search_active_loops_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                self.activeloops_total_amount_value_label.setText(str(result.get('totalamount')))
                self.closedloops_total_amount_value_label.setText(str(result.get('totalclosed')))
                self.activeloops_total_number_value_label.setText(str(result.get('numpending')))
                self.closedloops_total_number_value_label.setText(str(result.get('numclosed')))
                self.bottom_info('finished searching marmara blockchain for all blocks for the set pubkey')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                self.clear_search_active_loops_result()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def clear_search_active_loops_result(self):
        self.activeloops_total_amount_value_label.clear()
        self.closedloops_total_amount_value_label.clear()
        self.activeloops_total_number_value_label.clear()
        self.closedloops_total_number_value_label.clear()

    # -------------------------------------------------------------------
    # Credit Loop Queries functions
    # --------------------------------------------------------------------

    @pyqtSlot()
    def search_pubkeyloops(self):
        pubkey = self.loopqueries_pubkey_lineEdit.text()
        if pubkey:
            self.bottom_message_label.setText('getting marmarainfo, please wait')
            self.worker_pubkeyloopsearch = marmarachain_rpc.RpcHandler()
            command = cp.marmarainfo + ' 0 0 0 0 ' + pubkey
            pubkeyloopsearch_thread = self.worker_thread(self.thread_pubkeyloopsearch, self.worker_pubkeyloopsearch,
                                                         command)
            pubkeyloopsearch_thread.command_out.connect(self.get_search_pubkeyloops_result)
        else:
            self.bottom_info('write pubkey to search !')
            self.clear_lq_txid_search_result()

    def get_search_pubkeyloops_result(self, result_out):
        if result_out[0]:
            print(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                self.lq_pubkeynormalamount_value_label.setText(str(result.get('myPubkeyNormalAmount')))
                self.lq_pubkeyactivatedamount_value_label.setText(str(result.get('myActivatedAmount')))
                # print(result.get('TotalLockedInLoop'))
                self.lq_activeloopno_value_label.setText(str(result.get('numpending')))
                self.lq_pubkeyloopamount_value_label.setText(str(result.get('totalamount')))
                self.lq_closedloopno_value_label.setText(str(result.get('numclosed')))
                self.lq_pubkeyclosedloopamount_value_label.setText(str(result.get('totalclosed')))
                self.bottom_info('finished searching marmarainfo')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                self.clear_lq_pubkey_result()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def clear_lq_pubkey_result(self):
        self.lq_pubkeynormalamount_value_label.clear()
        self.lq_pubkeyactivatedamount_value_label.clear()
        self.lq_activeloopno_value_label.clear()
        self.lq_pubkeyloopamount_value_label.clear()
        self.lq_closedloopno_value_label.clear()
        self.lq_pubkeyclosedloopamount_value_label.clear()

    @pyqtSlot()
    def marmaracreditloop(self):
        txid = self.loopsearch_txid_lineEdit.text()
        if txid:
            self.bottom_info('getting credit loop info, please wait')
            self.worker_marmaracreditloop = marmarachain_rpc.RpcHandler()
            command = cp.marmaracreditloop + ' ' + txid
            marmaracreditloop_thread = self.worker_thread(self.thread_marmaracreditloop, self.worker_marmaracreditloop,
                                                          command)
            marmaracreditloop_thread.command_out.connect(self.marmaracreditloop_result)
        else:
            self.bottom_info('write loop transaction id  to search !')
            self.clear_lq_txid_search_result()

    @pyqtSlot(tuple)
    def marmaracreditloop_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            print(result)
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                self.clear_lq_txid_search_result()
            if result.get('result') == "success":
                self.loopquery_baton_value.setText(str(result.get('batontxid')))
                self.loopquery_amount_value.setText(str(result.get('amount')))
                self.loopquery_currency_value.setText(result.get('currency'))
                self.loopquery_matures_value.setText(str(result.get('matures')))
                self.loopquery_issuer_value.setText(str(result.get('batonpk')))
                self.bottom_info('credit loop info finished')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def clear_lq_txid_search_result(self):
        self.loopquery_baton_value.clear()
        self.loopquery_amount_value.clear()
        self.loopquery_currency_value.clear()
        self.loopquery_matures_value.clear()
        self.loopquery_issuer_value.clear()

    # -------------------------------------------------------------------
    # Getting Contacts in to comboboxes
    # --------------------------------------------------------------------
    def get_contact_names_addresses(self):
        self.contacts_address_comboBox.clear()
        self.receiver_address_lineEdit.clear()
        self.contacts_address_comboBox.addItem('Contacts')
        contacts_data = configuration.ContactsSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contacts_address_comboBox.addItem(name[0])

    @pyqtSlot()
    def get_selected_contact_address(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contact_address = contacts_data[self.contacts_address_comboBox.currentIndex()]
        if selected_contact_address[1] != 'Address':
            self.receiver_address_lineEdit.setText(selected_contact_address[1])
        if selected_contact_address[1] == 'Address':
            self.receiver_address_lineEdit.clear()

    def get_contact_names_pubkeys(self):
        self.contactpubkey_makeloop_comboBox.clear()
        self.contactpubkey_transferrequest_comboBox.clear()
        self.make_credit_loop_senderpubkey_lineEdit.clear()
        self.transfer_senderpubkey_lineEdit.clear()
        self.contactpubkey_makeloop_comboBox.addItem('Contacts')
        self.contactpubkey_transferrequest_comboBox.addItem('Contacts')
        contacts_data = configuration.ContactsSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contactpubkey_makeloop_comboBox.addItem(name[0])
                self.contactpubkey_transferrequest_comboBox.addItem(name[0])

    @pyqtSlot()
    def get_selected_contact_loop_pubkey(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contactpubkey_loop = contacts_data[self.contactpubkey_makeloop_comboBox.currentIndex()]
        if selected_contactpubkey_loop[2] != 'Pubkey':
            self.make_credit_loop_senderpubkey_lineEdit.setText(selected_contactpubkey_loop[2])
        if selected_contactpubkey_loop[2] == 'Pubkey':
            self.make_credit_loop_senderpubkey_lineEdit.clear()

    @pyqtSlot()
    def get_selected_contact_transfer_pubkey(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contactpubkey_transfer = contacts_data[self.contactpubkey_transferrequest_comboBox.currentIndex()]
        if selected_contactpubkey_transfer[2] != 'Pubkey':
            self.transfer_senderpubkey_lineEdit.setText(selected_contactpubkey_transfer[2])
        if selected_contactpubkey_transfer[2] == 'Pubkey':
            self.transfer_senderpubkey_lineEdit.clear()

    # -------------------------------------------------------------------
    # Adding contacts editing and deleting
    # --------------------------------------------------------------------
    @pyqtSlot()
    def add_contact(self):
        contact_name = self.contactname_lineEdit.text()
        contact_address = self.contactaddress_lineEdit.text()
        contact_pubkey = self.contactpubkey_lineEdit.text()
        new_record = [contact_name, contact_address, contact_pubkey]
        unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey)
        if unique_record:
            QMessageBox.information(self, "Error Adding Contact", unique_record.get('error'))
        if not unique_record:
            configuration.ContactsSettings().add_csv_file(new_record)
            read_contacts_data = configuration.ContactsSettings().read_csv_file()
            self.update_contact_tablewidget(read_contacts_data)
            self.clear_contacts_line_edit()
            QMessageBox.information(self, "Added Contact", "It is your responsibility that the information "
                                                           "you have entered are correct and valid.")

    def unique_contacts(self, name, address, pubkey, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContactsSettings().read_csv_file()
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

    @pyqtSlot()
    def clear_contacts_line_edit(self):
        self.contactname_lineEdit.clear()
        self.contactaddress_lineEdit.clear()
        self.contactpubkey_lineEdit.clear()
        self.contact_editing_row = None

    def update_contact_tablewidget(self, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContactsSettings().read_csv_file()
        self.contacts_tableWidget.setRowCount(len(contacts_data) - 1)  # -1 for exclude header
        self.contacts_tableWidget.autoScrollMargin()
        for row in contacts_data:
            if not row[0] == 'Name':
                row_number = contacts_data.index(row) - 1  # -1 for exclude header
                for item in row:
                    self.contacts_tableWidget.setItem(row_number, row.index(item), QTableWidgetItem(str(item)))
                    self.contacts_tableWidget.horizontalHeader().setSectionResizeMode(row.index(item),
                                                                                      QtWidgets.QHeaderView.ResizeToContents)

    @pyqtSlot(int, int)
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

    @pyqtSlot()
    def update_contact(self):
        if self.contact_editing_row is not None:
            read_contacts_data = configuration.ContactsSettings().read_csv_file()
            contact_name = self.contactname_lineEdit.text()
            contact_address = self.contactaddress_lineEdit.text()
            contact_pubkey = self.contactpubkey_lineEdit.text()
            contact_data = configuration.ContactsSettings().read_csv_file()
            del contact_data[self.contact_editing_row + 1]  # removing editing record to don't check same record
            unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey, contact_data)
            if unique_record:
                self.bottom_message_label.setText(unique_record.get('error'))
            if not unique_record:
                read_contacts_data[self.contact_editing_row + 1][0] = contact_name  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][1] = contact_address  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][2] = contact_pubkey  # +1 for exclude header
                configuration.ContactsSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
        else:
            QMessageBox.information(self, "Error Updating Contact", "You didn't select a contact from table.")

    @pyqtSlot()
    def delete_contact(self):
        print(self.contact_editing_row)
        if self.contact_editing_row is not None:
            response = QMessageBox.question(self,
                                            "Deleting Contact",
                                            "Are you sure to delete the contact from the list?",
                                            )
            if response == QMessageBox.Yes:
                read_contacts_data = configuration.ContactsSettings().read_csv_file()
                del read_contacts_data[self.contact_editing_row + 1]  # +1 for exclude header
                configuration.ContactsSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
            else:
                self.clear_contacts_line_edit()
        else:
            QMessageBox.information(self, "Error Deleting Contact", "You didn't select a contact from table.")

    # -------------------------------------------------------------------
    # Remote Host adding , editing, deleting and  saving in conf file
    # --------------------------------------------------------------------
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
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        selected_server_info = selected_server_info.split(",")
        self.edit_servername_lineEdit.setText(selected_server_info[0])
        self.edit_serverusername_lineEdit.setText(selected_server_info[1])
        self.edit_serverip_lineEdit.setText(selected_server_info[2])

    @pyqtSlot()
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

    @pyqtSlot()
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

    @pyqtSlot()
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
