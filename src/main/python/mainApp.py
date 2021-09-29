import json
import os
import pathlib
import platform
import sys
import time
import webbrowser
import logging
import qrcode
from datetime import datetime, timedelta
from qr_code_gen import Image
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon, QRegExpValidator, QFont
from PyQt5.QtCore import QThread, pyqtSlot, QDateTime, QSize, Qt, QTranslator, QRegExp
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QMessageBox, QDesktopWidget, QHeaderView, \
    QDialog, QDialogButtonBox, QVBoxLayout, QComboBox, QWidget, QGridLayout, QToolTip
import configuration
import marmarachain_rpc
import version
import remote_connection
import chain_args as cp
from qtguistyle import GuiStyle
import qtguistyle
from Loading import LoadingScreen
import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext

logging.getLogger(__name__)


class MarmaraMain(QMainWindow, GuiStyle):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        #   Default Settings
        self.trans = QTranslator(self)
        # self.retranslateUi(self)
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.chain_status = False
        self.pubkey_status = False
        self.center_ui()
        self.read_lang_setting()
        # paths settings
        # Menu Actions
        self.actionAbout.triggered.connect(self.show_about)
        self.actionLogout.triggered.connect(self.host_selection)
        self.actionLanguage_Selection.triggered.connect(self.show_languages)
        self.actionConsole.triggered.connect(self.open_debug_console)
        self.actionSee_Log_File.triggered.connect(self.open_log_file)
        self.actionCheck_for_Update.triggered.connect(self.check_app_version)
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)
        #   Login page Server authentication
        self.home_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.connect_button.clicked.connect(self.server_connect)
        self.serverpw_lineEdit.returnPressed.connect(self.server_connect)
        self.serveredit_button.clicked.connect(self.server_edit_selected)
        # install page
        self.start_install_button.clicked.connect(self.start_autoinstall)
        self.sudo_password_lineEdit.returnPressed.connect(self.start_autoinstall)
        #  Add Server Settings page
        self.add_serversave_button.clicked.connect(self.save_server_settings)
        self.servercancel_button.clicked.connect(self.add_cancel_selected)
        # Edit Server Settings page
        self.edit_serversave_button.clicked.connect(self.edit_server_settings)
        self.serverdelete_button.clicked.connect(self.delete_server_setting)
        # MCL tabwidget
        self.mcl_tab.currentChanged.connect(self.mcl_tab_changed)
        # side panel
        QToolTip.setFont(QFont('SansSerif', 10))
        self.copyaddress_button.clicked.connect(self.copyaddress_clipboard)
        self.copyaddress_button.setToolTip(self.tr("Copy address"))
        self.copypubkey_button.clicked.connect(self.copypubkey_clipboard)
        self.copypubkey_button.setToolTip(self.tr("Copy pubkey"))
        self.staking_button.setChecked(False)
        self.staking_button.clicked.connect(self.toggle_staking)
        self.mining_button.setChecked(False)
        self.regex = QRegExp("[1-90_]{1,5}")
        self.validator = QRegExpValidator(self.regex)
        self.cpu_core_lineEdit.setValidator(self.validator)
        self.cpu_core_selection_off()
        self.cpu_core_set_button.clicked.connect(self.setmining_cpu_core)
        self.mining_button.clicked.connect(self.toggle_mining)
        self.getinfo_refresh_button.clicked.connect(self.refresh_side_panel)
        self.support_pushButton.setToolTip(self.tr("Gift Marmara Core Team cups of coffee"))
        self.cup_lineEdit.setValidator(self.validator)
        self.cup_lineEdit.textChanged.connect(self.calculate_amount)
        self.cup_lineEdit.returnPressed.connect(self.send_coins_to_team)
        self.support_pushButton.clicked.connect(self.send_coins_to_team)
        # Chain page
        self.stopchain_button.clicked.connect(self.stop_chain)
        self.addaddress_page_button.clicked.connect(self.get_address_page)
        self.addresses_tableWidget.cellClicked.connect(self.addresstable_itemcontext)
        self.privkey_page_button.clicked.connect(self.see_privkey_page)
        self.hide_address_checkBox.clicked.connect(self.hide_addresses)
        self.download_blocks_button.setToolTip(self.tr("Download Blocks bootstrap"))
        self.download_blocks_button.clicked.connect(self.download_blocks)
        self.refresh_walletaddresses_button.clicked.connect(self.getaddresses)
        # - add address page ----
        self.newaddress_button.clicked.connect(self.get_new_address)
        self.address_seed_button.clicked.connect(self.convertpassphrase)
        self.addresspage_back_button.clicked.connect(self.back_chain_widget_index)
        # - private key page ----
        self.importprivkey_button.clicked.connect(self.importprivkey)
        self.privatekeypage_back_button.clicked.connect(self.back_chain_widget_index)
        # Wallet page
        self.myCCActivatedAddress = None
        self.addressamount_refresh_button.clicked.connect(self.get_address_amounts)
        self.lock_button.clicked.connect(self.marmaralock_amount)
        self.unlock_button.clicked.connect(self.marmaraunlock_amount)
        # Coin send-receive page
        self.contacts_address_comboBox.currentTextChanged.connect(self.get_selected_contact_address)
        self.qrcode_button.clicked.connect(self.create_currentaddress_qrcode)
        self.coinsend_button.clicked.connect(self.sendtoaddress)
        self.transactions_startdate_dateTimeEdit.setMinimumDateTime(QDateTime(datetime.fromtimestamp(1579278200)))
        self.transactions_startdate_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.transactions_startdate_dateTimeEdit.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.transactions_endtdate_dateTimeEdit.setMinimumDateTime(QDateTime(datetime.fromtimestamp(1579278200)))
        self.transactions_endtdate_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.transaction_search_button.clicked.connect(self.getaddresstxids)
        self.transactions_tableWidget.cellClicked.connect(self.transaction_itemcontext)
        # Credit Loops page-----------------
        self.creditloop_tabWidget.currentChanged.connect(self.credit_tab_changed)
        # ---- Received Loop Requests page ----
        self.looprequest_search_button.clicked.connect(self.search_marmarareceivelist)
        self.request_date_checkBox.clicked.connect(self.set_request_date_state)
        self.request_dateTimeEdit.setDateTime(QDateTime.currentDateTime())

        # -----Make credit Loop Request
        self.contactpubkey_makeloop_comboBox.currentTextChanged.connect(self.get_selected_contact_loop_pubkey)
        self.contactpubkey_transferrequest_comboBox.currentTextChanged.connect(self.get_selected_contact_transfer_pubkey)
        self.make_credit_loop_matures_dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        self.send_loop_request_button.clicked.connect(self.marmarareceive)
        self.send_transfer_request_button.clicked.connect(self.marmararecieve_transfer)
        # -----Total Credit Loops page -----
        self.activeloops_search_button.clicked.connect(self.search_active_loops)
        self.transferable_maturesfrom_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.transferable_maturesfrom_dateTimeEdit.setMinimumDateTime(QDateTime(datetime.fromtimestamp(1579278200)))
        self.transferable_maturesfrom_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.transferable_maturesfrom_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.transferable_maturesto_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.transferable_maturesto_dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        self.transferable_matures_checkBox.clicked.connect(self.set_transferable_mature_date_state)
        self.transferable_amount_checkBox.clicked.connect(self.set_transferable_amount_state)
        self.transferableloops_search_button.clicked.connect(self.marmaraholderloops)
        # ---- Loop Queries page --
        self.lq_pubkey_search_button.clicked.connect(self.search_any_pubkey_loops)
        self.lq_txid_search_button.clicked.connect(self.search_loop_txid)

        # Contacts Page
        self.addcontact_button.clicked.connect(self.add_contact)
        self.updatecontact_button.clicked.connect(self.update_contact)
        self.deletecontact_button.clicked.connect(self.delete_contact)
        self.contacts_tableWidget.cellClicked.connect(self.get_contact_info)
        self.clear_contact_button.clicked.connect(self.clear_contacts_line_edit)
        self.contact_editing_row = ""
        # Stats Page
        self.stats_refresh_pushButton.clicked.connect(self.get_marmara_stats)
        self.stats_calculate_pushButton.setEnabled(False)
        self.stats_calculate_pushButton.clicked.connect(self.calculate_estimated_stake)

        # Thread setup
        self.thread_marmarad_path = QThread()
        self.thread_autoinstall = QThread()
        self.thread_getinfo = QThread()
        self.worker_getinfo = marmarachain_rpc.RpcHandler()  # worker setting
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
        self.thread_marmarainfo = QThread()
        self.thread_marmaraholderloops = QThread()
        self.thread_marmaraissue = QThread()
        self.thread_marmaratransfer = QThread()
        self.thread_getaddresstxids = QThread()
        self.thread_sendtoteam = QThread()
        self.thread_get_address_amounts = QThread()
        self.thread_extract_bootstrap = QThread()

        # Loading Gif
        # --------------------------------------------------
        self.loading = LoadingScreen()
        # --------------------------------------------------

    def center_ui(self):
        qr = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center_point)
        self.move(qr.topLeft())

    def check_app_version(self):
        base_version = configuration.version
        latest_app_tag = version.git_request_tag(version.app_api_url)
        latest_app_version = version.latest_app_release_url()
        if latest_app_tag == 'Connection Error' or latest_app_version == 'Connection Error':
            message_box = self.custom_message(self.tr('Connection Error'),
                                              self.tr('Check your internet Connection '),
                                              'information', QMessageBox.Information)
        else:
            if base_version != latest_app_tag:
                message_box = self.custom_message(self.tr('Software Update Available'),
                                                  self.tr('A new update is available. <br>Follow the link ')
                                                          + "<a href='" + latest_app_version + "'" + self.tr(">here</a>"),
                                                  'information', QMessageBox.Information)
            else:
                message_box = self.custom_message(self.tr('No Update Available'),
                                                  self.tr('Current App version is ') + base_version,
                                                  'information', QMessageBox.Information)
    def read_lang_setting(self):
        language = configuration.ApplicationConfig().get_value('USER', 'lang')
        if language:
            entries = os.listdir(configuration.configuration_path + '/language')
            for item in entries:
                if item.strip('.qm') == language:
                    self.change_lang(language)

    @pyqtSlot()
    def show_languages(self):

        languageDialog = QDialog(self)
        languageDialog.setWindowTitle(self.tr("Choose a language"))

        apply_button = QDialogButtonBox(QDialogButtonBox.Apply)
        self.lang_comboBox = QtWidgets.QComboBox()

        languageDialog.layout = QVBoxLayout()
        languageDialog.layout.addWidget(self.lang_comboBox)
        languageDialog.layout.addWidget(apply_button)
        languageDialog.setLayout(languageDialog.layout)

        entries = os.listdir(configuration.configuration_path + '/language')
        entries.sort()

        for item in entries:
            self.lang_comboBox.addItem(item.strip('.qm'))
            self.lang_comboBox.setItemIcon(entries.index(item), QIcon(
                self.icon_path + "/lang_icons" + "/" + item.strip('.qm') + ".png"))
        apply_button.clicked.connect(self.get_lang_selection)
        apply_button.clicked.connect(languageDialog.close)
        languageDialog.exec_()

    @QtCore.pyqtSlot()
    def get_lang_selection(self):
        data = self.lang_comboBox.currentText()
        if data:
            self.change_lang(data)
            configuration.ApplicationConfig().set_key_value('USER', 'lang', data)
        else:
            QtWidgets.QApplication.instance().removeTranslator(self.trans)

    def change_lang(self, data):
        self.trans.load(configuration.configuration_path + '/language/' + data + '.qm')
        QtWidgets.QApplication.instance().installTranslator(self.trans)
        self.retranslateUi(MarmaraMain)

    def show_about(self):
        QMessageBox.about(self,
                          self.tr("About Marmara Connector"),
                          self.tr("This is a software written to carry out Marmarachain node operations "
                                  "on a local or remote machine." + "<br>Version info: ") + configuration.version
                          )

    def custom_message(self, title, content, message_type, icon=None, detailed_text=None):
        """ custom_message(str, str, str: message_type = {information, question}, icon = {QMessageBox.Question,
        QMessageBox.Information, QMessageBox.Warning, QMessageBox.Critical}, str) """
        messagebox = QMessageBox()
        messagebox.setWindowTitle(title)
        messagebox.setText(content)
        messagebox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        messagebox.setDetailedText(detailed_text)
        btn_yes = None
        btn_no = None
        btn_ok = None
        if message_type == "information":
            if icon:
                messagebox.setIcon(icon)
            messagebox.setStandardButtons(QMessageBox.Ok)
            btn_ok = messagebox.button(QMessageBox.Ok)
            btn_ok.setText(self.tr("Ok"))
        if message_type == "question":
            if icon:
                messagebox.setIcon(icon)
            messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            btn_yes = messagebox.button(QMessageBox.Yes)
            btn_yes.setText(self.tr("Yes"))
            btn_no = messagebox.button(QMessageBox.No)
            btn_no.setText(self.tr("No"))
        messagebox.exec_()
        if messagebox.clickedButton() == btn_yes:
            return QMessageBox.Yes
        if messagebox.clickedButton() == btn_no:
            return QMessageBox.No
        if messagebox.clickedButton() == btn_ok:
            return QMessageBox.Ok

    def host_selection(self):
        self.main_tab.setCurrentIndex(0)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.login_message_label.clear()
        self.chain_status = False
        self.clear_tablewidgets()

    def clear_tablewidgets(self):
        self.addresses_tableWidget.clear()
        self.addresses_privkey_tableWidget.clear()
        self.transactions_tableWidget.clear()
        self.loop_request_tableWidget.clear()
        self.transferrequests_tableWidget.clear()
        self.activeloops_tableWidget.clear()
        self.transferableloops_tableWidget.clear()
        self.addresses_tableWidget.setHorizontalHeaderLabels(['', self.tr('Amount'), self.tr('Address'),
                                                              self.tr('Pubkey')])
        self.addresses_privkey_tableWidget.setHorizontalHeaderLabels([self.tr('Address'), self.tr('See')])
        self.transactions_tableWidget.setHorizontalHeaderLabels([self.tr('See on Explorer'), self.tr('Txid')])
        self.loop_request_tableWidget.setHorizontalHeaderLabels([self.tr('Confirm'), self.tr('TxId'), self.tr('Amount'),
                                                                 self.tr('Maturity'), self.tr('Receiver Pubkey'), ''])
        self.transferrequests_tableWidget.setHorizontalHeaderLabels([self.tr('Confirm'), self.tr('TxId'),
                                                                     self.tr('Amount'), self.tr('Maturity'),
                                                                     self.tr('Receiver Pubkey'), ''])
        self.activeloops_tableWidget.setHorizontalHeaderLabels([self.tr('Loop Address'), self.tr('Amount')])
        self.transferableloops_tableWidget.setHorizontalHeaderLabels([self.tr('Txid'), self.tr('Details')])

    def local_selection(self):
        marmarachain_rpc.set_connection_local()
        logging.info('is local connection: ' + str(marmarachain_rpc.is_local))
        self.check_marmara_path()
        self.download_blocks_button.show()

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        marmarachain_rpc.set_connection_remote()
        logging.info('is local connection: ' + str(marmarachain_rpc.is_local))
        self.serverpw_lineEdit.clear()
        self.download_blocks_button.hide()
        if self.server_comboBox.count() != 0:
            self.serveredit_button.setEnabled(True)
            self.connect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)
            self.serveredit_button.setEnabled(False)

    def open_debug_console(self):
        QMessageBox.information(self,
                          self.tr("Debug Console"),
                          self.tr("Under development"))

    @pyqtSlot()
    def open_log_file(self):
        text_path = configuration.log_file_path
        webbrowser.open_new(text_path)


    @pyqtSlot(int)
    def mcl_tab_changed(self, index):
        if index == 4:
            self.update_contact_tablewidget()
        if index == 2:
            self.get_contact_names_addresses()
        if index == 3:
            self.creditloop_tabWidget.setCurrentIndex(0)

    @pyqtSlot(int)
    def credit_tab_changed(self, index):
        if index == 1:
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
            self.login_page_info(str(validate))
        else:
            self.check_marmara_path()

    def worker_thread(self, thread, worker, command):
        self.start_animation()
        worker.set_command(command)
        worker.moveToThread(thread)
        worker.finished.connect(thread.quit)
        worker.finished.connect(self.stop_animation)
        thread.started.connect(worker.do_execute_rpc)
        thread.start(priority=4)
        return worker

    @pyqtSlot()
    def start_animation(self):
        self.loading.startAnimation()

    @pyqtSlot()
    def stop_animation(self):
        self.loading.stopAnimation()

    def check_marmara_path(self):
        self.worker_check_marmara_path = marmarachain_rpc.RpcHandler()
        self.worker_check_marmara_path.moveToThread(self.thread_marmarad_path)
        self.worker_check_marmara_path.finished.connect(self.thread_marmarad_path.quit)
        self.thread_marmarad_path.started.connect(self.worker_check_marmara_path.check_marmara_path)
        self.thread_marmarad_path.start(priority=4)
        self.worker_check_marmara_path.output.connect(self.check_marmara_path_output)

    @pyqtSlot(str)
    def check_marmara_path_output(self, output):
        logging.info('Checking marmara path')
        logging.info('login:' + output)
        if output == 'get marmarad path':
            self.login_page_info(self.tr('Getting marmara chain path from config file'))
            logging.info('Getting marmara chain path from config file')
        if str(output).split(' ')[0] == 'marmarad_path':
            self.login_page_info(self.tr('marmara path from configuration file : ') + str(output).split(' ')[1])
            logging.info('marmara path from configuration file : ' + str(output).split(' ')[1])
        if output == 'verifiying path':
            self.login_page_info(self.tr('Verifiying the Chain location '))
            logging.info('Verifiying the Chain location ')
        if output == 'marmarad found.':
            self.login_page_info(self.tr('Chain location verified.'))
            logging.info('Chain location verified.')
            self.chain_init()
        if output == 'need to install mcl':
            message_box = self.custom_message(self.tr('Installing Marmarachain'),
                                              self.tr('Marmarachain is not installed. Would you like to install it?'),
                                              self.tr("question"), QMessageBox.Question)
            if message_box == QMessageBox.Yes:
                logging.info('Auto-install.')
                self.main_tab.setCurrentIndex(2)
                if marmarachain_rpc.is_local:
                    self.sudo_password_lineEdit.setVisible(True)
                    if platform.system() == 'Windows':
                        self.sudo_password_lineEdit.setVisible(False)
                else:
                    self.sudo_password_lineEdit.setVisible(False)
            if message_box == QMessageBox.No:
                self.main_tab.setCurrentIndex(0)

    @pyqtSlot()
    def start_autoinstall(self):
        self.worker_autoinstall = marmarachain_rpc.Autoinstall()
        if marmarachain_rpc.is_local:
            if platform.system() == 'Windows':
                start_install = True
            else:
                if self.sudo_password_lineEdit.text():
                    self.worker_autoinstall.set_password(self.sudo_password_lineEdit.text())
                    start_install = True
                    self.sudo_password_lineEdit.clear()
                else:
                    message_box = self.custom_message(self.tr('Auto-installation does not begin'), self.tr(
                        'You need to write a password that has admin privileges'), self.tr("information"),
                                                      QMessageBox.Information)

                    start_install = False
        else:
            start_install = True
        if start_install:
            self.start_install_button.setEnabled(False)
            self.install_progress_textBrowser.append(self.tr('Starting Install ...'))
            logging.info('Starting Install')

            self.worker_autoinstall.moveToThread(self.thread_autoinstall)
            self.worker_autoinstall.finished.connect(self.thread_autoinstall.quit)
            self.thread_autoinstall.started.connect(self.worker_autoinstall.start_install)
            self.thread_autoinstall.start()
            self.worker_autoinstall.out_text.connect(self.start_autoinstall_textout)
            self.worker_autoinstall.progress.connect(self.start_autoinstall_progress)

    @pyqtSlot(str)
    def start_autoinstall_textout(self, output):
        if str(output).find('Something Went Wrong') > -1:
            message_box = self.custom_message(self.tr('Installation not completed correctly'),
                                              self.tr(output),
                                              'information', QMessageBox.Information)
        self.install_progress_textBrowser.append(output)

    @pyqtSlot(int)
    def start_autoinstall_progress(self, val):
        print(val)
        self.install_progressBar.setValue(val)
        if 96 <= val < 100:
            self.install_progressBar.setValue(100)
            message_box = self.custom_message(self.tr('Installation Completed'), self.tr('Starting Marmarachain'),
                                              'information', QMessageBox.Information)
            if message_box == QMessageBox.Ok:
                self.main_tab.setCurrentIndex(1)
                self.mcl_tab.setCurrentIndex(0)
                self.check_marmara_path()
        if val > 100:
            self.install_progressBar.setValue(0)
            self.start_install_button.setEnabled(True)
            message_box = self.custom_message(self.tr('Installation not completed correctly'),
                                              self.tr('Wrong password input. Please install again'),
                                              'information', QMessageBox.Information)

    def bottom_info(self, info):
        self.bottom_message_label.setText(info)

    def bottom_err_info(self, err_msg):
        err_result = ""
        for line in str(err_msg).splitlines():
            err_result = err_result + ' ' + str(line)
        logging.error(err_result)
        self.bottom_message_label.setText(err_result)

    def login_page_info(self, info):
        self.login_message_label.setText(info)

    # ---------------------------------------
    #  Chain initialization
    # ---------------------------------------
    @pyqtSlot()
    def chain_init(self):
        self.main_tab.setCurrentIndex(1)
        self.mcl_tab.setCurrentIndex(0)
        self.chain_stackedWidget.setCurrentIndex(0)
        logging.info('chain_status ' + str(self.chain_status))
        self.bottom_info(self.tr('chain_status ' + str(self.chain_status)))
        time.sleep(0.1)
        if not self.chain_status:
            logging.info('Checking marmarachain')
            self.bottom_info(self.tr('Checking marmarachain'))
            marmara_pid = marmarachain_rpc.mcl_chain_status()
            if len(marmara_pid[0]) > 0:
                self.bottom_info(self.tr('marmarachain has pid'))
                logging.info('marmarachain has pid')
            if len(marmara_pid[0]) == 0:
                logging.info('sending chain start command')
                self.bottom_info(self.tr('sending chain start command'))
                marmarachain_rpc.start_chain()
            self.is_chain_ready()

    def is_chain_ready(self):
        self.bottom_info(self.tr('Checking if marmarachain is ready for rpc'))
        logging.info('Checking if marmarachain is ready for rpc')
        self.start_animation()
        self.worker_getchain = marmarachain_rpc.RpcHandler()  # worker setting
        self.worker_getchain.moveToThread(self.thread_getchain)  # move object in to thread
        self.worker_getchain.finished.connect(self.thread_getchain.quit)  # when finished close thread
        self.worker_getchain.finished.connect(self.stop_animation)  # when finished close animation
        self.thread_getchain.started.connect(self.worker_getchain.is_chain_ready)  # executing respective worker func.
        self.thread_getchain.start()  # start thread
        self.worker_getchain.command_out.connect(self.chain_ready_result)  # getting results and connecting to socket
        self.worker_getchain.walletlist_out.connect(self.set_getaddresses_result)

    @pyqtSlot(tuple)
    def chain_ready_result(self, result_out):
        if result_out[0]:
            logging.info('chain is ready')
            self.bottom_info(self.tr('chain ready'))
            result = json.loads(result_out[0])
            self.chain_status = True
            self.chainstatus_button.setIcon(QIcon(self.icon_path + '/circle-active.png'))
            if result.get('version'):
                self.set_getinfo_result(result)
                self.bottom_info(self.tr('getting wallet addresses'))
                logging.info('getting wallet addresses')
            elif result.get('WalletActivatedAddresses') or result.get('WalletActivatedAddresses') == []:
                TotalAmountOnActivated = 0.0
                for activated in result.get('WalletActivatedAddresses'):
                    TotalAmountOnActivated = TotalAmountOnActivated + activated.get('amount')
                self.totalactivated_value_label.setText(str(TotalAmountOnActivated))
            else:
                self.setgenerate_result(result_out)
                self.bottom_info(self.tr('Chain init completed.'))
                logging.info('Chain init completed.')
        elif result_out[1]:
            err_result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = err_result.index('error message:') + 1
                self.bottom_info(err_result[index])
                logging.error(err_result[index])
            else:
                self.bottom_err_info(result_out[1])
                logging.error(result_out[1])

    # --------------------------------------
    # Stopping Chain
    # --------------------------------------
    @pyqtSlot()
    def stop_chain(self):
        if self.chain_status:
            self.start_animation()
            stop_chain_thread = self.stop_chain_thread()
            # self.worker_stopchain = marmarachain_rpc.RpcHandler()  # worker setting
            # self.worker_stopchain.moveToThread(self.thread_stopchain)  # putting in to thread
            # self.worker_stopchain.finished.connect(self.thread_stopchain.quit)  # when finished close thread
            stop_chain_thread.finished.connect(self.stop_animation)  # when finished close animation
            # self.thread_stopchain.started.connect(self.worker_stopchain.stopping_chain)  # executing worker function
            # self.thread_stopchain.start()
            # self.worker_stopchain.command_out.connect(self.result_stopchain)  # getting results and connecting to socket
        else:
            self.bottom_info(self.tr('Marmarachain is not ready'))
            logging.warning('Marmarachain is not ready')

    def stop_chain_thread(self):
        self.worker_stopchain = marmarachain_rpc.RpcHandler()  # worker setting
        self.worker_stopchain.moveToThread(self.thread_stopchain)  # putting in to thread
        self.worker_stopchain.finished.connect(self.thread_stopchain.quit)  # when finished close thread
        # self.worker_stopchain.finished.connect(self.stop_animation)  # when finished close animation
        self.thread_stopchain.started.connect(self.worker_stopchain.stopping_chain)  # executing worker function
        self.thread_stopchain.start()
        self.worker_stopchain.command_out.connect(self.result_stopchain)
        return self.worker_stopchain

    @pyqtSlot(tuple)
    def result_stopchain(self, result_out):
        if result_out[0]:
            print_result = ""
            for line in str(result_out[0]).splitlines():
                print_result = print_result + ' ' + str(line)
            logging.info("Stopping chain:" + print_result)
            self.bottom_info(print_result)
        if len(result_out[0]) == 0:
            self.bottom_info(self.tr('Marmarachain stopped'))
            logging.info('Marmarachain stopped')
            self.chain_status = False
            self.chainstatus_button.setIcon(QIcon(self.icon_path + '/circle-inactive.png'))
            self.update_addresses_table()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

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
            self.bottom_info(self.tr('loading getinfo values'))
            logging.info('Loading getinfo values')
            self.set_getinfo_result(getinfo_result)
            logging.info('getinfo finished')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    def set_getinfo_result(self, getinfo_result):
        if getinfo_result.get('synced'):
            self.chainsync_button.setIcon(QIcon(self.icon_path + '/circle-active.png'))
        elif not getinfo_result.get('synced'):
            self.chainsync_button.setIcon(QIcon(self.icon_path + '/circle-inactive.png'))
        if getinfo_result.get('pubkey'):
            self.pubkey_status = True
            self.current_pubkey_value.setText(str(getinfo_result['pubkey']))
        if getinfo_result.get('pubkey') is None:
            self.bottom_info(self.tr('pubkey is not set'))
            logging.warning('pubkey is not set')
            self.pubkey_status = False
            self.current_pubkey_value.setText("")
        self.difficulty_value_label.setText(str(int(getinfo_result['difficulty'])))
        self.currentblock_value_label.setText(str(getinfo_result['blocks']))
        self.longestchain_value_label.setText(str(getinfo_result['longestchain']))
        self.connections_value_label.setText(str(getinfo_result['connections']))
        self.totalnormal_value_label.setText(str(getinfo_result['balance']))
        self.bottom_info(self.tr('getinfo finished'))
        logging.info('getinfo finished')

    # -----------------------------------------------------------
    # Side panel functions
    # -----------------------------------------------------------
    @pyqtSlot()
    def refresh_side_panel(self):
        self.start_animation()
        self.bottom_info(self.tr('getting getinfo'))
        logging.info('getting getinfo')
        # self.get_getinfo()
        self.worker_sidepanel = marmarachain_rpc.RpcHandler()
        self.worker_sidepanel.moveToThread(self.thread_sidepanel)
        self.worker_sidepanel.finished.connect(self.thread_sidepanel.quit)
        self.worker_sidepanel.finished.connect(self.stop_animation)
        self.thread_sidepanel.started.connect(self.worker_sidepanel.refresh_sidepanel)
        self.thread_sidepanel.start()
        self.worker_sidepanel.command_out.connect(self.refresh_side_panel_result)
        last_update = self.tr('Last Update: ')
        # date = (str(datetime.now().date()))
        last_update_time = str(datetime.now().time().replace(microsecond=0))
        self.last_update_label.setText(last_update + last_update_time)

    @pyqtSlot(tuple)
    def refresh_side_panel_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            if result.get('version'):
                self.set_getinfo_result(result)
                self.bottom_info(self.tr('getting activated balance.'))
                logging.info('getting activated balance.')
            else:
                TotalAmountOnActivated = 0.0
                for activated in json.loads(result_out[0]).get('WalletActivatedAddresses'):
                    TotalAmountOnActivated = TotalAmountOnActivated + activated.get('amount')
                self.totalactivated_value_label.setText(str(TotalAmountOnActivated))
                self.bottom_info(self.tr('Refresh completed.'))
                logging.info('Refresh completed.')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    @pyqtSlot()
    def copyaddress_clipboard(self):
        address = self.currentaddress_value.text()
        if address != "":
            QtWidgets.QApplication.clipboard().setText(address)
            self.bottom_info(self.tr('copied ') + address)
            logging.info('copied ' + address)
        else:
            self.bottom_info(self.tr('no address value set'))
            logging.warning('no address value set')

    @pyqtSlot()
    def copypubkey_clipboard(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey != "":
            QtWidgets.QApplication.clipboard().setText(pubkey)
            self.bottom_info(self.tr('copied ') + pubkey)
            logging.info('copied ' + pubkey)
        else:
            self.bottom_info(self.tr('no pubkey value set'))
            logging.warning('no pubkey value set')

    @pyqtSlot()
    def toggle_staking(self):
        if self.staking_button.isChecked():  # Staking button status is True.
            if self.mining_button.isChecked():  # Checking mining is also active
                message_box = self.custom_message(self.tr('Turning off Mining'),
                                                  self.tr('Mining is currently on. '
                                                          'You are about to turn off mining. Are you sure?'),
                                                  "question",
                                                  QMessageBox.Question)

                if message_box == QMessageBox.Yes:
                    self.mining_button.setChecked(False)  # Close mining and set staking mode
                    self.cpu_core_selection_off()
                    logging.debug('setgenerate True 0')
                    self.setgenerate('true 0')
                if message_box == QMessageBox.No:  # Abort selecting staking and continue mining
                    self.staking_button.setChecked(False)
            else:  # set staking mode
                logging.debug('setgenerate True 0')
                self.setgenerate('true 0')
        else:  # Staking button status is False
            message_box = self.custom_message(self.tr('Turning off Staking'),
                                              self.tr('You are about to turn off staking. Are you sure?'), "question",
                                              QMessageBox.Question)

            if message_box == QMessageBox.Yes:
                logging.debug('setgenerate False')
                self.setgenerate('false')
            if message_box == QMessageBox.No:
                self.staking_button.setChecked(True)  # Abort selecting staking button

    @pyqtSlot()
    def toggle_mining(self):
        if self.mining_button.isChecked():  # Mining button status is True.
            if self.staking_button.isChecked():  # Checking staking is also active
                message_box = self.custom_message(self.tr('Turning off Staking'),
                                                  self.tr('Staking is currently active. '
                                                          'You are about to turn off staking. Are you sure?'),
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.staking_button.setChecked(False)  # Close staking and turn on mining
                    logging.debug('setgenerate True 1')
                    self.setgenerate('true 1')
                    self.cpu_core_selection_on()
                if message_box == QMessageBox.No:  # Abort selecting mining and continue staking
                    self.mining_button.setChecked(False)
            else:  # Staking is off turn on Mining mode
                logging.debug('setgenerate True 1')
                self.cpu_core_selection_on()
                self.setgenerate('true 1')
        else:  # Mining button status is False.
            message_box = self.custom_message(self.tr('Turning off Mining'),
                                              self.tr('You are about to turn off mining. Are you sure?'), "question",
                                              QMessageBox.Question)
            if message_box == QMessageBox.Yes:
                logging.debug('setgenerate False')
                self.cpu_core_selection_off()
                self.setgenerate('false')
            if message_box == QMessageBox.No:
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
        self.start_animation()
        self.worker_setgenerate = marmarachain_rpc.RpcHandler()
        self.worker_setgenerate.set_command(cp.setgenerate + ' ' + arg)
        self.worker_setgenerate.moveToThread(self.thread_setgenerate)
        self.worker_setgenerate.finished.connect(self.thread_setgenerate.quit)
        self.worker_setgenerate.finished.connect(self.stop_animation)
        self.thread_setgenerate.started.connect(self.worker_setgenerate.setgenerate)
        self.thread_setgenerate.start()
        self.worker_setgenerate.command_out.connect(self.setgenerate_result)

    @pyqtSlot(tuple)
    def setgenerate_result(self, result_out):
        if result_out[0]:
            logging.debug('\n---- getgenerate result------\n' + str(json.loads(result_out[0])))
            result = json.loads(result_out[0])
            if result.get('staking') is True and result.get('generate') is False:
                self.bottom_info(self.tr('Staking ON'))
                logging.info('Staking ON')
                self.staking_button.setChecked(True)
                self.mining_button.setChecked(False)
            if result.get('staking') is False and result.get('generate') is False:
                self.bottom_info(self.tr('Mining status is OFF'))
                logging.info('Mining status is OFF')
                self.staking_button.setChecked(False)
                self.mining_button.setChecked(False)
            if result.get('generate') is True and result.get('staking') is False:
                self.bottom_info(self.tr('Mining ON with ') + str(result.get('numthreads')))
                logging.info('Mining ON with ' + str(result.get('numthreads')))
                self.cpu_core_lineEdit.setText(str(result.get('numthreads')))
                self.cpu_core_selection_on()
                self.staking_button.setChecked(False)
                self.mining_button.setChecked(True)
        if result_out[1]:
            self.bottom_err_info(self.tr(result_out[1]))
            logging.error(result_out[1])

    @pyqtSlot()
    def setmining_cpu_core(self):
        cpu_no = self.cpu_core_lineEdit.text()
        self.setgenerate('true ' + str(cpu_no))

    @pyqtSlot()
    def calculate_amount(self):
        number_of_cups = self.cup_lineEdit.text()
        if number_of_cups == "" or int(number_of_cups) == 0:
            self.support_pushButton.setEnabled(False)
            self.support_pushButton.setText(self.tr('Support'))
        else:
            amount = int(number_of_cups) * 30
            self.support_pushButton.setEnabled(True)
            self.support_pushButton.setText(self.tr('Support') + ' (' + str(amount) + ' MCL)')

    @pyqtSlot()
    def send_coins_to_team(self):
        number_of_cups = self.cup_lineEdit.text()
        amount = int(number_of_cups) * 30
        team_address = 'RXWqisAoJKEGVyXj46Zo3fDZnZTwQA6kQE'
        self.support_pushButton.setText(self.tr('Support') + ' (' + str(amount) + ' MCL)')
        message_box = self.custom_message(self.tr('Confirm Transaction'),
                                          self.tr(
                                              f'You are about to send {amount} MCL to Marmara Core Team.'),
                                          "question",
                                          QMessageBox.Question)
        if message_box == QMessageBox.Yes:
            self.worker_sendtoteam = marmarachain_rpc.RpcHandler()
            command = cp.sendtoaddress + ' ' + team_address + ' ' + str(amount)
            sendtoteam_thread = self.worker_thread(self.thread_sendtoteam, self.worker_sendtoteam, command)
            sendtoteam_thread.command_out.connect(self.sendtoaddress_result)
        if message_box == QMessageBox.No:
            self.bottom_info(self.tr('Transaction aborted'))
            logging.info('Transaction aborted')

    # -----------------------------------------------------------
    # Chain page functions
    # -----------------------------------------------------------

    # getting addresses for address table widget
    @pyqtSlot()
    def getaddresses(self):
        self.start_animation()
        self.bottom_info(self.tr('getting wallet addresses'))
        logging.info('getting wallet addresses')
        self.worker_getaddresses = marmarachain_rpc.RpcHandler()
        self.worker_getaddresses.moveToThread(self.thread_getaddresses)
        self.worker_getaddresses.finished.connect(self.thread_getaddresses.quit)
        self.worker_getaddresses.finished.connect(self.stop_animation)
        self.thread_getaddresses.started.connect(self.worker_getaddresses.get_addresses)
        self.thread_getaddresses.start()
        self.worker_getaddresses.walletlist_out.connect(self.set_getaddresses_result)

    @pyqtSlot(list)
    def set_getaddresses_result(self, result_out):
        self.bottom_info(self.tr('Loading Addresses ...'))
        logging.info('Loading Addresses ...')
        self.addresses_tableWidget.setRowCount(len(result_out))
        logging.info('\n------wallet address list----- \n' + str(result_out))
        for row in result_out:
            row_number = result_out.index(row)
            if self.pubkey_status:
                self.addresses_tableWidget.setColumnHidden(0, True)
            btn_setpubkey = QPushButton('Set pubkey')
            self.addresses_tableWidget.setCellWidget(row_number, 0, btn_setpubkey)
            self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            for item in row:
                self.addresses_tableWidget.setItem(row_number, (row.index(item) + 1), QTableWidgetItem(str(item)))
                self.addresses_tableWidget.horizontalHeader().setSectionResizeMode((row.index(item) + 1),
                                                                                   QHeaderView.ResizeToContents)
            btn_setpubkey.clicked.connect(self.set_pubkey)
        self.bottom_info(self.tr('Loading Addresses finished'))
        logging.info('Loading Addresses finished')
        self.update_addresses_table()

    @pyqtSlot()
    def hide_addresses(self):
        if self.hide_address_checkBox.checkState():
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                if self.addresses_tableWidget.item(rowcount, 1).text() == "0.0":
                    self.addresses_tableWidget.setRowHidden(rowcount, True)
                if rowcount == 0:
                    break
        else:
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                self.addresses_tableWidget.setRowHidden(rowcount, False)
                if rowcount == 0:
                    break

    @pyqtSlot(int, int)
    def addresstable_itemcontext(self, row, column):
        item = self.addresses_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_info(self.tr("Copied  ") + str(item))

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
                btn_start.clicked.connect(self.start_chain_with_pubkey)
                if rowcount == 0:
                    break
        self.hide_addresses()

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
                logging.info('this pubkey: ' + pubkey + ' is already set')
                self.bottom_info(result_out[0])
                logging.info(result_out[0])

            message_box = self.custom_message(self.tr('Pubkey set'), str(json.loads(result_out[0])['pubkey']),
                                              "information",
                                              QMessageBox.Information)
            if message_box == QMessageBox.Ok:
                self.update_addresses_table()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    @pyqtSlot()
    def start_chain_with_pubkey(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        logging.debug(index.row())
        logging.debug(index.column())
        if index.isValid():
            pubkey = self.addresses_tableWidget.item(index.row(), 3).text()
            self.start_chain_settings(pubkey)

    def start_chain_settings(self, pubkey):
        self.bottom_info(self.tr('Chain started with pubkey'))
        logging.info('Chain started with pubkey')
        self.start_pubkey = pubkey
        startchainDialog = QDialog(self)
        startchainDialog.setWindowTitle(self.tr('Settings for Chain Start'))
        startchainDialog.layout = QVBoxLayout()

        apply_button = QDialogButtonBox(QDialogButtonBox.Apply)
        self.reindex = QtWidgets.QCheckBox('reindex' + self.tr(' (starts from beginning and re-indexes currently '
                                                               'synced blockchain data)'))
        self.reindex.setChecked(False)
        self.rescan = QtWidgets.QCheckBox('rescan' + self.tr(' (starts scanning wallet data in blockchain data)'))
        self.rescan.setChecked(False)

        startchainDialog.setLayout(startchainDialog.layout)
        startchainDialog.layout.addWidget(self.reindex)
        startchainDialog.layout.addWidget(self.rescan)
        startchainDialog.layout.addWidget(apply_button)

        apply_button.clicked.connect(self.start_chain_with_settings)
        apply_button.clicked.connect(startchainDialog.close)
        startchainDialog.exec_()

    @pyqtSlot()
    def start_chain_with_settings(self):
        reindex_param = ''
        rescan_param = ''
        if self.reindex.checkState():
            reindex_param = ' -reindex'
        if self.rescan.checkState():
            rescan_param = ' -rescan'
        start_param = self.start_pubkey + reindex_param + rescan_param
        print(start_param)
        marmarachain_rpc.start_chain(start_param)
        time.sleep(0.5)
        self.addresses_tableWidget.setColumnHidden(0, True)
        self.is_chain_ready()

    @pyqtSlot()
    def download_blocks(self):
        blocksDialog = QDialog(self)
        blocksDialog.setWindowTitle(self.tr('Download Blocks bootstrap'))
        blocksDialog.layout = QGridLayout()

        description_label = QtWidgets.QLabel()
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        browse_button = QtWidgets.QPushButton('Browse ..')
        download_button = QtWidgets.QPushButton('Download')
        description_label.setText(self.tr('You can either download or browse previously downloaded bootstrap.'))

        blocksDialog.setLayout(blocksDialog.layout)
        blocksDialog.layout.addWidget(description_label, 0, 0, 1, 3)
        blocksDialog.layout.addItem(spacer_item, 1, 0, 1, 1)
        blocksDialog.layout.addWidget(download_button, 1, 1, 1, 1)
        blocksDialog.layout.addWidget(browse_button, 1, 2, 1, 1)

        # if self.download_button.clicked():
        download_button.clicked.connect(self.download_bootstrap_via_webbrowser)
        download_button.clicked.connect(blocksDialog.close)
        browse_button.clicked.connect(self.browse_bootstrap)
        browse_button.clicked.connect(blocksDialog.close)


        blocksDialog.exec_()

    @pyqtSlot()
    def download_bootstrap_via_webbrowser(self):
        if marmarachain_rpc.is_local:
            webbrowser.open_new('https://eu.bootstrap.dexstats.info/MCL-bootstrap.tar.gz')
        else:
            pass

    @pyqtSlot()
    def browse_bootstrap(self):
        home_path = str(pathlib.Path.home())
        get_bootstrap_path = QtWidgets.QFileDialog.getOpenFileName(caption=self.tr('select bootstrap.tar.gz'),
                                                                   directory=home_path, filter='*.tar.gz')
        bootstrap_path = str(get_bootstrap_path).split(',')[0].replace('(', '').replace("'", '')
        if platform.system() == 'Darwin':
            destination_path = os.environ['HOME'] + '/Library/Application Support/Komodo/MCL'
        elif platform.system() == 'Linux':
            destination_path = os.environ['HOME'] + '/.komodo/MCL'
        elif platform.system() == 'Win64' or platform.system() == 'Windows':
            destination_path = '%s\Komodo\MCL' % os.environ['APPDATA']
        messagebox = self.custom_message(self.tr("Extracting blocks"),
                                         self.tr("Marmara chain will be closed if it is running"), 'question',
                                         QMessageBox.Question)

        if messagebox == QMessageBox.Yes:
            print(destination_path)
            self.start_animation()
            stopchain_thread = self.stop_chain_thread()
            self.worker_extract_bootstrap = marmarachain_rpc.RpcHandler()  # worker setting
            self.worker_extract_bootstrap.set_command('tar -zvxf ' + bootstrap_path + ' -C ' + destination_path)
            self.worker_extract_bootstrap.moveToThread(self.thread_extract_bootstrap)  # putting in to thread
            self.worker_extract_bootstrap.finished.connect(self.thread_extract_bootstrap.quit)
            self.worker_extract_bootstrap.finished.connect(self.stop_animation)  # when finished close animation
            self.thread_extract_bootstrap.started.connect(self.worker_extract_bootstrap.extract_bootstrap)
            stopchain_thread.finished.connect(self.thread_extract_bootstrap.start)
            self.worker_extract_bootstrap.output.connect(self.extract_bootstrap_out)
        if messagebox == QMessageBox.No:
            self.bottom_info(self.tr('Bootstrap extracting cancelled'))

    @pyqtSlot(str)
    def extract_bootstrap_out(self, output):
        self.bottom_info(output)
        if output == 'None':
            self.bottom_info(self.tr('Extracting blocks finished'))

    #     to do extract bootstrap on remote server

    # ------------------
    # Chain  --- wallet Address Add, import
    # -------------------
    @pyqtSlot()
    def get_address_page(self):
        self.chain_stackedWidget.setCurrentIndex(1)
        self.passphrase_TextEdit.clear()
        self.confirm_passphrase_TextEdit.clear()

    @pyqtSlot()
    def get_new_address(self):
        self.worker_get_newaddress = marmarachain_rpc.RpcHandler()
        message_box = self.custom_message(self.tr('Creating New Address'),
                                          self.tr("You are about to create a new address. Are you sure?"),
                                          "question",
                                          QMessageBox.Question)

        if message_box == QMessageBox.Yes:
            command = cp.getnewaddress
            getnewaddress_thread = self.worker_thread(self.thread_getnewaddress, self.worker_get_newaddress, command)
            getnewaddress_thread.command_out.connect(self.set_getnewaddress_result)

    @pyqtSlot(tuple)
    def set_getnewaddress_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            # self.bottom_info('new address = ' + str(result_out[0]))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    @pyqtSlot()
    def convertpassphrase(self):
        verified = False
        seed = self.passphrase_TextEdit.toPlainText()
        confirm_seed = self.confirm_passphrase_TextEdit.toPlainText()
        if seed:
            if seed == confirm_seed:
                verified = True
            else:
                self.bottom_info(self.tr('seed words does not match'))
                logging.warning('seed words does not match')
        else:
            self.bottom_info(self.tr('write some seed words!'))
            logging.warning('write some seed words!')
        if verified:
            self.worker_convert_passphrase = marmarachain_rpc.RpcHandler()
            command = cp.convertpassphrase + ' "' + seed + '"'
            convert_passphrase_thread = self.worker_thread(self.thread_convertpassphrase,
                                                           self.worker_convert_passphrase, command)
            convert_passphrase_thread.command_out.connect(self.convertpassphrase_result)

    @pyqtSlot(tuple)
    def convertpassphrase_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            wif = result['wif']
            message_box = self.custom_message(self.tr('Creating an Address'),
                                              self.tr("An address has been created with details below. Do you want to "
                                                      "import this address to the wallet?") +
                                                      self.tr("<br><b>Seed = </b><br>") + result['agamapassphrase'] +
                                                      self.tr("<br><b>Private Key = </b><br>") + wif +
                                                      self.tr("<br><b>Address = </b><br>") + result['address'] +
                                                      self.tr("<br><b>Pubkey = </b><br>") + result['pubkey'],
                                              "question",
                                              QMessageBox.Question)
            if message_box == QMessageBox.Yes:
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
            self.bottom_info(self.tr('write private key first'))
            logging.warning('write private key first')

    def get_importprivkey(self, wif):
        self.worker_importprivkey = marmarachain_rpc.RpcHandler()
        command = cp.importprivkey + ' ' + wif
        importprivkey_thread = self.worker_thread(self.thread_importprivkey, self.worker_importprivkey, command)
        importprivkey_thread.command_out.connect(self.set_importprivkey_result)

    @pyqtSlot(tuple)
    def set_importprivkey_result(self, result_out):
        if result_out[0]:
            self.bottom_info(str(result_out[0]))
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
            self.addresses_privkey_tableWidget.setRowCount(len(result))
            # self.addresses_privkey_tableWidget.autoScrollMargin()
            for address in result:
                row_number = result.index(address)
                btn_seeprivkey = QPushButton(qta.icon('mdi.shield-key'), '')
                btn_seeprivkey.setIconSize(QSize(32, 32))
                self.addresses_privkey_tableWidget.setCellWidget(row_number, 1, btn_seeprivkey)
                self.addresses_privkey_tableWidget.setItem(row_number, 0, QTableWidgetItem(address))
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                           QHeaderView.ResizeToContents)
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                           QHeaderView.ResizeToContents)
                btn_seeprivkey.clicked.connect(self.set_seeprivkey)

        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def set_seeprivkey(self):
        button = self.sender()
        index = self.addresses_privkey_tableWidget.indexAt(button.pos())
        if index.isValid():
            address = self.addresses_privkey_tableWidget.item(index.row(), 0).text()
            self.worker_see_privkey = marmarachain_rpc.RpcHandler()
            command = cp.dumpprivkey + ' ' + address
            see_privkey_thread = self.worker_thread(self.thread_seeprivkey, self.worker_see_privkey, command)
            see_privkey_thread.command_out.connect(self.get_seeprivkey_result)

    @pyqtSlot(tuple)
    def get_seeprivkey_result(self, result_out):
        if result_out[0]:
            message_box = self.custom_message(self.tr('Private Key'),
                                              result_out[0],
                                              "information",
                                              QMessageBox.Information)
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # --------------------------------------------------------------------
    # Wallet page functions
    # --------------------------------------------------------------------
    def marmarainfo(self, pubkey):
        self.bottom_info(self.tr('getting marmarainfo, please wait'))
        self.worker_marmarainfo = marmarachain_rpc.RpcHandler()
        command = cp.marmarainfo + ' 0 0 0 0 ' + pubkey
        marmarainfo_thread = self.worker_thread(self.thread_marmarainfo, self.worker_marmarainfo, command)
        return marmarainfo_thread

    @pyqtSlot()
    def get_address_amounts(self):
        pubkey = self.current_pubkey_value.text()
        logging.info('---- current pubkey : ' + pubkey)
        if pubkey and self.myCCActivatedAddress is None:
            marmarainfo = self.marmarainfo(pubkey)
            marmarainfo.command_out.connect(self.marmarinfo_amount_and_loops_result)
        elif pubkey and self.myCCActivatedAddress:
            self.start_animation()
            self.worker_get_address_amounts = marmarachain_rpc.RpcHandler()
            self.worker_get_address_amounts.moveToThread(self.thread_get_address_amounts)
            self.worker_get_address_amounts.finished.connect(self.thread_get_address_amounts.quit)
            self.worker_get_address_amounts.finished.connect(self.stop_animation)
            self.thread_get_address_amounts.started.connect(self.worker_get_address_amounts.get_balances)
            self.thread_get_address_amounts.start(priority=4)
            self.worker_get_address_amounts.command_out.connect(self.set_address_amounts)
        else:
            self.bottom_info(self.tr('pubkey is not set!'))
            logging.warning('pubkey is not set!')

    @pyqtSlot(tuple)
    def set_address_amounts(self, result_out):
        if result_out[3] == 0:
            self.wallet_total_normal_value.setText(str(result_out[0]))
            for address in result_out[1]:
                if address[0] == self.currentaddress_value.text():
                    self.normal_amount_value.setText(str(address[1]))
            TotalAmountOnActivated = 0.0
            for activated in result_out[2].get('WalletActivatedAddresses'):
                TotalAmountOnActivated = TotalAmountOnActivated + activated.get('amount')
                if activated.get('activatedaddress') == self.myCCActivatedAddress:
                    self.activated_amount_value.setText(str(activated.get('amount')))
            self.wallet_total_activated_value.setText(str(TotalAmountOnActivated))
        elif result_out[3] == 1:
            self.bottom_info(self.tr('Error getting address amounts'))
            logging.warning(str(result_out[0]))
            logging.warning(str(result_out[1]))
            logging.warning(str(result_out[2]))



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
            logging.info(result)
            if result['result'] == 'success':
                message_box = self.custom_message(self.tr('Confirm Transaction'),
                                                  self.tr('You are about to activate ') + self.lock_amount_value.text()
                                                  + ' MCL',
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result['hex'])
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')
            if result.get('error'):
                self.bottom_info(str(result['error']))
                logging.error(str(result['error']))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
                logging.error(result_out[1])
            result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])
                logging.error(result[index])

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
            logging.info(result_out[0])
            logging.info(str(result_out[0]).find('result'))
            if str(result_out[0]).find('result') == -1:
                message_box = self.custom_message(self.tr('Confirm Transaction'),
                                                  self.tr('You are about to unlock ') +
                                                  self.unlock_amount_value.text() + ' MCL',
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result_out[0])
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')
            else:
                result = json.loads(result_out[0])
                logging.info(result)
                if result.get('result') == "error":
                    self.bottom_info(result.get('error'))
                    logging.error(result.get('error'))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
                logging.error(result_out[1])
            result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])
                logging.error(result[index])

    # --------------------------------------------------------------------
    # sending raw transaction
    # --------------------------------------------------------------------

    def sendrawtransaction(self, hex):
        self.bottom_info(self.tr('Signing transaction'))
        logging.info('Signing transaction')
        self.worker_sendrawtransaction = marmarachain_rpc.RpcHandler()
        command = cp.sendrawtransaction + ' ' + hex
        time.sleep(0.1)
        sendrawtransaction_thread = self.worker_thread(self.thread_sendrawtransaction, self.worker_sendrawtransaction,
                                                       command)
        sendrawtransaction_thread.command_out.connect(self.sendrawtransaction_result)

    @pyqtSlot(tuple)
    def sendrawtransaction_result(self, result_out):
        if result_out[0]:
            self.bottom_info('txid: ' + str(result_out[0]).replace('\n', ''))
            logging.info('txid: ' + str(result_out[0]).replace('\n', ''))
            time.sleep(0.2)  # wait for loading screen disappear
            self.custom_message(self.tr('Transaction Successful'), self.tr(f'TxId : {result_out[0]}'), "information")
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    # --------------------------------------------------------------------
    # Coin Send-Receive  page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def create_currentaddress_qrcode(self):
        # creating a pix map of qr code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=7, border=1)
        qr.add_data(self.currentaddress_value.text())
        # set image to the Icon
        qr_image = qr.make_image(image_factory=Image).pixmap()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setIconPixmap(qr_image)
        msg.setWindowTitle(self.tr('Qr Code'))
        msg.exec_()

    @pyqtSlot()
    def sendtoaddress(self):
        if self.receiver_address_lineEdit.text() == "":
            self.bottom_info(self.tr('enter a receiver address'))
            logging.info('enter a receiver address')
        else:
            if self.sending_amount_lineEdit.text() == "":
                self.bottom_info(self.tr('enter some amount to send'))
                logging.warning('enter some amount to send')
            else:
                message_box = self.custom_message(self.tr('Confirm Transaction'),
                                                  self.tr('You are about to send ') +
                                                  self.sending_amount_lineEdit.text() + self.tr(' MCL to ') +
                                                  self.receiver_address_lineEdit.text(),
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.worker_sendtoaddress = marmarachain_rpc.RpcHandler()
                    command = cp.sendtoaddress + ' ' + self.receiver_address_lineEdit.text() + ' ' + self.sending_amount_lineEdit.text()
                    sendtoaddress_thread = self.worker_thread(self.thread_sendtoaddress, self.worker_sendtoaddress,
                                                              command)
                    sendtoaddress_thread.command_out.connect(self.sendtoaddress_result)
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')

    @pyqtSlot(tuple)
    def sendtoaddress_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            self.bottom_info('txid : ' + str(result_out[0]).replace('\n', ''))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
                logging.error(result_out[1])
            result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])
                logging.error(result[index])

    @pyqtSlot()
    def getaddresstxids(self):
        address = self.currentaddress_value.text()
        start_date = self.transactions_startdate_dateTimeEdit.dateTime()
        end_date = self.transactions_endtdate_dateTimeEdit.dateTime()
        start_height = int(self.currentblock_value_label.text()) - int(self.change_datetime_to_block_age(start_date))
        end_height = int(self.currentblock_value_label.text()) - int(self.change_datetime_to_block_age(end_date))
        if address == "":
            self.bottom_info(self.tr('A pubkey is not set yet! Please set a pubkey first.'))
            logging.info('A pubkey is not set yet! Please set a pubkey first.')
        else:
            self.worker_getaddresstxids = marmarachain_rpc.RpcHandler()
            command = cp.getaddresstxids + " '" + '{"addresses": ["' + address + '"], "start":' + str(
                start_height) + ', "end":' + str(end_height) + "}'"
            gettxids_thread = self.worker_thread(self.thread_getaddresstxids, self.worker_getaddresstxids, command)
            gettxids_thread.command_out.connect(self.getaddresstxids_result)

    @pyqtSlot(tuple)
    def getaddresstxids_result(self, result_out):
        if result_out[0]:
            txids = json.loads(result_out[0])
            self.transactions_tableWidget.setRowCount(len(txids))
            if len(txids) == 0:
                self.bottom_info(self.tr("No transaction between selected dates."))
                logging.info("No transaction between selected dates.")
            else:
                for txid in txids:
                    row_number = txids.index(txid)
                    btn_explorer = QPushButton(qta.icon('mdi.firefox'), '')
                    btn_explorer.setIconSize(QSize(24, 24))
                    self.transactions_tableWidget.setCellWidget(row_number, 0, btn_explorer)
                    self.transactions_tableWidget.setItem(row_number, 1, QTableWidgetItem(str(txid)))
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                          QHeaderView.ResizeToContents)
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                          QHeaderView.ResizeToContents)
                    btn_explorer.clicked.connect(self.open_in_explorer)

        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    @pyqtSlot()
    def open_in_explorer(self):
        button = self.sender()
        index = self.transactions_tableWidget.indexAt(button.pos())
        if index.isValid():
            tx_id = self.transactions_tableWidget.item(index.row(), 1).text()
            url = 'https://explorer.marmara.io/tx/' + tx_id
            webbrowser.open_new(url)

    @pyqtSlot(int, int)
    def transaction_itemcontext(self, row, column):
        item = self.transactions_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_info(self.tr("Copied ") + str(item))

    # -------------------------------------------------------------------
    # Credit loops functions
    # --------------------------------------------------------------------

    # function name: change_datetime_to_block_age
    # purpose: changes datetime to block age with given args date
    # usage: Calling function calculates the int value of block age between current datetime and date arg
    # return: str value of block_age
    def change_datetime_to_block_age(self, date):
        selected_datetime = date.toPyDateTime()
        now = datetime.now()
        if selected_datetime > now:
            time_diff = selected_datetime - now
        if now > selected_datetime:
            time_diff = now - selected_datetime
        block_age = int(time_diff.total_seconds() / 60)
        return str(block_age)

    def change_block_to_date(self, block):
        block_diff = int(block) - int(self.longestchain_value_label.text())
        maturity_date = datetime.now() + timedelta(minutes=block_diff)
        maturity_date_format = str(maturity_date.day) + "/" + str(maturity_date.month) + "/" + str(maturity_date.year)
        return maturity_date_format

    def check_pubkey_contact_name(self, pubkey):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        known_pubkey = pubkey
        for contact in contacts_data:  # each contact set in contacts_data
            if contact[2] == pubkey:  # contact[2] contact pubkey
                known_pubkey = contact[0]  # contact[0] contact name
                break
        return known_pubkey

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
            logging.info('maxage ' + str(maxage))
        self.bottom_info(self.tr('searching incoming loop requests'))
        logging.info('querying incoming loop requests with marmarareceivelist')
        self.worker_marmarareceivelist = marmarachain_rpc.RpcHandler()
        command = cp.marmarareceivelist + ' ' + self.current_pubkey_value.text() + ' ' + str(maxage)
        marmarareceivelist_thread = self.worker_thread(self.thread_marmarareceivelist, self.worker_marmarareceivelist,
                                                       command)
        marmarareceivelist_thread.command_out.connect(self.search_marmarareceivelist_result)

    @pyqtSlot(tuple)
    def search_marmarareceivelist_result(self, result_out):
        if result_out[0]:
            self.bottom_info(self.tr('finished searching incoming loop requests'))
            logging.info('finished querying incoming loop requests')
            result = json.loads(result_out[0])
            self.loop_request_tableWidget.setRowCount(len(result))
            loop_create_request_list = []
            loop_transfer_request_list = []
            for item in result:
                tx_id = item.get('txid')
                func_id = item.get('funcid')
                amount = item.get('amount')
                matures = item.get('matures')
                maturity = self.change_block_to_date(matures)
                receive_pk = item.get('receivepk')
                receive_pubkey = self.check_pubkey_contact_name(receive_pk)
                # issuer_pk = item.get('issuerpk')
                if func_id == 'B':
                    row = [tx_id, amount, maturity, receive_pubkey, receive_pk]
                    loop_create_request_list.append(row)
                if func_id == 'R':
                    row = [tx_id, amount, maturity, receive_pubkey, receive_pk]
                    loop_transfer_request_list.append(row)
            self.set_credit_request_table(loop_create_request_list)
            self.set_transfer_request_table(loop_transfer_request_list)
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    def set_credit_request_table(self, credit_request_list):
        self.loop_request_tableWidget.setRowCount(len(credit_request_list))
        self.loop_request_tableWidget.setColumnHidden(5, True)
        for row in credit_request_list:
            row_number = credit_request_list.index(row)
            btn_review = QPushButton(qta.icon('mdi.text-box-check-outline'), '')
            btn_review.setIconSize(QSize(24, 24))
            self.loop_request_tableWidget.setCellWidget(row_number, 0, btn_review)
            self.loop_request_tableWidget.setItem(row_number, 1, QTableWidgetItem(str(row[0])))
            self.loop_request_tableWidget.setItem(row_number, 2, QTableWidgetItem(str(row[1])))
            self.loop_request_tableWidget.setItem(row_number, 3, QTableWidgetItem(str(row[2])))
            self.loop_request_tableWidget.setItem(row_number, 4, QTableWidgetItem(str(row[3])))
            self.loop_request_tableWidget.setItem(row_number, 5, QTableWidgetItem(str(row[4])))
            self.loop_request_tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.loop_request_tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.loop_request_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.loop_request_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.loop_request_tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            btn_review.clicked.connect(self.review_creditloop_request)

    @pyqtSlot()
    def review_creditloop_request(self):
        button = self.sender()
        index = self.loop_request_tableWidget.indexAt(button.pos())
        if index.isValid():
            tx_id = self.loop_request_tableWidget.item(index.row(), 1).text()
            receiver_pk = self.loop_request_tableWidget.item(index.row(), 5).text()
            self.marmaraissue(receiver_pk, tx_id)

    def set_transfer_request_table(self, transfer_request_list):
        self.transferrequests_tableWidget.setRowCount(len(transfer_request_list))
        self.transferrequests_tableWidget.setColumnHidden(5, True)
        for row in transfer_request_list:
            row_number = transfer_request_list.index(row)
            btn_review = QPushButton(qta.icon('mdi.text-box-check-outline'), '')
            btn_review.setIconSize(QSize(24, 24))
            self.transferrequests_tableWidget.setCellWidget(row_number, 0, btn_review)
            self.transferrequests_tableWidget.setItem(row_number, 1, QTableWidgetItem(str(row[0])))
            self.transferrequests_tableWidget.setItem(row_number, 2, QTableWidgetItem(str(row[1])))
            self.transferrequests_tableWidget.setItem(row_number, 3, QTableWidgetItem(str(row[2])))
            self.transferrequests_tableWidget.setItem(row_number, 4, QTableWidgetItem(str(row[3])))
            self.transferrequests_tableWidget.setItem(row_number, 5, QTableWidgetItem(str(row[4])))
            self.transferrequests_tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.transferrequests_tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.transferrequests_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.transferrequests_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.transferrequests_tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            btn_review.clicked.connect(self.review_credittransfer_request)

    @pyqtSlot()
    def review_credittransfer_request(self):
        button = self.sender()
        index = self.transferrequests_tableWidget.indexAt(button.pos())
        if index.isValid():
            tx_id = self.transferrequests_tableWidget.item(index.row(), 1).text()
            receiver_pk = self.transferrequests_tableWidget.item(index.row(), 5).text()
            self.marmaratransfer(receiver_pk, tx_id)

    def marmaraissue(self, receiver_pk, txid):
        command = cp.marmaraissue + ' ' + receiver_pk + " '" + '{"avalcount":"0", "autosettlement":"true", ' \
                                                               '"autoinsurance":"true", "disputeexpires":"offset", ' \
                                                               '"EscrowOn":"false", "BlockageAmount":"0" }' + "' " + txid
        self.worker_marmaraissue = marmarachain_rpc.RpcHandler()
        marmaraissue_thread = self.worker_thread(self.thread_marmaraissue, self.worker_marmaraissue, command)
        marmaraissue_thread.command_out.connect(self.marmaraissue_result)

    @pyqtSlot(tuple)
    def marmaraissue_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                message_box = self.custom_message(self.tr('Create Credit Loop'),
                                                  self.tr(
                                                      "You are about to create credit loop with given details below:") +
                                                      "<br><b>Tx ID = </b>" + result.get('requesttxid') +
                                                      "<br><b>Pubkey = </b>" + result.get('receiverpk'), "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result.get('hex'))
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
        elif result_out[1]:
            logging.error(result_out[1])

    def marmaratransfer(self, receiver_pk, tx_id):
        command = cp.marmaratransfer + ' ' + receiver_pk + " '" + '{"avalcount":"0"}' + "' " + tx_id
        self.worker_marmaratransfer = marmarachain_rpc.RpcHandler()
        marmaratransfer_thread = self.worker_thread(self.thread_marmaratransfer, self.worker_marmaratransfer, command)
        marmaratransfer_thread.command_out.connect(self.marmaratransfer_result)

    @pyqtSlot(tuple)
    def marmaratransfer_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                message_box = self.custom_message(self.tr('Transfer Credit Loop'),
                                                  self.tr("You are about to transfer you credit loop with given "
                                                          "details below:") +
                                                  "<br><b>baton txid = </b>" + result.get('batontxid') +
                                                  "<br><b>Pubkey = </b>" + result.get('receiverpk'),
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result.get('hex'))
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

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
            self.bottom_info(self.tr('preparing loop request'))
            marmarareceive_thread = self.worker_thread(self.thread_marmarareceive, self.worker_marmarareceive, command)
            marmarareceive_thread.command_out.connect(self.marmarareceive_result)
        else:
            self.bottom_info(self.tr('cannot make a credit loop request with empty fields'))
            logging.warning('cannot make a credit loop request with empty fields')

    @pyqtSlot(tuple)
    def marmarareceive_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                logging.info(result)
                message_box = self.custom_message(self.tr('Confirm Transaction'),
                                                  self.tr('You are about to make a credit loop request'),
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result.get('hex'))
                if message_box == QMessageBox.No:
                    self.bottom_info('Transaction aborted')
                    logging.info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    # function name: marmararecieve_transfer
    # purpose:  holder makes a marmarareceive request to the endorser to get the credit for selling the goods/services
    @pyqtSlot()
    def marmararecieve_transfer(self):
        senderpk = self.transfer_senderpubkey_lineEdit.text()
        baton = self.transfer_baton_lineEdit.text()
        if senderpk and baton:
            self.worker_marmarareceive_transfer = marmarachain_rpc.RpcHandler()
            command = cp.marmarareceive + ' ' + senderpk + ' ' + baton + " '" + '{"avalcount":"0"}' + "'"
            marmarareceive_transfer_thread = self.worker_thread(self.thread_marmarareceive_transfer,
                                                                self.worker_marmarareceive_transfer, command)
            marmarareceive_transfer_thread.command_out.connect(self.marmararecieve_transfer_result)
        else:
            self.bottom_info(self.tr('cannot make a receive transfer request with empty fields'))
            logging.warning('cannot make a receive transfer request with empty fields')

    @pyqtSlot(tuple)
    def marmararecieve_transfer_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                logging.info(result)
                message_box = self.custom_message(self.tr('Confirm Transaction'),
                                                  self.tr('You are about to make a request to the endorser'),
                                                  "question",
                                                  QMessageBox.Question)
                if message_box == QMessageBox.Yes:
                    self.sendrawtransaction(result.get('hex'))
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
        elif result_out[1]:
            if self.chain_status is False:
                self.bottom_err_info(result_out[1])
            result = str(result_out[1]).splitlines()
            if str(result_out[1]).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])
                logging.error(result[index])

    # -------------------------------------------------------------------
    # Total Credit Loops page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def search_active_loops(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey:
            marmarainfo = self.marmarainfo(pubkey)
            marmarainfo.command_out.connect(self.marmarinfo_amount_and_loops_result)
        else:
            self.bottom_info('pubkey not set!')
            self.clear_search_active_loops_result()

    @pyqtSlot(tuple)
    def marmarinfo_amount_and_loops_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                self.myCCActivatedAddress = str(result.get('myCCActivatedAddress'))
                self.normal_amount_value.setText(str(result.get('myPubkeyNormalAmount')))
                self.wallet_total_normal_value.setText(str(result.get('myWalletNormalAmount')))
                self.activated_amount_value.setText(str(result.get('myActivatedAmount')))
                self.wallet_total_activated_value.setText(str(result.get('myTotalAmountOnActivatedAddress')))
                self.bottom_info(self.tr('getting address amounts finished'))
                loops = result.get('Loops')
                self.activeloops_total_amount_value_label.setText(str(result.get('TotalLockedInLoop')))
                self.closedloops_total_amount_value_label.setText(str(result.get('totalclosed')))
                self.activeloops_pending_number_value_label.setText(str(result.get('numpending')))
                self.closedloops_total_number_value_label.setText(str(result.get('numclosed')))
                self.activeloops_tableWidget.setRowCount(len(loops))
                for item in loops:
                    row_number = loops.index(item)
                    self.activeloops_tableWidget.setItem(row_number, 0, QTableWidgetItem(str(item.get('LoopAddress'))))
                    self.activeloops_tableWidget.setItem(row_number, 1,
                                                         QTableWidgetItem(str(item.get('myAmountLockedInLoop'))))
                    self.activeloops_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                         QHeaderView.ResizeToContents)
                    self.activeloops_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                         QHeaderView.ResizeToContents)
                self.bottom_info(self.tr('finished searching marmara blockchain for all blocks for the set pubkey'))
                logging.info('finished searching marmara blockchain for all blocks for the set pubkey')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
                self.clear_search_active_loops_result()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    def clear_search_active_loops_result(self):
        self.activeloops_total_amount_value_label.clear()
        self.closedloops_total_amount_value_label.clear()
        self.activeloops_total_number_value_label.clear()
        self.closedloops_total_number_value_label.clear()

    @pyqtSlot()
    def set_transferable_mature_date_state(self):
        if self.transferable_matures_checkBox.checkState():
            self.transferable_maturesfrom_dateTimeEdit.setEnabled(False)
            self.transferable_maturesto_dateTimeEdit.setEnabled(False)
        else:
            self.transferable_maturesfrom_dateTimeEdit.setEnabled(True)
            self.transferable_maturesto_dateTimeEdit.setEnabled(True)

    @pyqtSlot()
    def set_transferable_amount_state(self):
        if self.transferable_amount_checkBox.checkState():
            self.transferable_minamount_lineEdit.setEnabled(False)
            self.transferable_maxamount_lineEdit.setEnabled(False)
        else:
            self.transferable_minamount_lineEdit.setEnabled(True)
            self.transferable_maxamount_lineEdit.setEnabled(True)

    @pyqtSlot()
    def marmaraholderloops(self):
        if self.transferable_matures_checkBox.checkState():
            firstheight = '0'
            lastheight = '0'
        else:
            matures_from_date = self.transferable_maturesfrom_dateTimeEdit.dateTime()
            matures_to_date = self.transferable_maturesto_dateTimeEdit.dateTime()
            firstheight = int(self.currentblock_value_label.text()) - int(
                self.change_datetime_to_block_age(matures_from_date))
            lastheight = int(self.currentblock_value_label.text()) + int(
                self.change_datetime_to_block_age(matures_to_date))

        if self.transferable_amount_checkBox.checkState():
            minamount = '0'
            maxamount = '0'
        else:
            minamount = self.transferable_minamount_lineEdit.text()
            maxamount = self.transferable_maxamount_lineEdit.text()
        if minamount > maxamount:
            maxamount = minamount
            self.transferable_maxamount_lineEdit.setText(maxamount)
        if int(firstheight) <= int(lastheight):
            self.worker_marmaraholderloops = marmarachain_rpc.RpcHandler()
            command = cp.marmaraholderloops + ' ' + str(firstheight) + ' ' + str(lastheight) + ' ' + str(minamount) + \
                      ' ' + str(maxamount) + ' ' + self.current_pubkey_value.text()
            marmaraholderloops_thread = self.worker_thread(self.thread_marmaraholderloops,
                                                           self.worker_marmaraholderloops,
                                                           command)
            marmaraholderloops_thread.command_out.connect(self.marmaraholderloops_result)
        else:
            response = self.custom_message(self.tr("Date Selection Warning"),
                                           self.tr('Make sure that the from and to dates are selected correctly.'),
                                           "information",
                                           QMessageBox.Warning)

    @pyqtSlot(tuple)
    def marmaraholderloops_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            logging.info(result)
            logging.info("numpending: " + str(result.get('numpending')))
            issuances = result.get('issuances')
            self.transferableloops_tableWidget.setRowCount(result.get('numpending'))
            for item in issuances:
                row_number = issuances.index(item)
                btn_detail = QPushButton(qta.icon('mdi.dots-horizontal'), '')
                btn_detail.setIconSize(QSize(24, 24))
                self.transferableloops_tableWidget.setItem(row_number, 0, QTableWidgetItem(str(item)))
                self.transferableloops_tableWidget.setCellWidget(row_number, 1, btn_detail)
                self.transferableloops_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                           QHeaderView.ResizeToContents)
                self.transferableloops_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                           QHeaderView.ResizeToContents)
                btn_detail.clicked.connect(self.see_holderloop_detail)
        elif result_out[1]:
            logging.error(result_out[1])

    @pyqtSlot()
    def see_holderloop_detail(self):
        button = self.sender()
        index = self.transferableloops_tableWidget.indexAt(button.pos())
        if index.isValid():
            tx_id = self.transferableloops_tableWidget.item(index.row(), 0).text()
            marmaracreditloop = self.marmaracreditloop(tx_id)
            marmaracreditloop.command_out.connect(self.holderloop_detail_result)

    @pyqtSlot(tuple)
    def holderloop_detail_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            maturity = self.change_block_to_date(result.get('matures'))
            message_box = self.custom_message(self.tr("Credit loop detail"), self.tr("Credit loop details.") +
                                              self.tr("<br><b>Tx ID = </b>") + str(result.get('batontxid')) +
                                              self.tr("<br><b>Amount = </b>") + str(result.get('amount')) +
                                              self.tr("<br><b>Maturity = </b>") + str(maturity), "information",
                                              QMessageBox.Information)
        elif result_out[1]:
            logging.error(result_out[1])
            self.bottom_err_info(result_out[1])

    # -------------------------------------------------------------------
    # Credit Loop Queries functions
    # --------------------------------------------------------------------

    @pyqtSlot()
    def search_any_pubkey_loops(self):
        pubkey = self.loopqueries_pubkey_lineEdit.text()
        if pubkey:
            marmarainfo = self.marmarainfo(pubkey)
            marmarainfo.command_out.connect(self.get_search_any_pubkey_loops_result)
        else:
            self.bottom_info('write pubkey to search!')
            logging.info('write pubkey to search!')
            self.clear_lq_txid_search_result()

    def get_search_any_pubkey_loops_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                self.lq_pubkey_address_label_value.setText(str(result.get('myNormalAddress')))
                self.lq_pubkeynormalamount_value_label.setText(str(result.get('myPubkeyNormalAmount')))
                self.lq_pubkeyactivatedamount_value_label.setText(str(result.get('myActivatedAmount')))
                self.lq_activeloopno_value_label.setText(str(result.get('numpending')))
                self.lq_pubkeyloopamount_value_label.setText(str(result.get('TotalLockedInLoop')))
                self.lq_closedloopno_value_label.setText(str(result.get('numclosed')))
                self.lq_pubkeyclosedloopamount_value_label.setText(str(result.get('totalclosed')))
                self.bottom_info(self.tr('finished searching marmarainfo'))
                logging.info('finished searching marmarainfo')
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
                self.clear_lq_pubkey_result()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    def clear_lq_pubkey_result(self):
        self.lq_pubkeynormalamount_value_label.clear()
        self.lq_pubkeyactivatedamount_value_label.clear()
        self.lq_activeloopno_value_label.clear()
        self.lq_pubkeyloopamount_value_label.clear()
        self.lq_closedloopno_value_label.clear()
        self.lq_pubkeyclosedloopamount_value_label.clear()

    def marmaracreditloop(self, txid):
        self.bottom_info(self.tr('getting credit loop info, please wait'))
        logging.info('getting credit loop info, please wait')
        self.worker_marmaracreditloop = marmarachain_rpc.RpcHandler()
        command = cp.marmaracreditloop + ' ' + txid
        marmaracreditloop_thread = self.worker_thread(self.thread_marmaracreditloop, self.worker_marmaracreditloop,
                                                      command)
        return marmaracreditloop_thread

    @pyqtSlot()
    def search_loop_txid(self):
        txid = self.loopsearch_txid_lineEdit.text()
        if txid:
            marmaracreditloop = self.marmaracreditloop(txid)
            marmaracreditloop.command_out.connect(self.search_loop_txid_result)
        else:
            self.bottom_info(self.tr('write loop transaction id to search!'))
            logging.info('write loop transaction id to search!')
            self.clear_lq_txid_search_result()

    @pyqtSlot(tuple)
    def search_loop_txid_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            logging.info(result)
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                self.clear_lq_txid_search_result()
            if result.get('result') == "success":
                creditloop = result.get('creditloop')
                self.loopquery_baton_value.setText(str(result.get('batontxid')))
                self.loopquery_amount_value.setText(str(result.get('amount')))
                self.loopquery_currency_value.setText(result.get('currency'))
                self.loopquery_matures_value.setText(str(result.get('matures')))
                self.loopquery_batonpk_value.setText(str(result.get('batonpk')))
                self.loopquery_issuer_value.setText(str((creditloop[0]).get('issuerpk')))
                self.loopquery_transfercount_value.setText(str(result.get('n')))
                self.bottom_info(self.tr('credit loop info finished'))
                logging.info('credit loop info finished')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])
            logging.error(result_out[1])

    def clear_lq_txid_search_result(self):
        self.loopquery_baton_value.clear()
        self.loopquery_amount_value.clear()
        self.loopquery_currency_value.clear()
        self.loopquery_matures_value.clear()
        self.loopquery_issuer_value.clear()

    # -------------------------------------------------------------------
    # Getting Contacts into comboboxes
    # --------------------------------------------------------------------
    def get_contact_names_addresses(self):
        self.contacts_address_comboBox.clear()
        self.receiver_address_lineEdit.clear()
        self.contacts_address_comboBox.addItem(self.tr('Contacts'))
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
        self.contactpubkey_makeloop_comboBox.addItem(self.tr('Contacts'))
        self.contactpubkey_transferrequest_comboBox.addItem(self.tr('Contacts'))
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
            response = self.custom_message(self.tr("Error Adding Contact"),
                                           unique_record.get('error'),
                                           "information",
                                           QMessageBox.Warning)
        if not unique_record:
            configuration.ContactsSettings().add_csv_file(new_record)
            read_contacts_data = configuration.ContactsSettings().read_csv_file()
            self.update_contact_tablewidget(read_contacts_data)
            self.clear_contacts_line_edit()
            response = self.custom_message(self.tr('Added Contact'),
                                           self.tr('It is your responsibility that the information you have entered '
                                                   'are correct and valid.'),
                                           "information",
                                           QMessageBox.Information)

    def unique_contacts(self, name, address, pubkey, contacts_data=None):
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContactsSettings().read_csv_file()
        if name == address:
            return {'error': self.tr('Name and Address cannot be the same!')}
        if name == pubkey:
            return {'error': self.tr('Name and Pubkey cannot be the same!')}
        if pubkey == address:
            return {'error': self.tr('Pubkey and Address cannot be the same!')}
        for row in contacts_data:
            if row[0] == name:
                logging.error('same contact name exists')
                return {'error': self.tr('Same name exists')}
            if row[1] == address:
                logging.error('same address exists')
                return {'error': self.tr('Same address exists')}
            if row[2] == pubkey:
                logging.error('same pubkey exists')
                return {'error': self.tr('Same pubkey exists')}
            if not name or not address or not pubkey:
                logging.error('empty record')
                return {'error': self.tr('cannot be an empty record')}
            # is_valid_address = row[1] # check if address is valid
            # if is_valid_address == False:
            #     return {'error': self.tr('address is not valid')}
            # is_valid_pubkey = row[2] #  check if pubkey is valid
            # if is_valid_pubkey == False:
            #     return {'error': self.tr('pubkey is not valid')}

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
                                                                                      QHeaderView.ResizeToContents)

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
                self.bottom_info(unique_record.get('error'))
                logging.error(unique_record.get('error'))
            if not unique_record:
                read_contacts_data[self.contact_editing_row + 1][0] = contact_name  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][1] = contact_address  # +1 for exclude header
                read_contacts_data[self.contact_editing_row + 1][2] = contact_pubkey  # +1 for exclude header
                configuration.ContactsSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
        else:
            message_box = self.custom_message(self.tr('Error Updating Contact'),
                                              self.tr('You did not select a contact from table.'),
                                              "information",
                                              QMessageBox.Information)

    @pyqtSlot()
    def delete_contact(self):
        if self.contact_editing_row is not None:
            message_box = self.custom_message(self.tr('Deleting Contact'),
                                              self.tr('Are you sure to delete the contact from the list?'),
                                              "question",
                                              QMessageBox.Question)
            if message_box == QMessageBox.Yes:
                read_contacts_data = configuration.ContactsSettings().read_csv_file()
                del read_contacts_data[self.contact_editing_row + 1]  # +1 for exclude header
                configuration.ContactsSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
            else:
                self.clear_contacts_line_edit()
        else:
            message_box = self.custom_message(self.tr('Error Deleting Contact'),
                                              self.tr('You did not select a contact from table.'),
                                              "information",
                                              QMessageBox.Information)
    # ------------------------
    # Stats Page
    # ------------------------

    @pyqtSlot()
    def get_marmara_stats(self):
        self.bottom_info(self.tr('getting stats values'))
        mcl_stats = version.get_marmara_stats()
        if mcl_stats != 'error':
            mcl_stats_info = mcl_stats.get('info')
            self.stats_height_value_label.setText(str(mcl_stats_info.get('height')))
            self.stats_normal_label_value.setText(str(mcl_stats_info.get('TotalNormals')))
            self.stats_activated_label_value.setText(str(mcl_stats_info.get('TotalActivated')))
            self.stats_in_loops_label_value.setText(str(mcl_stats_info.get('TotalLockedInLoops')))
            self.bottom_info(self.tr('stats values retrieved'))
            self.stats_refresh_pushButton.setEnabled(False)
            self.stats_calculate_pushButton.setEnabled(True)
            QtCore.QTimer.singleShot(60000, self.stat_refresh_enable)  # after 60 second it will enable button
        else:
            self.bottom_err_info(self.tr('Error in getting stats values'))

    @pyqtSlot()
    def stat_refresh_enable(self):
        self.stats_refresh_pushButton.setEnabled(True)

    @pyqtSlot()
    def calculate_estimated_stake(self):
        total_activated = float(self.stats_activated_label_value.text())
        total_inloops = float(self.stats_in_loops_label_value.text())
        if self.stats_amount_in_activated_lineEdit.text():
            amount_activated = float(self.stats_amount_in_activated_lineEdit.text())
        else:
            amount_activated = 0
            self.stats_amount_in_activated_lineEdit.setText('0')
        if self.stats_amount_in_loops_lineEdit.text():
            amount_inloops = float(self.stats_amount_in_loops_lineEdit.text())
        else:
            amount_inloops = 0
            self.stats_amount_in_loops_lineEdit.setText('0')
        calculation = (((amount_activated/total_activated) + (amount_inloops/total_inloops)*3)/4)*32400
        self.stats_estimated_staking_label_value.setText(str(calculation))
        # 30 * 60 * 24 * 0,75  = 32400

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
            # self.get_server_combobox_names()
            # self.login_stackedWidget.setCurrentIndex(1)
            self.remote_selection()
        else:
            self.login_message_label.setText(self.tr('please insert all values'))

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
            self.login_message_label.setText(self.tr('please insert all values'))

    @pyqtSlot()
    def delete_server_setting(self):
        server_list = configuration.ServerSettings().read_file()
        del server_list[self.server_comboBox.currentIndex()]
        configuration.ServerSettings().delete_record(server_list)
        self.remote_selection()


class AppContext(ApplicationContext):

    def run(self):
        version = self.build_settings['version']
        app = QtWidgets.QApplication(sys.argv)
        app.setOrganizationDomain('marmara.io')
        ui = MarmaraMain()
        ui.show()
        return self.app.exec_()


if __name__ == '__main__':
    appcontext = AppContext()
    exit_code = appcontext.run()
    sys.exit(exit_code)
