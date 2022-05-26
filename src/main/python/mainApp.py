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
from PyQt5 import QtWidgets, QtCore, QtChart
from PyQt5.QtGui import QIcon, QRegExpValidator, QFont, QPainter, QFontDatabase
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtCore import QThread, pyqtSlot, QDateTime, QSize, Qt, QTranslator, QRegExp
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTableWidgetItem, QMessageBox, QDesktopWidget, QHeaderView, \
    QDialog, QDialogButtonBox, QVBoxLayout, QGridLayout, QToolTip, QHBoxLayout, QFileDialog
import configuration
import marmarachain_rpc
import api_request
import remote_connection
import chain_args as cp
import qtguistyle
from Loading import LoadingScreen
import qtawesome as qta
from fbs_runtime.application_context.PyQt5 import ApplicationContext

logging.getLogger(__name__)


class MarmaraMain(QMainWindow, qtguistyle.GuiStyle):

    def __init__(self, parent=None):
        super(MarmaraMain, self).__init__(parent)
        #   Default Settings
        self.trans = QTranslator(self)
        self.retranslateUi(self)
        self.default_fontsize = 12
        self.get_default_fontsize()
        self.set_font_size(self.default_fontsize)
        self.main_tab.setCurrentIndex(0)
        self.main_tab.tabBar().setVisible(False)
        self.login_stackedWidget.setCurrentIndex(0)
        self.home_button.setVisible(False)
        self.chain_status = False
        self.chain_synced = False
        self.pubkey_status = False
        self.center_ui()
        self.selected_stylesheet = ""
        self.get_initial_style_settings()
        self.read_lang_setting()
        self.set_tooltip_texts()
        self.get_balance_hide()
        # paths settings
        # Menu Actions
        self.actionAbout.triggered.connect(self.show_about)
        self.actionLogout.triggered.connect(self.logout_host)
        self.actionLanguage_Selection.triggered.connect(self.show_languages)
        self.actionConsole.setVisible(False)
        self.actionConsole.triggered.connect(self.open_debug_console)
        self.actionSee_Log_File.triggered.connect(self.open_log_file)
        self.actionSee_chain_Log_File.triggered.connect(self.open_chain_log_file)
        self.actionCheck_for_Update.triggered.connect(self.check_app_version)
        self.actionAppearances.triggered.connect(self.show_style_themes)
        #   Login page Host Selection
        self.local_button.clicked.connect(self.local_selection)
        self.remote_button.clicked.connect(self.remote_selection)
        #   Login page Server authentication
        self.home_button.clicked.connect(self.host_selection)
        self.serveradd_button.clicked.connect(self.server_add_selected)
        self.connect_button.clicked.connect(self.server_connect)
        self.serverpw_lineEdit.returnPressed.connect(self.server_connect)
        self.serveredit_button.clicked.connect(self.server_edit_selected)
        self.regex = QRegExp("[1-90_]{1,5}")
        self.validator = QRegExpValidator(self.regex)
        self.ssh_port_lineEdit.setValidator(self.validator)
        self.ssh_port_lineEdit.setText('22')
        self.ssh_port_checkBox.clicked.connect(self.enable_ssh_custom_port)
        # install page
        self.start_install_button.clicked.connect(self.start_autoinstall)
        self.sudo_password_lineEdit.returnPressed.connect(self.start_autoinstall)
        ##  Add Server Settings page
        self.add_serversave_button.clicked.connect(self.save_server_settings)
        self.servercancel_button.clicked.connect(self.add_cancel_selected)
        ## Edit Server Settings page
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
        # self.regex = QRegExp("[1-90_]{1,4}")
        # self.validator = QRegExpValidator(self.regex)
        self.cpu_core_lineEdit.setValidator(self.validator)
        self.cpu_core_selection_off()
        self.cpu_core_set_button.clicked.connect(self.setmining_cpu_core)
        self.mining_button.clicked.connect(self.toggle_mining)
        self.getinfo_refresh_button.clicked.connect(self.refresh_side_panel)
        self.walletsummary_hide_button.clicked.connect(self.toggle_walletsummary)
        self.cup_lineEdit.setValidator(self.validator)
        self.cup_lineEdit.textChanged.connect(self.calculate_amount)
        self.cup_lineEdit.returnPressed.connect(self.send_coins_to_team)
        self.support_pushButton.clicked.connect(self.send_coins_to_team)
        self.fontsize_plus_button.clicked.connect(self.increase_fontsize)
        self.fontsize_minus_button.clicked.connect(self.decrease_fontsize)
        self.discord_button.clicked.connect(self.open_discord)
        self.youtube_button.clicked.connect(self.open_youtube)
        self.website_button.clicked.connect(self.open_website)
        # Chain page
        self.stopchain_button.clicked.connect(self.stop_chain)
        self.addaddress_page_button.clicked.connect(self.get_address_page)
        self.addresses_tableWidget.cellClicked.connect(self.addresstable_itemcontext)
        self.privkey_page_button.clicked.connect(self.see_privkey_page)
        self.hide_address_checkBox.clicked.connect(self.hide_addresses)
        self.download_blocks_button.clicked.connect(self.download_blocks)
        self.refresh_walletaddresses_button.clicked.connect(self.getaddresses)
        self.check_fork_button.clicked.connect(self.check_fork)
        self.check_fork_button.setHidden(True)
        self.update_chain_button.clicked.connect(self.update_chain_latest)
        self.latest_chain_version = None
        self.chain_versiyon_tag = None
        self.update_chain_textBrowser.setVisible(False)
        self.debug_button.clicked.connect(self.toggle_textbrowser)
        self.rescan_checkBox.setVisible(False)
        self.reindex_checkBox.setVisible(False)
        self.startchain_button.setVisible(False)
        self.startchain_button.clicked.connect(self.start_chain_settings)
        # - add address page ----
        self.newaddress_button.clicked.connect(self.get_new_address)
        self.address_seed_button.clicked.connect(self.convertpassphrase)
        self.addresspage_back_button.clicked.connect(self.back_chain_widget_index)
        self.new_address_frame.setEnabled(False)
        self.add_with_seed_radiobutton.clicked.connect(self.change_address_frame_visibility)
        self.add_without_seed_radiobutton.clicked.connect(self.change_address_frame_visibility)
        # - private key page ----
        self.importprivkey_button.clicked.connect(self.importprivkey)
        self.privatekeypage_back_button.clicked.connect(self.back_chain_widget_index)
        # Wallet page
        self.myCCActivatedAddress = None
        self.addressamount_refresh_button.clicked.connect(self.get_address_amounts)
        self.lock_button.clicked.connect(self.marmaralock_amount)
        self.unlock_button.clicked.connect(self.marmaraunlock_amount)
        self.refresh_loopinfo_button.setVisible(False)
        self.refresh_loopinfo_button.clicked.connect(self.get_wallet_loopinfo)
        # Coin send-receive page
        self.contacts_address_comboBox.currentTextChanged.connect(self.get_selected_contact_address)
        self.qrcode_button.clicked.connect(self.create_currentaddress_qrcode)
        self.coinsend_button.clicked.connect(self.sendtoaddress)
        self.transactions_startdate_dateTimeEdit.setMinimumDateTime(QDateTime(datetime.fromtimestamp(1579278200)))
        self.transactions_startdate_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.transactions_startdate_dateTimeEdit.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.transactions_endtdate_dateTimeEdit.setMinimumDateTime(QDateTime(datetime.fromtimestamp(1579278200)))
        self.transactions_endtdate_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.transaction_search_button.clicked.connect(self.getaddresstxids)
        self.transactions_tableWidget.cellClicked.connect(self.transaction_itemcontext)
        # Credit Loops page-----------------
        self.creditloop_tabWidget.currentChanged.connect(self.credit_tab_changed)
        # ---- Received Loop Requests page ----
        self.looprequest_search_button.clicked.connect(self.search_marmarareceivelist)
        self.request_date_checkBox.clicked.connect(self.set_request_date_state)
        self.request_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.contactpk_otherpk_looprequest_comboBox.currentTextChanged.connect(self.get_selected_contact_pukey)
        # -----Make credit Loop Request
        self.contactpk_makeloop_comboBox.currentTextChanged.connect(self.get_selected_contact_loop_pubkey)
        self.contactpk_transferrequest_comboBox.currentTextChanged.connect(self.get_selected_contact_transfer_pubkey)
        self.make_credit_loop_matures_dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())
        self.send_loop_request_button.clicked.connect(self.marmarareceive)
        self.send_transfer_request_button.clicked.connect(self.marmararecieve_transfer)
        self.looprequest_otherpk_radioButton.clicked.connect(self.change_visibilty_looprequestpubkey)
        self.looprequest_currentpk_radioButton.clicked.connect(self.change_visibilty_looprequestpubkey)
        self.change_visibilty_looprequestpubkey()
        # -----Total Credit Loops page -----
        self.activeloops_search_button.clicked.connect(self.search_active_loops)
        self.holderloops_search_button.clicked.connect(self.marmaraholderloops)
        self.activeloops_tableWidget.cellClicked.connect(self.activeloop_itemcontext)
        self.transferableloops_tableWidget.cellClicked.connect(self.transferableloops_itemcontext)
        # ---- Loop Queries page --
        self.lq_pubkey_search_button.clicked.connect(self.search_any_pubkey_loops)
        self.lq_txid_search_button.clicked.connect(self.search_loop_txid)

        # Contacts Page
        self.addcontact_button.clicked.connect(self.add_contact)
        self.updatecontact_button.clicked.connect(self.update_contact)
        self.deletecontact_button.clicked.connect(self.delete_contact)
        self.contacts_tableWidget.cellClicked.connect(self.get_contact_info)
        self.clear_contact_button.clicked.connect(self.clear_contacts_line_edit)
        self.contacts_tableWidget.horizontalHeader().sectionClicked.connect(self.clear_contacts_line_edit)
        self.contact_editing_row = ""
        # Stats Page
        self.stats_refresh_pushButton.clicked.connect(self.get_marmara_stats)
        self.stats_calculate_pushButton.setEnabled(False)
        self.stats_amount_in_activated_lineEdit.setEnabled(False)
        self.stats_amount_in_loops_lineEdit.setEnabled(False)
        self.stats_calculate_pushButton.clicked.connect(self.calculate_estimated_stake)
        self.earning_stop_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.earning_stop_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.earning_start_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.earning_start_dateTimeEdit.setDateTime(QDateTime.currentDateTime().addDays(-1))
        self.earnings_search_button.clicked.connect(self.get_wallet_earnings)
        self.export_earning_table_button.clicked.connect(self.pay_for_export)
        # Market Page
        self.exchange_market_request_button.clicked.connect(self.get_mcl_exchange_market)
        self.mcl_amount_lineEdit.textEdited.connect(self.calculate_usd_price)
        self.usd_amount_lineEdit.textEdited.connect(self.calculate_mcl_price)
        self.mcl_exchange_market_result = None
        self.mcl_exchange_ticker_result = None
        self.market_fiat_comboBox.addItems(['USD', 'TRY', 'BTC', 'EUR', 'RUB'])
        self.market_fiat_comboBox.currentTextChanged.connect(self.market_fiat_changed)

        # Thread setup
        self.thread_marmarad_path = QThread()
        self.thread_autoinstall = QThread()
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
        self.thread_marmaralock = QThread()
        self.thread_marmaraunlock = QThread()
        self.thread_sendrawtransaction = QThread()
        self.thread_marmarareceivelist = QThread()
        self.thread_sendtoaddress = QThread()
        self.thread_marmaracreditloop = QThread()
        self.thread_marmarareceive = QThread()
        self.thread_setgenerate = QThread()
        self.thread_sidepanel = QThread()
        self.thread_marmarareceive_transfer = QThread()
        self.thread_marmarainfo = QThread()
        self.thread_getloops = QThread()
        self.thread_marmaraissue = QThread()
        self.thread_marmaratransfer = QThread()
        self.thread_getaddresstxids = QThread()
        self.thread_sendtoteam = QThread()
        self.thread_get_address_amounts = QThread()
        self.thread_extract_bootstrap = QThread()
        self.thread_api_exchange_request = QThread()
        self.thread_api_stats_request = QThread()
        self.thread_marmarholderloop = QThread()
        self.thread_getblock = QThread()
        self.thread_api_chain_update_check = QThread()
        self.thread_chain_update = QThread()
        self.thread_fetch_params = QThread()
        self.thread_earnings = QThread()
        self.thread_api_app_ver = QThread()

        # Loading Gif
        # --------------------------------------------------
        self.loading = LoadingScreen()
        # --------------------------------------------------
        # Check for update
        self.check_app_version()
        # ---------------------------------------------------

    def set_tooltip_texts(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.copyaddress_button.setToolTip(self.tr("Copy address"))
        self.copypubkey_button.setToolTip(self.tr("Copy pubkey"))
        self.support_pushButton.setToolTip(self.tr("Gift Marmara Core Team cups of coffee"))
        self.download_blocks_button.setToolTip(self.tr("Download Blocks bootstrap"))
        self.stats_refresh_pushButton.setToolTip(self.tr("can be refreshed once in a minute"))
        self.exchange_market_request_button.setToolTip(self.tr("can be refreshed once in 20 seconds"))
        self.fontsize_plus_button.setToolTip(self.tr("Increase font size"))
        self.fontsize_minus_button.setToolTip(self.tr("Decrease font size"))
        self.youtube_button.setToolTip('Youtube MARMARA')
        self.discord_button.setToolTip('Discord MARMARA')
        self.website_button.setToolTip("marmara.io")
        self.debug_button.setToolTip('Debug')
        self.export_earning_table_button.setToolTip(self.tr('Export to CSV'))
        self.reindex_checkBox.setToolTip(self.tr('starts from beginning and re-indexes currently '
                                                 'synced blockchain data'))
        self.rescan_checkBox.setToolTip(self.tr('starts scanning wallet data in blockchain data'))
        self.walletsummary_hide_button.setToolTip(self.tr('Hide'))
        self.connections_warning_label.setToolTip(self.tr('Check your Network Connection'))

    def center_ui(self):
        qr = self.frameGeometry()
        top_point = QDesktopWidget().availableGeometry().top()
        center_point = QDesktopWidget().availableGeometry().center().x()
        qr.moveTopLeft(QtCore.QPoint(center_point - (qr.width() / 2), top_point))
        self.move(qr.topLeft())

    def get_default_fontsize(self):
        fontsize_conf = configuration.ApplicationConfig().get_value('USER', 'fontsize')
        if fontsize_conf:
            self.default_fontsize = int(fontsize_conf)

    def get_balance_hide(self):
        if configuration.ApplicationConfig().get_value('USER', 'balance_hide') == 'True':
            self.toggle_walletsummary()

    def get_initial_style_settings(self):
        style_conf = configuration.ApplicationConfig().get_value('USER', 'style')
        if style_conf:
            self.set_stylesheet(style_conf)
        else:
            self.set_icon_color('black')

    @pyqtSlot()
    def show_style_themes(self):
        font = QFont()
        font.setPointSize(self.default_fontsize)
        themeDialog = QDialog(self)
        themeDialog.setWindowTitle(self.tr("Choose a style"))
        themeDialog.setFont(font)
        themeDialog.setMinimumSize(255, 100)
        apply_button = QDialogButtonBox(QDialogButtonBox.Apply)
        apply_button.setFont(font)
        self.style_comboBox = QtWidgets.QComboBox()
        self.style_comboBox.setFont(font)

        themeDialog.layout = QVBoxLayout()
        themeDialog.layout.addWidget(self.style_comboBox)
        themeDialog.layout.addWidget(apply_button)
        themeDialog.setLayout(themeDialog.layout)

        entries = os.listdir(qtguistyle.style_path)
        entries.sort()
        for item in entries:
            self.style_comboBox.addItem(item.strip('.qss'))
        self.style_comboBox.addItem('light')
        apply_button.clicked.connect(self.get_theme_selection)
        apply_button.clicked.connect(themeDialog.close)
        themeDialog.exec_()

    @pyqtSlot()
    def get_theme_selection(self):
        data = self.style_comboBox.currentText()
        if data:
            configuration.ApplicationConfig().set_key_value('USER', 'style', data)
            self.set_stylesheet(data)

    def set_stylesheet(self, data):
        if data == 'light':
            self.selected_stylesheet = ""
            self.set_icon_color('black')
        else:
            self.selected_stylesheet = self.get_style(data + '.qss')
            self.set_icon_color('#eff0f1')
        self.setStyleSheet(self.selected_stylesheet)
        self.set_font_size(self.default_fontsize)

    @pyqtSlot()
    def check_app_version(self):
        self.worker_api_app_ver = marmarachain_rpc.ApiWorker()
        self.worker_api_app_ver.moveToThread(self.thread_api_app_ver)
        self.worker_api_app_ver.finished.connect(self.thread_api_app_ver.quit)
        self.thread_api_app_ver.started.connect(self.worker_api_app_ver.app_ver_check)
        self.thread_api_app_ver.start()
        self.worker_api_app_ver.out_list.connect(self.check_app_version_listout)
        self.worker_api_app_ver.out_err.connect(self.check_app_version_errtout)

    @pyqtSlot(list)
    def check_app_version_listout(self, out):
        latest_app_tag = out[0]
        latest_app_version = out[1]
        base_version = configuration.version
        if base_version != latest_app_tag:
            QMessageBox.information(self, self.tr('Software Update Available'),
                                    self.tr('A new update is available. <br>Follow the link ')
                                    + "<a href='" + latest_app_version + "'>" + self.tr("here") + '</a>')
        else:
            self.bottom_info(self.tr('No Update Available Current App version is ') + base_version)

    @pyqtSlot(str)
    def check_app_version_errtout(self, out):
        if out == 'Connection Error':
            self.custom_message(self.tr('Connection Error'), self.tr('Check your internet Connection '), 'information',
                                QMessageBox.Information)

    def read_lang_setting(self):
        language = configuration.ApplicationConfig().get_value('USER', 'lang')
        if language:
            entries = os.listdir(configuration.configuration_path + '/language')
            for item in entries:
                if item.strip('.qm') == language:
                    self.change_lang(language)

    @pyqtSlot()
    def show_languages(self):
        font = QFont()
        font.setPointSize(self.default_fontsize)
        languageDialog = QDialog(self)
        languageDialog.setMinimumSize(300, 100)
        languageDialog.setWindowTitle(self.tr("Choose a language"))
        languageDialog.setFont(font)
        apply_button = QDialogButtonBox(QDialogButtonBox.Apply)
        apply_button.setFont(font)
        self.lang_comboBox = QtWidgets.QComboBox()
        self.lang_comboBox.setFont(font)

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

    @pyqtSlot()
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
        font = QFont()
        font.setPointSize(self.default_fontsize)
        messagebox = QMessageBox()
        messagebox.setStyleSheet(self.selected_stylesheet)
        messagebox.setWindowTitle(title)
        messagebox.setText(content)
        messagebox.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        messagebox.setDetailedText(detailed_text)
        messagebox.setFont(font)
        btn_yes = None
        btn_no = None
        btn_ok = None

        if message_type == "information":
            if icon:
                messagebox.setIcon(icon)
            messagebox.setStandardButtons(QMessageBox.Ok)
            btn_ok = messagebox.button(QMessageBox.Ok)
            btn_ok.setText(self.tr("Ok"))
            btn_ok.setFont(font)
        if message_type == "question":
            if icon:
                messagebox.setIcon(icon)
            messagebox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            btn_yes = messagebox.button(QMessageBox.Yes)
            btn_yes.setText(self.tr("Yes"))
            btn_yes.setFont(font)
            btn_no = messagebox.button(QMessageBox.No)
            btn_no.setText(self.tr("No"))
            btn_no.setFont(font)
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
        self.chain_synced = False
        self.host_name_label.clear()

    def logout_host(self):
        self.current_pubkey_value.clear()
        self.currentaddress_value.clear()
        self.pubkey_status = False
        self.myCCActivatedAddress = None
        self.addresses_tableWidget.setRowCount(0)
        self.addresses_privkey_tableWidget.setRowCount(0)
        self.transactions_tableWidget.setRowCount(0)
        self.loop_request_tableWidget.setRowCount(0)
        self.transferrequests_tableWidget.setRowCount(0)
        self.activeloops_tableWidget.setRowCount(0)
        self.transferableloops_tableWidget.setRowCount(0)
        self.earning_stats_tableWidget.setRowCount(0)
        self.chain_version_label.clear()
        self.latest_chain_version = None
        self.chain_versiyon_tag = None
        self.clear_amount_values()
        self.host_selection()

    def clear_amount_values(self):
        self.normal_amount_value.clear()
        self.activated_amount_value.clear()
        self.wallet_total_normal_value.clear()
        self.wallet_total_activated_value.clear()
        self.totalnormal_value_label.clear()
        self.totalactivated_value_label.clear()
        self.total_issuer_loop_amount_label_value.clear()
        self.activeloops_pending_number_value_label.clear()
        self.closedloops_total_amount_value_label.clear()
        self.closedloops_total_number_value_label.clear()
        self.activeloops_total_amount_value_label.clear()
        self.numberof_total_activeloops_label_value.clear()
        self.my_stats_normal_label_value.clear()
        self.my_stats_activated_label_value.clear()
        self.my_stats_inloops_label_value.clear()
        self.total_transferrable_loop_amount_label_value.clear()
        self.numberof_transferrable_loop_amount_label_value.clear()
        self.holderloops_closed_amount_label_value.clear()
        self.holderloops_closed_number_label_value.clear()
        self.activated_earning_value.clear()
        self.normal_earning_value.clear()
        self.total_earning_value.clear()

    def local_selection(self):
        marmarachain_rpc.set_connection_local()
        logging.info('is local connection: ' + str(marmarachain_rpc.is_local))
        self.check_marmara_path()
        self.download_blocks_button.show()
        self.host_name_label.setText(self.tr('LOCAL'))

    def remote_selection(self):
        self.login_stackedWidget.setCurrentIndex(1)
        self.get_server_combobox_names()
        self.home_button.setVisible(True)
        marmarachain_rpc.set_connection_remote()
        marmarachain_rpc.set_sshclient(None)
        logging.info('is local connection: ' + str(marmarachain_rpc.is_local))
        self.serverpw_lineEdit.clear()
        self.download_blocks_button.hide()
        if self.server_comboBox.count() != 0:
            self.serveredit_button.setEnabled(True)
            self.connect_button.setEnabled(True)
        else:
            self.connect_button.setEnabled(False)
            self.serveredit_button.setEnabled(False)

    @pyqtSlot()
    def server_connect(self):
        server_list = configuration.ServerSettings().read_file()
        selected_server_info = server_list[self.server_comboBox.currentIndex()]
        selected_server_info = selected_server_info.split(",")
        if not self.ssh_port_lineEdit.text():
            self.ssh_port_lineEdit.setText('22')
        remote_connection.set_server_connection(ip=selected_server_info[2], username=selected_server_info[1],
                                                pw=self.serverpw_lineEdit.text(),
                                                ssh_port=self.ssh_port_lineEdit.text())
        validate = remote_connection.check_server_connection()
        if validate == 'error':
            self.login_page_info(self.tr("Authentication or Connection Error"))
        else:
            self.check_marmara_path()
            marmarachain_rpc.set_sshclient(validate)
            self.host_name_label.setText(self.tr('Remote: ') + self.server_comboBox.currentText())

    @pyqtSlot()
    def open_debug_console(self):
        QMessageBox.information(self,
                                self.tr("Debug Console"),
                                self.tr("Under development"))

    @pyqtSlot()
    def open_log_file(self):
        text_path = configuration.log_file_path
        webbrowser.open_new(text_path)

    @pyqtSlot()
    def open_chain_log_file(self):
        operating_system = platform.system()
        debug_log_path = ''
        if operating_system == 'Darwin':
            debug_log_path = os.environ['HOME'] + '/Library/Application Support/Komodo/MCL'
        elif operating_system == 'Linux':
            debug_log_path = os.environ['HOME'] + '/.komodo/MCL'
        elif operating_system == 'Win64' or operating_system == 'Windows':
            debug_log_path = '%s/komodo/MCL' % os.environ['APPDATA']
        debug_log_file = str(debug_log_path + '/' + 'debug.log')
        webbrowser.open_new(debug_log_file)

    @pyqtSlot(int)
    def mcl_tab_changed(self, index):
        if index == 4:
            self.update_contact_tablewidget()
        if index == 2:
            self.get_contact_names_addresses()
        if index == 3:
            self.creditloop_tabWidget.setCurrentIndex(0)
        if index == 6:
            self.update_exchange_market_combobox()

    @pyqtSlot(int)
    def credit_tab_changed(self, index):
        if index == 1:
            self.get_contact_names_pubkeys()

    def worker_thread(self, thread, worker, method=None, params=None, worker_output=None, execute=None):
        if self.chain_status:
            self.start_animation()
            if method:
                worker.set_method(method)
            if params:
                worker.set_params(params)
            worker.moveToThread(thread)
            worker.finished.connect(thread.quit)
            worker.finished.connect(self.stop_animation)
            if execute is None:
                thread.started.connect(worker.do_execute_rpc)
            if execute == 'refresh_sidepanel':
                thread.started.connect(worker.refresh_sidepanel)
            if execute == 'get_addresses':
                thread.started.connect(worker.get_addresses)
                worker.walletlist_out.connect(worker_output)
            if execute == 'setgenerate':
                thread.started.connect(worker.setgenerate)
            if execute == 'get_balances':
                thread.started.connect(worker.get_balances)
            if execute == 'txids_detail':
                thread.started.connect(worker.txids_detail)
            if execute == 'active_loops_details':
                thread.started.connect(worker.active_loops_details)
            if execute == 'holder_loop_detail':
                thread.started.connect(worker.holder_loop_detail)
            if execute == 'check_fork_api':
                thread.started.connect(worker.check_fork_api)
            if execute == 'wallet_earnings':
                thread.started.connect(worker.calc_wallet_earnings)
                worker.output.connect(self.earnings_output_info)
            thread.start(priority=4)
            if worker_output and execute != 'get_addresses':
                worker.command_out.connect(worker_output)
            return worker
        else:
            logging.info("Marmarachain is not started")
            self.bottom_info(self.tr("Marmarachain is not started"))

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
        if output == 'get marmarad path':
            self.login_page_info(self.tr('Getting marmara chain path from config file'))
            logging.info('Getting marmara chain path from config file')
        if str(output).split('=')[0] == 'marmarad_path':
            self.login_page_info(self.tr('marmara path from configuration file = ') + str(output).split('=')[1])
            logging.info('marmara path from configuration file = ' + str(output).split('=')[1])
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
                                              "question", QMessageBox.Question)
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

    @pyqtSlot(str)
    def bottom_info(self, info):
        self.bottom_message_label.setText(info)

    def bottom_err_info(self, err_msg):
        try:
            result = json.loads(err_msg)
            self.bottom_info(result['message'])
            logging.error(result['message'])
        except Exception:
            result = str(err_msg).splitlines()
            if str(err_msg).find('error message:') != -1:
                index = result.index('error message:') + 1
                self.bottom_info(result[index])
                logging.error(result[index])
            else:
                err_result = ""
                for line in str(err_msg).splitlines():
                    err_result = err_result + ' ' + str(line)
                logging.error(err_result)
                self.bottom_info(err_result)
                if str(err_msg) == "(7, 'Failed to connect to 127.0.0.1 port 33825: Connection refused')" or \
                        str(err_msg).find("error: couldn't connect to server: unknown (code -1)") != -1:
                    if self.chain_status:
                        self.custom_message(self.tr('Chain is not Working'),
                                            self.tr('Make sure the marmara chain is running!'), 'information',
                                            QMessageBox.Warning)
                        self.chain_status = False
                        self.chainstatus_label_value.setPixmap(self.inactive_icon_pixmap)

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
        self.check_chain_update()
        logging.info('chain_status ' + str(self.chain_status))
        self.bottom_info(self.tr('chain_status ' + str(self.chain_status)))
        time.sleep(0.1)
        zcash_status = marmarachain_rpc.check_zcashparams()
        if zcash_status[0] == 0:
            if not self.chain_status:
                logging.info('Checking marmarachain')
                self.bottom_info(self.tr('Checking marmarachain'))
                marmara_pid = marmarachain_rpc.mcl_chain_status()
                if len(marmara_pid[0]) > 0:
                    self.bottom_info(self.tr('marmarachain has pid'))
                    logging.info('marmarachain has pid')
                    self.is_chain_ready()
                if len(marmara_pid[0]) == 0:
                    logging.info('marmarachain is not running')
                    self.bottom_info(self.tr('marmarachain is not running'))
                    self.enable_start_button()

        if zcash_status[0] == 1:
            message_content = ""
            corrupted_files = ""
            if type(zcash_status[1]) is str:
                message_content = self.tr('ZcashParams folder missing')
            else:
                if len(zcash_status[1]) > 0:
                    for item in zcash_status[1]:
                        corrupted_files = corrupted_files + item.strip('/') + ' '
                    message_content = message_content + self.tr(' incomplete files: ') + corrupted_files + '\n'
                if len(zcash_status[2]) > 0:
                    missing_files = ""
                    for item in zcash_status[2]:
                        missing_files = missing_files + item.strip('/') + ', '
                    message_content = message_content + self.tr(' missing files: ') + missing_files
            message_box = self.custom_message('Incomplete ZcashParams',
                                              message_content + "\n" + self.tr(' Do you want to install'),
                                              'question', QMessageBox.Warning)
            if message_box == QMessageBox.Yes:
                self.run_fetch_params(zcash_status[1])
            if message_box == QMessageBox.No:  # Abort
                self.logout_host()

    def run_fetch_params(self, zc_file=None):
        self.start_animation()
        self.worker_fetch_params = marmarachain_rpc.Autoinstall()
        if zc_file:
            self.worker_fetch_params.set_input_list(zc_file)
        self.worker_fetch_params.moveToThread(self.thread_fetch_params)
        self.worker_fetch_params.finished.connect(self.thread_fetch_params.quit)
        self.worker_fetch_params.finished.connect(self.stop_animation)
        self.worker_fetch_params.finished.connect(self.fetch_params_install_finished)
        self.thread_fetch_params.started.connect(self.worker_fetch_params.fetch_params_install)
        self.thread_fetch_params.start()
        self.update_chain_textBrowser.setVisible(True)
        self.worker_fetch_params.out_text.connect(self.fetch_params_install_result)

    def fetch_params_install_result(self, output):
        self.update_chain_textBrowser.append(output)

    def fetch_params_install_finished(self):
        message_box = self.custom_message(self.tr('ZcashParams Finished'), self.tr('Starting Chain'), 'information')
        if message_box == QMessageBox.Ok:
            self.chain_init()

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
            self.check_fork_button.setHidden(False)
            self.chainstatus_label_value.setPixmap(self.active_icon_pixmap)
            if result.get('version'):
                self.set_getinfo_result(result)
                self.bottom_info(self.tr('getting wallet addresses'))
                logging.info('getting wallet addresses')
            elif result.get('WalletActivatedAddresses') or result.get('WalletActivatedAddresses') == []:
                TotalAmountOnActivated = 0.0
                for activated in result.get('WalletActivatedAddresses'):
                    TotalAmountOnActivated = TotalAmountOnActivated + activated.get('amount')
                self.totalactivated_value_label.setText(str(TotalAmountOnActivated))
                self.wallet_total_activated_value.setText(str(TotalAmountOnActivated))
            else:
                self.setgenerate_result(result_out)
                self.bottom_info(self.tr('Chain init completed.'))
                logging.info('Chain init completed.')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def enable_start_button(self):
        self.startchain_button.setVisible(True)
        self.stopchain_button.setVisible(False)

    def disable_start_button(self):
        self.startchain_button.setVisible(False)
        self.stopchain_button.setVisible(True)

    def check_chain_update(self):
        self.update_chain_button.setHidden(True)
        self.worker_api_chain_update = marmarachain_rpc.ApiWorker()
        self.worker_api_chain_update.moveToThread(self.thread_api_chain_update_check)
        self.worker_api_chain_update.finished.connect(self.thread_api_chain_update_check.quit)
        self.thread_api_chain_update_check.started.connect(self.worker_api_chain_update.mcl_update_check)
        self.thread_api_chain_update_check.start()
        self.worker_api_chain_update.out_str.connect(self.check_installed_mcl_version)
        self.worker_api_chain_update.out_err.connect(self.check_chain_update_err)

    @pyqtSlot(str)
    def check_installed_mcl_version(self, out):
        self.latest_chain_version = out
        if marmarachain_rpc.marmara_path:
            installed_chain_versiyon = self.get_installed_chain_version()
            if out == installed_chain_versiyon:
                self.update_chain_button.setHidden(True)
            else:
                self.update_chain_button.setHidden(False)
        else:
            self.update_chain_button.setHidden(False)

    def get_installed_chain_version(self):
        if marmarachain_rpc.is_local:
            file = None
            try:
                file = open(marmarachain_rpc.marmara_path + 'version.info', "r")
                self.chain_versiyon_tag = file.read().rstrip()
                self.chain_version_label.setText('Marmara Chain ' + self.chain_versiyon_tag)
                return self.chain_versiyon_tag
            except IOError as error:
                logging.error("Exception error while reading mcl version info file: " + str(error))
                self.update_chain_button.setHidden(False)
            finally:
                if file:
                    file.close()
        else:
            remote_file = None
            try:
                sftp_client = marmarachain_rpc.ssh_client.open_sftp()
                remote_file = sftp_client.open(marmarachain_rpc.marmara_path + 'version.info', "r")
                self.chain_versiyon_tag = remote_file.read().rstrip().decode()
                self.chain_version_label.setText('Marmara Chain ' + self.chain_versiyon_tag)
                return self.chain_versiyon_tag
            except Exception as error:
                logging.error("Exception error while reading mcl version info file: " + str(error))
                self.update_chain_button.setHidden(False)
            finally:
                if remote_file:
                    remote_file.close()

    @pyqtSlot(str)
    def check_chain_update_err(self, err):
        self.bottom_info(err)
        self.update_chain_button.setHidden(False)
        logging.error(err)

    # --------------------------------------
    # Stopping Chain
    # --------------------------------------
    @pyqtSlot()
    def stop_chain(self):
        if self.chain_status:
            self.start_animation()
            stop_chain_thread = self.stop_chain_thread()
            stop_chain_thread.finished.connect(self.stop_animation)  # when finished close animation
        else:
            self.bottom_info(self.tr('Marmarachain is not started'))
            logging.warning('Marmarachain is not started')

    def stop_chain_thread(self):
        self.worker_stopchain = marmarachain_rpc.RpcHandler()  # worker setting
        self.worker_stopchain.moveToThread(self.thread_stopchain)  # putting in to thread
        self.worker_stopchain.finished.connect(self.thread_stopchain.quit)  # when finished close thread
        self.thread_stopchain.started.connect(self.worker_stopchain.stopping_chain)  # executing worker function
        self.thread_stopchain.start()
        self.worker_stopchain.command_out.connect(self.result_stopchain)
        return self.worker_stopchain

    @pyqtSlot(tuple)
    def result_stopchain(self, result_out):
        if result_out[2] != 1:
            if result_out[0]:
                print_result = ""
                for line in str(result_out[0]).splitlines():
                    print_result = print_result + ' ' + str(line)
                logging.info("Stopping chain:" + print_result)
                self.bottom_info(print_result)

            if result_out[0] == 0:
                self.bottom_info(self.tr('Marmarachain stopped'))
                logging.info('Marmarachain stopped')
                self.chain_status = False
                self.myCCActivatedAddress = None
                self.chainstatus_label_value.setPixmap(self.inactive_icon_pixmap)
                self.update_addresses_table()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # -------------------------------------------------------
    # Getting getinfo command
    # -------------------------------------------------------
    @pyqtSlot()
    def get_getinfo(self):
        self.worker_getinfo = marmarachain_rpc.RpcHandler()  # worker setting
        method = cp.getinfo  # setting command
        params = []
        self.worker_thread(self.thread_getinfo, self.worker_getinfo, method, params, self.getinfo_result)

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

    def set_getinfo_result(self, getinfo_result):
        if getinfo_result.get('synced'):
            self.chainsync_label_value.setPixmap(self.active_icon_pixmap)
            self.chainsync_label_value.setAlignment(QtCore.Qt.AlignCenter)
            self.chain_synced = True
        if not getinfo_result.get('synced'):
            self.chain_synced = False
            if int(getinfo_result['longestchain']) == 0:
                self.chainsync_label_value.setAlignment(QtCore.Qt.AlignCenter)
                self.chainsync_label_value.setPixmap(self.inactive_icon_pixmap)
            else:
                block_diff = int(getinfo_result['longestchain']) - int(getinfo_result['blocks'])
                days_sync = None
                if 0 < block_diff < 61:
                    days_sync = str(block_diff) + self.tr(' Min')
                if 60 < block_diff < 1140:
                    days_sync = str(round(block_diff / 60)) + self.tr(' Hour')
                if block_diff > 1140:
                    days_sync = str(round(block_diff / 1440)) + self.tr(' Day')
                if block_diff == 0:
                    days_sync = None
                    self.chainsync_label_value.setAlignment(QtCore.Qt.AlignCenter)
                    self.chainsync_label_value.setPixmap(self.inactive_icon_pixmap)
                if block_diff:
                    self.chainsync_label_value.setAlignment(QtCore.Qt.AlignLeft)
                    self.chainsync_label_value.setText(days_sync)
        if getinfo_result.get('pubkey'):
            self.pubkey_status = True
            self.current_pubkey_value.setText(str(getinfo_result['pubkey']))
        if getinfo_result.get('pubkey') is None or getinfo_result.get('pubkey') is "":
            self.bottom_info(self.tr('pubkey is not set'))
            logging.warning('pubkey is not set')
            self.pubkey_status = False
            self.current_pubkey_value.setText("")
        if getinfo_result.get('errors') is "":
            self.update_chain_textBrowser.setVisible(False)
        if getinfo_result.get('errors') is not "":
            self.update_chain_textBrowser.setVisible(True)
            self.update_chain_textBrowser.setText(str(getinfo_result.get('errors')))
        self.difficulty_value_label.setText(str(int(getinfo_result['difficulty'])))
        self.currentblock_value_label.setText(str(getinfo_result['blocks']))
        self.longestchain_value_label.setText(str(getinfo_result['longestchain']))
        connection_count = int(getinfo_result['connections'])
        if connection_count == 0:
            self.connections_warning_label.setVisible(True)
        if connection_count > 0:
            self.connections_warning_label.setVisible(False)
        self.connections_value_label.setText(str(getinfo_result['connections']))
        self.totalnormal_value_label.setText(str(getinfo_result['balance']))
        self.wallet_total_normal_value.setText(str(getinfo_result['balance']))
        self.bottom_info(self.tr('getinfo finished'))
        logging.info('getinfo finished')

    # -----------------------------------------------------------
    # Side panel functions
    # -----------------------------------------------------------
    @pyqtSlot()
    def refresh_side_panel(self):
        self.bottom_info(self.tr('getting getinfo'))
        logging.info('getting getinfo')
        # self.get_getinfo()
        self.worker_sidepanel = marmarachain_rpc.RpcHandler()
        self.worker_thread(self.thread_sidepanel, self.worker_sidepanel, worker_output=self.refresh_side_panel_result,
                           execute='refresh_sidepanel')
        last_update = self.tr('Last Update: ')
        # date = (str(datetime.now().date()))
        last_update_time = str(datetime.now().time().replace(microsecond=0))
        self.last_update_label.setText(last_update + last_update_time)
        self.update_datetime_edit_maxdates()

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
                self.wallet_total_activated_value.setText(str(TotalAmountOnActivated))
                self.bottom_info(self.tr('Refresh completed.'))
                logging.info('Refresh completed.')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def update_datetime_edit_maxdates(self):
        self.transactions_startdate_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.earning_stop_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.earning_start_dateTimeEdit.setMaximumDateTime(QDateTime.currentDateTime())
        self.earning_stop_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.transactions_endtdate_dateTimeEdit.setDateTime(QDateTime.currentDateTime())
        self.make_credit_loop_matures_dateTimeEdit.setMinimumDateTime(QDateTime.currentDateTime())

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
    def decrease_fontsize(self):
        if self.default_fontsize >= 9:
            self.default_fontsize = self.default_fontsize - 1
        self.set_font_size(self.default_fontsize)
        self.bottom_info('fontsize :' + str(self.default_fontsize))

    @pyqtSlot()
    def increase_fontsize(self):
        if self.default_fontsize <= 20:
            self.default_fontsize = self.default_fontsize + 1
        self.set_font_size(self.default_fontsize)
        self.bottom_info('fontsize :' + str(self.default_fontsize))

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
    def open_discord(self):
        webbrowser.open_new('https://marmara.io/discord')

    @pyqtSlot()
    def open_youtube(self):
        webbrowser.open_new('https://www.youtube.com/c/MarmaraCreditLoops')

    @pyqtSlot()
    def open_website(self):
        webbrowser.open_new('https://marmara.io')

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
                    logging.info('setgenerate True 0')
                    self.setgenerate([True, 0])
                if message_box == QMessageBox.No:  # Abort selecting staking and continue mining
                    self.staking_button.setChecked(False)
            else:  # set staking mode
                logging.info('setgenerate True 0')
                self.setgenerate([True, 0])
        else:  # Staking button status is False
            message_box = self.custom_message(self.tr('Turning off Staking'),
                                              self.tr('You are about to turn off staking. Are you sure?'), "question",
                                              QMessageBox.Question)

            if message_box == QMessageBox.Yes:
                logging.info('setgenerate False')
                self.setgenerate([False])
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
                    logging.info('setgenerate True 1')
                    self.setgenerate([True, 1])
                    self.cpu_core_selection_on()
                if message_box == QMessageBox.No:  # Abort selecting mining and continue staking
                    self.mining_button.setChecked(False)
            else:  # Staking is off turn on Mining mode
                logging.info('setgenerate True 1')
                self.cpu_core_selection_on()
                self.setgenerate([True, 1])
        else:  # Mining button status is False.
            message_box = self.custom_message(self.tr('Turning off Mining'),
                                              self.tr('You are about to turn off mining. Are you sure?'), "question",
                                              QMessageBox.Question)
            if message_box == QMessageBox.Yes:
                logging.info('setgenerate False')
                self.cpu_core_selection_off()
                self.setgenerate([False])
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
        self.worker_setgenerate = marmarachain_rpc.RpcHandler()
        method = cp.setgenerate
        params = arg
        self.worker_thread(self.thread_setgenerate, self.worker_setgenerate, method, params, self.setgenerate_result,
                           execute='setgenerate')

    @pyqtSlot(tuple)
    def setgenerate_result(self, result_out):
        if result_out[0]:
            logging.info('\n---- getgenerate result------\n' + str(json.loads(result_out[0])))
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

    @pyqtSlot()
    def setmining_cpu_core(self):
        cpu_no = self.cpu_core_lineEdit.text()
        self.setgenerate([True, int(cpu_no)])

    @pyqtSlot()
    def toggle_walletsummary(self):
        if self.walletsummary_amount_frame.isHidden():
            self.walletsummary_hide_button.setIcon(qta.icon('ei.eye-close', color='#cc2900'))
            self.walletsummary_hide_button.setToolTip(self.tr('Hide'))
            self.walletsummary_amount_frame.setHidden(False)
            configuration.ApplicationConfig().set_key_value('USER', 'balance_hide', 'False')
        else:
            self.walletsummary_hide_button.setIcon(qta.icon('ei.eye-open', color='#cc2900'))
            self.walletsummary_hide_button.setToolTip(self.tr('Show'))
            self.walletsummary_amount_frame.setHidden(True)
            configuration.ApplicationConfig().set_key_value('USER', 'balance_hide', 'True')

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
                                          self.tr(f'The amount to be send to the Marmara Team is ') + str(amount)
                                          + ' MCL',
                                          "question",
                                          QMessageBox.Question)
        if message_box == QMessageBox.Yes:
            self.worker_sendtoteam = marmarachain_rpc.RpcHandler()
            method = cp.sendtoaddress
            params = [team_address, str(amount)]
            self.worker_thread(self.thread_sendtoteam, self.worker_sendtoteam, method, params,
                               self.sendtoaddress_result)
        if message_box == QMessageBox.No:
            self.bottom_info(self.tr('Transaction aborted'))
            logging.info('Transaction aborted')

    # -----------------------------------------------------------
    # Chain page functions
    # -----------------------------------------------------------

    # getting addresses for address table widget
    @pyqtSlot()
    def getaddresses(self):
        if self.chain_status:
            self.bottom_info(self.tr('getting wallet addresses'))
            logging.info('getting wallet addresses')
            self.worker_getaddresses = marmarachain_rpc.RpcHandler()
            self.worker_thread(thread=self.thread_getaddresses, worker=self.worker_getaddresses,
                               worker_output=self.set_getaddresses_result, execute='get_addresses')
        else:
            self.update_addresses_table()

    @pyqtSlot(list)
    def set_getaddresses_result(self, result_out):
        if result_out == []:
            self.bottom_err_info(self.tr('could not get addresses. make sure chain is running'))
        else:
            self.bottom_info(self.tr('Loading Addresses ...'))
            logging.info('Loading Addresses ...')
            self.addresses_tableWidget.setSortingEnabled(False)
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
            self.addresses_tableWidget.setSortingEnabled(True)
            # self.hide_address_checkBox.setCheckState(False)
            self.update_addresses_table()

    @pyqtSlot()
    def hide_addresses(self):
        self.unhide_addresses()
        if self.hide_address_checkBox.checkState():
            rowcount = self.addresses_tableWidget.rowCount()
            while True:
                rowcount = rowcount - 1
                if self.addresses_tableWidget.item(rowcount, 1).text() == "0.0":
                    self.addresses_tableWidget.setRowHidden(rowcount, True)
                if rowcount == 0:
                    break

    def unhide_addresses(self):
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
        if self.addresses_tableWidget.rowCount() > 0:
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
            self.get_known_addresses()

    def check_address_contact_name(self, address):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        known_address = ""
        for contact in contacts_data:  # each contact set in contacts_data
            if contact[1] == address:  # contact[1] contact address
                known_address = contact[0]  # contact[0] contact name
                break
        return known_address

    def get_known_addresses(self):
        rowcount = self.addresses_tableWidget.rowCount()
        self.addresses_tableWidget.setRowCount(rowcount)
        while True:
            rowcount = rowcount - 1
            address = self.addresses_tableWidget.item(rowcount, 2).text()
            known_address = self.check_address_contact_name(address)
            self.addresses_tableWidget.setItem(rowcount, 4, QTableWidgetItem(str(known_address)))
            self.addresses_tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            if rowcount == 0:
                break

    @pyqtSlot()
    def set_pubkey(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        if index.isValid():
            self.worker_setpubkey = marmarachain_rpc.RpcHandler()
            method = cp.setpubkey
            params = [self.addresses_tableWidget.item(index.row(), 3).text()]
            self.worker_thread(self.thread_setpubkey, self.worker_setpubkey, method, params, self.set_pubkey_result)

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

    @pyqtSlot()
    def start_chain_with_pubkey(self):
        button = self.sender()
        index = self.addresses_tableWidget.indexAt(button.pos())
        logging.info(index.row())
        logging.info(index.column())
        if index.isValid():
            pubkey = self.addresses_tableWidget.item(index.row(), 3).text()
            self.start_chain_settings(pubkey)

    def start_chain_settings(self, pubkey=None):
        if pubkey:
            self.bottom_info(self.tr('Chain started with pubkey'))
            logging.info('Chain started with pubkey')
            reindex_param = ''
            rescan_param = ''
            if self.reindex_checkBox.checkState():
                reindex_param = ' -reindex'
            if self.rescan_checkBox.checkState():
                rescan_param = ' -rescan'
            start_param = pubkey + reindex_param + rescan_param
            logging.info(start_param)
            marmarachain_rpc.start_chain(start_param)
            time.sleep(0.5)
            self.addresses_tableWidget.setColumnHidden(0, True)
            self.is_chain_ready()
        else:
            logging.info('sending chain start command')
            self.bottom_info(self.tr('sending chain start command'))
            marmarachain_rpc.start_chain()
            self.disable_start_button()
            self.is_chain_ready()
        # self.is_chain_ready()
        # self.start_pubkey = pubkey
        # font = QFont()
        # font.setPointSize(self.default_fontsize)
        # startchainDialog = QDialog(self)
        # startchainDialog.setWindowTitle(self.tr('Settings for Chain Start'))
        # startchainDialog.layout = QVBoxLayout()
        # startchainDialog.setFont(font)
        # apply_button = QPushButton('Start')
        # apply_button.setIcon(QIcon(self.icon_path + "/start_icon.png"))
        # apply_button.setFont(font)
        # button_layout = QHBoxLayout()
        # self.reindex = QtWidgets.QCheckBox('reindex' + self.tr(' (starts from beginning and re-indexes currently '
        #                                                        'synced blockchain data)'))
        # self.reindex.setChecked(False)
        # self.rescan = QtWidgets.QCheckBox('rescan' + self.tr(' (starts scanning wallet data in blockchain data)'))
        # self.rescan.setChecked(False)
        # self.reindex.setFont(font)
        # self.rescan.setFont(font)
        # spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # startchainDialog.setLayout(startchainDialog.layout)
        # startchainDialog.layout.addWidget(self.reindex)
        # startchainDialog.layout.addWidget(self.rescan)
        # startchainDialog.layout.addLayout(button_layout)
        # button_layout.addItem(spacer_item)
        # button_layout.addWidget(apply_button)
        #
        # apply_button.clicked.connect(self.start_chain_with_settings)
        # apply_button.clicked.connect(startchainDialog.close)
        # startchainDialog.exec_()

    # @pyqtSlot()
    # def start_chain_with_settings(self):
    #     reindex_param = ''
    #     rescan_param = ''
    #     if self.reindex.checkState():
    #         reindex_param = ' -reindex'
    #     if self.rescan.checkState():
    #         rescan_param = ' -rescan'
    #     start_param = self.start_pubkey + reindex_param + rescan_param
    #     logging.info(start_param)
    #     marmarachain_rpc.start_chain(start_param)
    #     time.sleep(0.5)
    #     self.addresses_tableWidget.setColumnHidden(0, True)
    #     self.is_chain_ready()

    @pyqtSlot()
    def download_blocks(self):
        font = QFont()
        font.setPointSize(self.default_fontsize)
        blocksDialog = QDialog(self)
        blocksDialog.setWindowTitle(self.tr('Download Blocks bootstrap'))
        blocksDialog.layout = QGridLayout()
        blocksDialog.setFont(font)
        description_label = QtWidgets.QLabel()
        spacer_item = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        browse_button = QtWidgets.QPushButton(self.tr('Browse ../ Extract'))
        browse_button.setFont(font)
        download_button = QtWidgets.QPushButton('Download')
        download_button.setFont(font)
        description_label.setText(
            self.tr('You can either download or browse and extract previously downloaded bootstrap.'))
        description_label.setFont(font)

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
        get_bootstrap_path = QFileDialog.getOpenFileName(self, caption=self.tr('select bootstrap.tar.gz'),
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
            self.start_animation()
            stopchain_thread = None
            if self.chain_status:
                stopchain_thread = self.stop_chain_thread()
            self.worker_extract_bootstrap = marmarachain_rpc.RpcHandler()  # worker setting
            self.worker_extract_bootstrap.set_command('tar -zvxf ' + bootstrap_path + ' -C ' + destination_path)
            self.worker_extract_bootstrap.set_method(destination_path)
            self.worker_extract_bootstrap.moveToThread(self.thread_extract_bootstrap)  # putting in to thread
            self.worker_extract_bootstrap.finished.connect(self.thread_extract_bootstrap.quit)
            self.worker_extract_bootstrap.finished.connect(self.stop_animation)  # when finished close animation
            self.thread_extract_bootstrap.started.connect(self.worker_extract_bootstrap.extract_bootstrap)
            self.update_chain_textBrowser.clear()
            self.update_chain_textBrowser.setVisible(True)
            if stopchain_thread is None:
                self.thread_extract_bootstrap.start()
            else:
                stopchain_thread.finished.connect(self.thread_extract_bootstrap.start)
            self.worker_extract_bootstrap.output.connect(self.extract_bootstrap_out)
        if messagebox == QMessageBox.No:
            self.bottom_info(self.tr('Bootstrap extracting cancelled'))

    @pyqtSlot(str)
    def extract_bootstrap_out(self, output):
        self.update_chain_textBrowser.append(output)
        logging.info(output)
        if output:
            self.update_chain_textBrowser.setVisible(True)
        if output == 'None':
            self.update_chain_textBrowser.setVisible(False)
            self.bottom_info(self.tr('Extracting blocks finished'))
            logging.info('Extracting blocks finished')

    #     to do extract bootstrap on remote server

    @pyqtSlot()
    def check_fork(self):
        block = self.currentblock_value_label.text()
        self.worker_getblock = marmarachain_rpc.RpcHandler()
        method = cp.getblock
        params = [block]
        self.worker_thread(self.thread_getblock, self.worker_getblock, method, params, self.out_getblock,
                           execute='check_fork_api')

    @pyqtSlot(tuple)
    def out_getblock(self, result_out):
        if result_out[2] == 0:
            if type(result_out[1]) is list:
                fork_message = ""
                forked = False
                self.fork_count = 0
                index = 1
                for r_list in result_out[1]:
                    for item in result_out[0]:
                        if item != r_list[result_out[0].index(item)]:
                            forked = True
                            self.fork_count = self.fork_count + 1
                    if forked:
                        fork_message = fork_message + self.tr('Not Sync with explorer') + str(index) \
                                       + self.tr(" possible fork ") + '\n'
                        forked = False
                    else:
                        fork_message = fork_message + self.tr('Sync with ') + 'explorer' + str(index) + ' \n'
                    index = index + 1
                self.fork_message_box(str(result_out[0][0]), fork_message)
                logging.info(fork_message)
            if result_out[1] == 'error':
                self.bottom_err_info(self.tr('Could not get info from explorer. Check your network connection'))
                logging.info('Could not get info from explorer. Check your network connection')
        elif result_out[2] == 1:
            self.bottom_err_info(result_out[1])

    def fork_message_box(self, result, message):
        fork_message_detail = ""
        if 3 <= self.fork_count <= 9:
            message = message + '\n' + self.tr('Your node forked.')
            fork_message_detail = self.tr("To fix your node fork, stop the chain and start again. if the fork is not "
                                          "fixed, you may try downloading blocks.")
        self.custom_message(self.tr('Comparing Chain with Explorers'), self.tr('Checked for block height ') +
                            result + '\n' + '\n' + message, 'information', QMessageBox.Information,
                            detailed_text=fork_message_detail)

    @pyqtSlot()
    def update_chain_latest(self):
        if not self.latest_chain_version:
            self.check_chain_update()
        if not self.chain_versiyon_tag and self.latest_chain_version:
            installed_chain_versiyon = self.get_installed_chain_version()
            if installed_chain_versiyon:
                self.update_chain_dialogbox(self.tr('your chain version'), self.chain_versiyon_tag)
            else:
                self.update_chain_dialogbox(self.tr('Could not get your version'), "")

        if self.latest_chain_version and self.chain_versiyon_tag:
            self.update_chain_dialogbox(self.tr('your chain version'), self.chain_versiyon_tag)

    def update_chain_dialogbox(self, message, version):
        message_box = self.custom_message('Marmara Chain Update', message +
                                          version + ' \n' + self.tr('Latest available version ')
                                          + self.latest_chain_version, 'question', QMessageBox.Question)
        if message_box == QMessageBox.Yes:
            self.start_animation()
            stopchain_thread = None
            if self.chain_status:
                stopchain_thread = self.stop_chain_thread()
            self.worker_update_chain = marmarachain_rpc.Autoinstall()
            self.worker_update_chain.moveToThread(self.thread_chain_update)  # putting in to thread
            self.worker_update_chain.finished.connect(self.thread_chain_update.quit)
            self.worker_update_chain.finished.connect(self.stop_animation)  # when finished close animation
            self.thread_chain_update.started.connect(self.worker_update_chain.update_chain)
            self.update_chain_textBrowser.clear()
            if stopchain_thread is None:
                self.thread_chain_update.start()
            else:
                stopchain_thread.finished.connect(self.thread_chain_update.start)
            self.update_chain_textBrowser.setVisible(True)
            self.worker_update_chain.out_text.connect(self.update_chain_progress)
            self.worker_update_chain.finished.connect(self.update_chain_finished)

        if message_box == QMessageBox.No:
            self.bottom_info(self.tr('Update closed'))
            logging.info('Update closed')

    @pyqtSlot(str)
    def update_chain_progress(self, out):
        self.update_chain_textBrowser.append(out)

    @pyqtSlot()
    def update_chain_finished(self):
        if self.get_installed_chain_version():
            self.custom_message(self.tr('Update finished'), self.tr('marmara chain ') +
                                self.get_installed_chain_version() + self.tr(' update finished.'), 'information',
                                QMessageBox.Information)
            self.update_chain_textBrowser.setVisible(False)
            self.check_chain_update()
        else:
            self.custom_message(self.tr('Update Failed'), self.tr('Something went wrong update failed.'), 'information')

    @pyqtSlot()
    def toggle_textbrowser(self):
        if self.update_chain_textBrowser.isVisible():
            self.update_chain_textBrowser.setVisible(False)
            self.rescan_checkBox.setVisible(False)
            self.reindex_checkBox.setVisible(False)
        else:
            self.update_chain_textBrowser.setVisible(True)
            if not self.chain_status:
                self.rescan_checkBox.setVisible(True)
                self.reindex_checkBox.setVisible(True)

    # ------------------
    # Chain  --- wallet Address Add, import
    # -------------------
    @pyqtSlot()
    def change_address_frame_visibility(self):
        if self.add_with_seed_radiobutton.isChecked():
            self.new_address_frame.setEnabled(False)
            self.add_seed_address_frame.setEnabled(True)
        if self.add_without_seed_radiobutton.isChecked():
            self.new_address_frame.setEnabled(True)
            self.add_seed_address_frame.setEnabled(False)

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
            method = cp.getnewaddress
            params = []
            self.worker_thread(self.thread_getnewaddress, self.worker_get_newaddress, method, params,
                               self.set_getnewaddress_result)

    @pyqtSlot(tuple)
    def set_getnewaddress_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            # self.bottom_info('new address = ' + str(result_out[0]))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

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
            method = cp.convertpassphrase
            params = [seed]
            self.worker_thread(self.thread_convertpassphrase, self.worker_convert_passphrase, method, params,
                               self.convertpassphrase_result)

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
        method = cp.importprivkey
        params = [wif]
        self.worker_thread(self.thread_importprivkey, self.worker_importprivkey, method, params,
                           self.set_importprivkey_result)

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
        method = cp.getaddressesbyaccount
        params = ['']
        self.worker_thread(self.thread_address_privkey, self.worker_getaddress_privkey, method, params,
                           self.set_privkey_table_result)

    @pyqtSlot(tuple)
    def set_privkey_table_result(self, result_out):
        if result_out[0]:
            result = json.loads(result_out[0])
            self.addresses_privkey_tableWidget.setRowCount(len(result))
            self.addresses_privkey_tableWidget.setSortingEnabled(False)
            for address in result:
                row_number = result.index(address)
                btn_seeprivkey = QPushButton(qta.icon('mdi.shield-key', color='#cc2900'), '')
                btn_seeprivkey.setIconSize(QSize(32, 32))
                self.addresses_privkey_tableWidget.setCellWidget(row_number, 1, btn_seeprivkey)
                self.addresses_privkey_tableWidget.setItem(row_number, 0, QTableWidgetItem(address))
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                           QHeaderView.ResizeToContents)
                self.addresses_privkey_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                           QHeaderView.ResizeToContents)
                btn_seeprivkey.clicked.connect(self.set_seeprivkey)
            self.addresses_privkey_tableWidget.setSortingEnabled(True)
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def set_seeprivkey(self):
        button = self.sender()
        index = self.addresses_privkey_tableWidget.indexAt(button.pos())
        if index.isValid():
            address = self.addresses_privkey_tableWidget.item(index.row(), 0).text()
            self.worker_see_privkey = marmarachain_rpc.RpcHandler()
            method = cp.dumpprivkey
            params = [address]
            self.worker_thread(self.thread_seeprivkey, self.worker_see_privkey, method, params,
                               self.get_seeprivkey_result)

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
    def marmarainfo(self, pubkey, worker_output):
        self.bottom_info(self.tr('getting marmarainfo, please wait'))
        self.worker_marmarainfo = marmarachain_rpc.RpcHandler()
        method = cp.marmarainfo
        params = ['0', '0', '0', '0', pubkey]
        self.worker_thread(self.thread_marmarainfo, self.worker_marmarainfo, method, params,
                           worker_output=worker_output)

    @pyqtSlot()
    def get_wallet_loopinfo(self):
        pubkey = self.current_pubkey_value.text()
        self.marmarainfo(pubkey, self.marmarinfo_amount_and_loops_result)

    @pyqtSlot()
    def get_address_amounts(self):
        pubkey = self.current_pubkey_value.text()
        logging.info('---- current pubkey : ' + pubkey)
        if pubkey and self.myCCActivatedAddress is None:
            self.marmarainfo(pubkey, self.marmarinfo_amount_and_loops_result)
        if pubkey and self.myCCActivatedAddress:
            self.worker_get_address_amounts = marmarachain_rpc.RpcHandler()
            self.worker_thread(self.thread_get_address_amounts, self.worker_get_address_amounts,
                               worker_output=self.set_address_amounts, execute='get_balances')
        if pubkey is "":
            self.bottom_info(self.tr('pubkey is not set!'))
            logging.warning('pubkey is not set!')

    @pyqtSlot(tuple)
    def set_address_amounts(self, result_out):
        if result_out[3] == 0:
            self.wallet_total_normal_value.setText(str(result_out[0]))
            if len(result_out[1]) > 0:
                address_result_out = result_out[1][0]
            else:
                address_result_out = result_out[1]
            for address in address_result_out:
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
            method = cp.marmaralock
            params = [self.lock_amount_value.text()]
            self.worker_thread(self.thread_marmaralock, self.worker_marmaralock, method, params,
                               self.marmaralock_amount_result)

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
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def marmaraunlock_amount(self):
        if not self.unlock_amount_value.text() == "":
            self.worker_marmaraunlock = marmarachain_rpc.RpcHandler()
            method = cp.marmaraunlock
            params = [self.unlock_amount_value.text()]
            self.worker_thread(self.thread_marmaraunlock, self.worker_marmaraunlock, method, params,
                               self.marmaraunlock_amount_result)

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
                    self.sendrawtransaction(result_out[0].replace('"', ''))
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
            self.bottom_err_info(result_out[1])

    # --------------------------------------------------------------------
    # sending raw transaction
    # --------------------------------------------------------------------

    def sendrawtransaction(self, hex):
        self.bottom_info(self.tr('Signing transaction'))
        logging.info('Signing transaction')
        self.worker_sendrawtransaction = marmarachain_rpc.RpcHandler()
        method = cp.sendrawtransaction
        params = [hex]
        time.sleep(0.1)
        self.worker_thread(self.thread_sendrawtransaction, self.worker_sendrawtransaction, method, params,
                           self.sendrawtransaction_result)

    @pyqtSlot(tuple)
    def sendrawtransaction_result(self, result_out):
        if result_out[0]:
            result = str(result_out[0]).replace('\n', '').replace('"', '')
            self.bottom_info('txid: ' + result)
            logging.info('txid: ' + result)
            time.sleep(0.2)  # wait for loading screen disappear
            self.custom_message(self.tr('Transaction Successful'), self.tr('TxId :') + result, "information")
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    # --------------------------------------------------------------------
    # Coin Send-Receive  page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def create_currentaddress_qrcode(self):
        if self.currentaddress_value.text() != "":
            # creating a pix map of qr code
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=7, border=1)
            qr.add_data(self.currentaddress_value.text())
            # set image to the Icon
            qr_image = qr.make_image(image_factory=Image).pixmap()
            msg = QMessageBox()
            msg.setStyleSheet(self.selected_stylesheet)
            msg.setIcon(QMessageBox.Information)
            msg.setIconPixmap(qr_image)
            msg.setWindowTitle(self.currentaddress_value.text() + "  ")
            msg.setStandardButtons(QMessageBox.Close)
            msg.exec_()
        else:
            self.bottom_info(self.tr('no address value set'))
            logging.warning('no address value set')

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
                    method = cp.sendtoaddress
                    params = [self.receiver_address_lineEdit.text(), self.sending_amount_lineEdit.text()]
                    self.worker_thread(self.thread_sendtoaddress, self.worker_sendtoaddress, method, params,
                                       self.sendtoaddress_result)
                if message_box == QMessageBox.No:
                    self.bottom_info(self.tr('Transaction aborted'))
                    logging.info('Transaction aborted')

    @pyqtSlot(tuple)
    def sendtoaddress_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            self.bottom_info('txid : ' + str(result_out[0]).replace('\n', ''))
        if result_out[1]:
            self.bottom_err_info(result_out[1])

    @pyqtSlot()
    def getaddresstxids(self):
        if self.chain_status:
            address = self.currentaddress_value.text()
            start_date = self.transactions_startdate_dateTimeEdit.dateTime()
            end_date = self.transactions_endtdate_dateTimeEdit.dateTime()
            start_height = int(self.currentblock_value_label.text()) - int(
                self.change_datetime_to_block_age(start_date))
            end_height = int(self.currentblock_value_label.text()) - int(self.change_datetime_to_block_age(end_date))
            if start_height < end_height:
                if end_date > datetime.now():
                    end_height = self.currentblock_value_label.text()
                if address == "":
                    self.bottom_info(self.tr('A pubkey is not set yet! Please set a pubkey first.'))
                    logging.info('A pubkey is not set yet! Please set a pubkey first.')
                else:
                    self.worker_getaddresstxids = marmarachain_rpc.RpcHandler()
                    method = cp.getaddresstxids
                    params = [{'addresses': [address], 'start': int(start_height), 'end': int(end_height)}]
                    self.worker_thread(self.thread_getaddresstxids, self.worker_getaddresstxids, method, params,
                                       self.getaddresstxids_result, execute='txids_detail')
            else:
                self.bottom_info(self.tr('Start Date should be before the Stop Date'))
                logging.info('Start Date should be before the Stop Date')
        else:
            self.bottom_info(self.tr('Marmarachain is not started'))
            logging.warning('Marmarachain is not started')

    @pyqtSlot(tuple)
    def getaddresstxids_result(self, result_out):
        if result_out[1] == 0:
            self.transactions_tableWidget.setRowCount(len(result_out[0]))
            self.transactions_tableWidget.setSortingEnabled(False)
            if len(result_out[0]) == 0:
                self.transactions_tableWidget.setRowCount(0)
                self.bottom_err_info(self.tr("No transaction found between selected dates."))
                logging.error("No transaction found between selected dates.")
            else:
                for txid in result_out[0]:
                    self.bottom_info(self.tr("fetched transactions between selected dates."))
                    row_number = result_out[0].index(txid)
                    btn_explorer = QPushButton(qta.icon('mdi.firefox', color='#728FCE'), '')
                    btn_explorer.setIconSize(QSize(24, 24))
                    txid_date = datetime.fromtimestamp(txid[2]).date()
                    self.transactions_tableWidget.setCellWidget(row_number, 0, btn_explorer)
                    self.transactions_tableWidget.setItem(row_number, 1, QTableWidgetItem(str(txid[0])))
                    self.transactions_tableWidget.setItem(row_number, 2, QTableWidgetItem(str(txid[1])))
                    self.transactions_tableWidget.setItem(row_number, 3, QTableWidgetItem(str(txid_date)))
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(0,
                                                                                          QHeaderView.ResizeToContents)
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(1,
                                                                                          QHeaderView.ResizeToContents)
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(2,
                                                                                          QHeaderView.ResizeToContents)
                    self.transactions_tableWidget.horizontalHeader().setSectionResizeMode(3,
                                                                                          QHeaderView.ResizeToContents)
                    btn_explorer.clicked.connect(self.open_in_explorer)
            self.transactions_tableWidget.setSortingEnabled(True)
        if result_out[1] == 1:
            self.bottom_err_info(result_out[1])

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
    def change_visibilty_looprequestpubkey(self):
        if self.looprequest_currentpk_radioButton.isChecked():
            self.looprequest_otherpk_lineEdit.setHidden(True)
            self.contactpk_otherpk_looprequest_comboBox.setHidden(True)
            self.transferrequests_tableWidget.setColumnHidden(0, False)
            self.loop_request_tableWidget.setColumnHidden(0, False)
            self.loop_request_tableWidget.setRowCount(0)
            self.transferrequests_tableWidget.setRowCount(0)
        if self.looprequest_otherpk_radioButton.isChecked():
            self.looprequest_otherpk_lineEdit.setHidden(False)
            self.looprequest_otherpk_lineEdit.clear()
            self.contactpk_otherpk_looprequest_comboBox.setHidden(False)
            self.loop_request_tableWidget.setColumnHidden(0, True)
            self.transferrequests_tableWidget.setColumnHidden(0, True)
            self.loop_request_tableWidget.setRowCount(0)
            self.transferrequests_tableWidget.setRowCount(0)
            self.get_contact_names_pubkeys()

    @pyqtSlot()
    def get_selected_contact_pukey(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contactpubkey_transfer = contacts_data[self.contactpk_otherpk_looprequest_comboBox.currentIndex()]
        if selected_contactpubkey_transfer[2] != 'Pubkey':
            self.looprequest_otherpk_lineEdit.setText(selected_contactpubkey_transfer[2])
        if selected_contactpubkey_transfer[2] == 'Pubkey':
            self.looprequest_otherpk_lineEdit.clear()

    @pyqtSlot()
    def search_marmarareceivelist(self):
        pubkey = self.current_pubkey_value.text()
        if self.looprequest_otherpk_radioButton.isChecked():
            pubkey = self.looprequest_otherpk_lineEdit.text()
        if self.request_date_checkBox.checkState():
            maxage = '1440'
        else:
            date = self.request_dateTimeEdit.dateTime()
            maxage = self.change_datetime_to_block_age(date)
            logging.info('maxage ' + str(maxage))
        self.bottom_info(self.tr('searching incoming loop requests'))
        logging.info('querying incoming loop requests with marmarareceivelist')
        self.worker_marmarareceivelist = marmarachain_rpc.RpcHandler()
        method = cp.marmarareceivelist
        params = [pubkey, str(maxage)]
        self.worker_thread(self.thread_marmarareceivelist, self.worker_marmarareceivelist, method, params,
                           self.search_marmarareceivelist_result)

    @pyqtSlot(tuple)
    def search_marmarareceivelist_result(self, result_out):
        if result_out[2] == 200 or result_out[2] == 0:
            self.bottom_info(self.tr('finished searching incoming loop requests'))
            logging.info('finished querying incoming loop requests')
            result = json.loads(str(result_out[0]))
            if type(result) == list:
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
            if type(result) == dict:
                if result.get('result') == 'error':
                    self.bottom_err_info(result.get('error'))
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def set_credit_request_table(self, credit_request_list):
        self.loop_request_tableWidget.setRowCount(len(credit_request_list))
        self.loop_request_tableWidget.setColumnHidden(5, True)
        self.loop_request_tableWidget.setSortingEnabled(False)
        for row in credit_request_list:
            row_number = credit_request_list.index(row)
            btn_review = QPushButton(qta.icon('mdi.text-box-check-outline', color='#728FCE'), '')
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
        self.loop_request_tableWidget.setSortingEnabled(True)

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
        self.transferrequests_tableWidget.setSortingEnabled(False)
        for row in transfer_request_list:
            row_number = transfer_request_list.index(row)
            btn_review = QPushButton(qta.icon('mdi.text-box-check-outline', color='#728FCE'), '')
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
        self.transferrequests_tableWidget.setSortingEnabled(True)

    @pyqtSlot()
    def review_credittransfer_request(self):
        button = self.sender()
        index = self.transferrequests_tableWidget.indexAt(button.pos())
        if index.isValid():
            tx_id = self.transferrequests_tableWidget.item(index.row(), 1).text()
            receiver_pk = self.transferrequests_tableWidget.item(index.row(), 5).text()
            self.marmaratransfer(receiver_pk, tx_id)

    def marmaraissue(self, receiver_pk, txid):
        method = cp.marmaraissue
        params = [receiver_pk, {'avalcount': '0', 'autosettlement': 'true', 'autoinsurance': 'true',
                                'disputeexpires': 'offset', 'EscrowOn': 'false', 'BlockageAmount': '0'}, txid]
        self.worker_marmaraissue = marmarachain_rpc.RpcHandler()
        self.worker_thread(self.thread_marmaraissue, self.worker_marmaraissue, method, params, self.marmaraissue_result)

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
            self.bottom_err_info(result_out[1])

    def marmaratransfer(self, receiver_pk, tx_id):
        method = cp.marmaratransfer
        params = [receiver_pk, {'avalcount': '0'}, tx_id]
        self.worker_marmaratransfer = marmarachain_rpc.RpcHandler()
        self.worker_thread(self.thread_marmaratransfer, self.worker_marmaratransfer, method, params,
                           self.marmaratransfer_result)

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

    # --- Create Loop Request page functions ----

    @pyqtSlot()
    def marmarareceive(self):
        amount = self.make_credit_loop_amount_lineEdit.text()
        senderpk = self.make_credit_loop_senderpubkey_lineEdit.text()
        matures_date = self.make_credit_loop_matures_dateTimeEdit.dateTime()
        matures = self.change_datetime_to_block_age(matures_date)
        if amount and senderpk and matures:
            self.worker_marmarareceive = marmarachain_rpc.RpcHandler()
            method = cp.marmarareceive
            currency = self.make_credit_loop_currency_value_label.text()
            params = [senderpk, amount, currency, str(matures), {'avalcount': '0'}]
            self.bottom_info(self.tr('preparing loop request'))
            self.worker_thread(self.thread_marmarareceive, self.worker_marmarareceive, method, params,
                               self.marmarareceive_result)
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

    # function name: marmararecieve_transfer
    # purpose:  holder makes a marmarareceive request to the endorser to get the credit for selling the goods/services
    @pyqtSlot()
    def marmararecieve_transfer(self):
        senderpk = self.transfer_senderpubkey_lineEdit.text()
        baton = self.transfer_baton_lineEdit.text()
        if senderpk and baton:
            self.worker_marmarareceive_transfer = marmarachain_rpc.RpcHandler()
            method = cp.marmarareceive
            params = [senderpk, baton, {'avalcount': '0'}]
            self.worker_thread(self.thread_marmarareceive_transfer, self.worker_marmarareceive_transfer,
                               method, params, self.marmararecieve_transfer_result)
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
            self.bottom_err_info(result_out[1])

    # -------------------------------------------------------------------
    # Total Credit Loops page functions
    # --------------------------------------------------------------------
    @pyqtSlot()
    def search_active_loops(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey:
            self.bottom_info(self.tr('getting active Loops details'))
            logging.info('getting active Loops details')
            self.worker_getloops = marmarachain_rpc.RpcHandler()
            method = cp.marmarainfo
            params = ['0', '0', '0', '0', pubkey]
            self.worker_thread(self.thread_getloops, self.worker_getloops, method, params, self.loops_details_result,
                               execute='active_loops_details')
        else:
            self.bottom_info('pubkey not set!')
            self.clear_search_active_loops_labels()

    @pyqtSlot(tuple)
    def loops_details_result(self, result_out):
        if result_out[2] == 0:
            self.set_activeloops_table(result_out[0])
            self.set_loop_amount_result(result_out[1])
            self.refresh_loopinfo_button.setVisible(True)
        if result_out[2] == 1:
            self.bottom_err_info(result_out[1])
            logging.error(str(result_out[1]))

    def set_loop_amount_result(self, result):
        self.myCCActivatedAddress = str(result.get('myCCActivatedAddress'))
        self.normal_amount_value.setText(str(result.get('myPubkeyNormalAmount')))
        self.wallet_total_normal_value.setText(str(result.get('myWalletNormalAmount')))
        self.activated_amount_value.setText(str(result.get('myActivatedAmount')))
        self.activeloops_total_amount_value_label.setText(str(result.get('TotalLockedInLoop')))
        self.total_issuer_loop_amount_label_value.setText(str(result.get('totalamount')))
        self.closedloops_total_amount_value_label.setText(str(result.get('totalclosed')))
        self.activeloops_pending_number_value_label.setText(str(result.get('numpending')))
        self.closedloops_total_number_value_label.setText(str(result.get('numclosed')))
        self.numberof_total_activeloops_label_value.setText(str(len(result.get('Loops'))))
        my_total_normal = float(self.wallet_total_normal_value.text())
        my_total_activated = float(self.activated_amount_value.text())
        my_total_inloops = float(self.activeloops_total_amount_value_label.text())
        self.stats_amount_in_activated_lineEdit.setText(self.totalactivated_value_label.text())
        self.stats_amount_in_loops_lineEdit.setText(self.activeloops_total_amount_value_label.text())
        my_total = my_total_normal + my_total_activated + my_total_inloops
        self.my_stats_normal_label_value.setText(str(round((my_total_normal / my_total) * 100, 2)))
        self.my_stats_activated_label_value.setText(str(round((my_total_activated / my_total) * 100, 2)))
        self.my_stats_inloops_label_value.setText(str(round((my_total_inloops / my_total) * 100, 2)))

    @pyqtSlot(tuple)
    def marmarinfo_amount_and_loops_result(self, result_out):
        if result_out[0]:
            logging.info(result_out[0])
            result = json.loads(result_out[0])
            if result.get('result') == "success":
                # self.wallet_total_activated_value.setText(str(result.get('myTotalAmountOnActivatedAddress')))
                self.bottom_info(self.tr('getting address amounts finished'))
                self.set_loop_amount_result(result)
                self.bottom_info(self.tr('finished searching marmara blockchain for all blocks for the set pubkey'))
                logging.info('finished searching marmara blockchain for all blocks for the set pubkey')
                self.refresh_loopinfo_button.setVisible(True)
            if result.get('result') == "error":
                self.bottom_info(result.get('error'))
                logging.error(result.get('error'))
                self.clear_search_active_loops_labels()
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def set_activeloops_table(self, loop_info):
        self.activeloops_tableWidget.setColumnHidden(5, True)
        self.activeloops_tableWidget.setRowCount(len(loop_info))
        self.activeloops_tableWidget.setSortingEnabled(False)
        for section in loop_info:
            row_number = loop_info.index(section)
            for item in section:
                column_no = section.index(item)
                if column_no == 2:
                    item = self.check_pubkey_contact_name(item)
                if column_no == 3 or column_no == 4:
                    item = self.change_block_to_date(item)
                self.activeloops_tableWidget.setItem(row_number, column_no, QTableWidgetItem(str(item)))
                self.activeloops_tableWidget.horizontalHeader().setSectionResizeMode(column_no,
                                                                                     QHeaderView.ResizeToContents)
        self.activeloops_tableWidget.setSortingEnabled(True)

    def clear_search_active_loops_labels(self):
        self.total_issuer_loop_amount_label_value.clear()
        self.closedloops_total_amount_value_label.clear()
        self.activeloops_pending_number_value_label.clear()
        self.closedloops_total_number_value_label.clear()

    def clear_search_holder_loops_labels(self):
        self.total_transferrable_loop_amount_label_value.clear()
        self.numberof_transferrable_loop_amount_label_value.clear()
        self.holderloops_closed_amount_label_value.clear()
        self.holderloops_closed_number_label_value.clear()

    @pyqtSlot()
    def marmaraholderloops(self):
        pubkey = self.current_pubkey_value.text()
        if pubkey:
            self.bottom_info(self.tr('getting transferable Loops details'))
            logging.info('getting transferable Loops details')
            self.worker_holderloops = marmarachain_rpc.RpcHandler()
            method = cp.marmaraholderloops
            params = ['0', '0', '0', '0', pubkey]
            self.worker_thread(self.thread_marmarholderloop, self.worker_holderloops, method, params,
                               worker_output=self.marmaraholderloops_result, execute='holder_loop_detail')
        else:
            self.bottom_info('pubkey not set!')
            self.clear_search_holder_loops_labels()

    @pyqtSlot(tuple)
    def marmaraholderloops_result(self, result_out):
        if result_out[2] == 0:
            self.set_holder_loops_table(result_out[0])
            self.total_transferrable_loop_amount_label_value.setText(str(result_out[1].get('totalamount')))
            self.numberof_transferrable_loop_amount_label_value.setText(str(result_out[1].get('numpending')))
            self.holderloops_closed_amount_label_value.setText(str(result_out[1].get('numclosed')))
            self.holderloops_closed_number_label_value.setText(str(result_out[1].get('totalclosed')))
        if result_out[2] == 1:
            self.bottom_err_info(result_out[1])
            logging.error(str(result_out[1]))

    def set_holder_loops_table(self, loop_info):
        self.transferableloops_tableWidget.setColumnHidden(5, True)
        self.transferableloops_tableWidget.setRowCount(len(loop_info))
        self.transferableloops_tableWidget.setSortingEnabled(False)
        for section in loop_info:
            row_number = loop_info.index(section)
            for item in section:
                column_no = section.index(item)
                if column_no == 2:
                    item = self.check_pubkey_contact_name(item)
                if column_no == 3 or column_no == 4:
                    item = self.change_block_to_date(item)
                self.transferableloops_tableWidget.setItem(row_number, column_no, QTableWidgetItem(str(item)))
                self.transferableloops_tableWidget.horizontalHeader().setSectionResizeMode(column_no,
                                                                                           QHeaderView.ResizeToContents)
        self.transferableloops_tableWidget.setSortingEnabled(True)

    @pyqtSlot(int, int)
    def activeloop_itemcontext(self, row, column):
        item = self.activeloops_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_info(self.tr("Copied ") + str(item))

    @pyqtSlot(int, int)
    def transferableloops_itemcontext(self, row, column):
        item = self.transferableloops_tableWidget.item(row, column).text()
        QtWidgets.QApplication.clipboard().setText(item)
        self.bottom_info(self.tr("Copied ") + str(item))

    # -------------------------------------------------------------------
    # Credit Loop Queries functions
    # --------------------------------------------------------------------

    @pyqtSlot()
    def search_any_pubkey_loops(self):
        pubkey = self.loopqueries_pubkey_lineEdit.text()
        if pubkey:
            self.marmarainfo(pubkey, self.get_search_any_pubkey_loops_result)
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
        method = cp.marmaracreditloop
        params = [txid]
        marmaracreditloop_thread = self.worker_thread(self.thread_marmaracreditloop, self.worker_marmaracreditloop,
                                                      method, params)
        return marmaracreditloop_thread

    @pyqtSlot()
    def search_loop_txid(self):
        txid = self.loopsearch_txid_lineEdit.text()
        if txid:
            marmaracreditloop = self.marmaracreditloop(txid)
            if self.chain_status:
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
            else:
                creditloop = result.get('creditloop')
                if str(result.get('funcid')) == 'S':
                    baton = str(result.get('settlement'))
                    batonpk = str(result.get('pubkey'))
                    amount = str(result.get('collected'))
                    self.loopquery_baton_label.setText(self.tr('Txid (Settlement)'))
                    issuerpk = str((creditloop[0]).get('issuerpk'))
                elif str(result.get('funcid')) == 'B':
                    issuerpk = str(result.get('issuerpk'))
                    amount = str(result.get('amount'))
                    baton = str(result.get('createtxid'))
                    batonpk = str(self.tr('Not issued yet!'))
                    self.loopquery_baton_label.setText(self.tr('Txid (baton)'))
                else:
                    baton = str(result.get('batontxid'))
                    batonpk = str(result.get('batonpk'))
                    amount = str(result.get('amount'))
                    issuerpk = str((creditloop[0]).get('issuerpk'))
                    self.loopquery_baton_label.setText(self.tr('Txid (baton)'))

                self.loopquery_baton_value.setText(baton)
                self.loopquery_amount_value.setText(amount)
                self.loopquery_currency_value.setText(result.get('currency'))
                self.loopquery_matures_value.setText(str(result.get('matures')))
                self.loopquery_batonpk_value.setText(batonpk)
                self.loopquery_issuer_value.setText(issuerpk)
                self.loopquery_transfercount_value.setText(str(result.get('n')))
                self.bottom_info(self.tr('credit loop info finished'))
                logging.info('credit loop info finished')
        elif result_out[1]:
            self.bottom_err_info(result_out[1])

    def clear_lq_txid_search_result(self):
        self.loopquery_baton_value.clear()
        self.loopquery_amount_value.clear()
        self.loopquery_batonpk_value.clear()
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
        self.contactpk_makeloop_comboBox.clear()
        self.contactpk_transferrequest_comboBox.clear()
        self.contactpk_otherpk_looprequest_comboBox.clear()
        self.make_credit_loop_senderpubkey_lineEdit.clear()
        self.transfer_senderpubkey_lineEdit.clear()
        self.contactpk_makeloop_comboBox.addItem(self.tr('Contacts'))
        self.contactpk_transferrequest_comboBox.addItem(self.tr('Contacts'))
        self.contactpk_otherpk_looprequest_comboBox.addItem(self.tr('Contacts'))
        contacts_data = configuration.ContactsSettings().read_csv_file()
        for name in contacts_data:
            if name[0] != 'Name':
                self.contactpk_makeloop_comboBox.addItem(name[0])
                self.contactpk_transferrequest_comboBox.addItem(name[0])
                self.contactpk_otherpk_looprequest_comboBox.addItem(name[0])

    @pyqtSlot()
    def get_selected_contact_loop_pubkey(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contactpubkey_loop = contacts_data[self.contactpk_makeloop_comboBox.currentIndex()]
        if selected_contactpubkey_loop[2] != 'Pubkey':
            self.make_credit_loop_senderpubkey_lineEdit.setText(selected_contactpubkey_loop[2])
        if selected_contactpubkey_loop[2] == 'Pubkey':
            self.make_credit_loop_senderpubkey_lineEdit.clear()

    @pyqtSlot()
    def get_selected_contact_transfer_pubkey(self):
        contacts_data = configuration.ContactsSettings().read_csv_file()
        selected_contactpubkey_transfer = contacts_data[self.contactpk_transferrequest_comboBox.currentIndex()]
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
        contact_address = self.contactaddress_lineEdit.text().replace(' ', '')
        contact_pubkey = self.contactpubkey_lineEdit.text().replace(' ', '')
        contact_group = self.contactgroup_lineEdit.text().replace(' ', '')
        new_record = [contact_name, contact_address, contact_pubkey, contact_group]
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
        self.contactgroup_lineEdit.clear()
        self.contact_editing_row = None

    def update_contact_tablewidget(self, contacts_data=None):
        self.contacts_tableWidget.setSortingEnabled(False)
        if contacts_data:
            pass
        elif not contacts_data:
            contacts_data = configuration.ContactsSettings().read_csv_file()
        self.contacts_tableWidget.setRowCount(len(contacts_data) - 1)  # -1 for exclude header
        del contacts_data[0]
        # self.contacts_tableWidget.autoScrollMargin()
        for row in contacts_data:
            row_number = contacts_data.index(row)  # -1 for exclude header
            if len(row) < 4:
                row.append('')
            for item in row:
                self.contacts_tableWidget.setItem(row_number, row.index(item), QTableWidgetItem(str(item)))
                self.contacts_tableWidget.horizontalHeader().setSectionResizeMode(row.index(item),
                                                                                  QHeaderView.ResizeToContents)
        self.contacts_tableWidget.setSortingEnabled(True)

    @pyqtSlot(int, int)
    def get_contact_info(self, row, column):
        contact_name = ""
        contact_address = ""
        contact_pubkey = ""
        contact_group = ""
        if self.contacts_tableWidget.item(row, 0):
            contact_name = self.contacts_tableWidget.item(row, 0).text()
        if self.contacts_tableWidget.item(row, 1):
            contact_address = self.contacts_tableWidget.item(row, 1).text()
        if self.contacts_tableWidget.item(row, 2):
            contact_pubkey = self.contacts_tableWidget.item(row, 2).text()
        if self.contacts_tableWidget.item(row, 3):
            contact_group = self.contacts_tableWidget.item(row, 3).text()
        self.contactname_lineEdit.setText(contact_name)
        self.contactaddress_lineEdit.setText(contact_address)
        self.contactpubkey_lineEdit.setText(contact_pubkey)
        self.contactgroup_lineEdit.setText(contact_group)
        self.contact_editing_row = row

    @pyqtSlot()
    def update_contact(self):
        self.contacts_tableWidget.setSortingEnabled(False)
        if self.contact_editing_row is not None:
            read_contacts_data = configuration.ContactsSettings().read_csv_file()
            contact_name = self.contactname_lineEdit.text()
            contact_address = self.contactaddress_lineEdit.text().replace(' ', '')
            contact_pubkey = self.contactpubkey_lineEdit.text().replace(' ', '')
            contact_group = self.contactgroup_lineEdit.text().replace(' ', '')
            contact_data = configuration.ContactsSettings().read_csv_file()
            item_name = self.contacts_tableWidget.item(self.contact_editing_row, 0).text()
            for row in contact_data:
                if row[0] == item_name:
                    self.contact_editing_row = contact_data.index(row)
            del contact_data[self.contact_editing_row]  # removing editing record to don't check same record
            unique_record = self.unique_contacts(contact_name, contact_address, contact_pubkey, contact_data)
            if unique_record:
                self.bottom_info(unique_record.get('error'))
                logging.error(unique_record.get('error'))
            if not unique_record:
                read_contacts_data[self.contact_editing_row] = [contact_name, contact_address, contact_pubkey,
                                                                contact_group]
                configuration.ContactsSettings().update_csv_file(read_contacts_data)
                self.update_contact_tablewidget()
                self.clear_contacts_line_edit()
        else:
            message_box = self.custom_message(self.tr('Error Updating Contact'),
                                              self.tr('You did not select a contact from table.'),
                                              "information",
                                              QMessageBox.Information)
        self.contacts_tableWidget.setSortingEnabled(True)

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
        self.worker_mcl_stats = marmarachain_rpc.ApiWorker()
        self.worker_mcl_stats.moveToThread(self.thread_api_stats_request)
        self.worker_mcl_stats.finished.connect(self.thread_api_stats_request.quit)
        self.thread_api_stats_request.started.connect(self.worker_mcl_stats.mcl_stats_api)
        self.thread_api_stats_request.start()
        self.worker_mcl_stats.out_dict.connect(self.set_marmara_stats_values)
        self.worker_mcl_stats.out_err.connect(self.set_marmara_stats_err)
        self.stats_refresh_pushButton.setEnabled(False)
        QtCore.QTimer.singleShot(60000, self.stat_refresh_enable)  # after 60 second it will enable button

    @pyqtSlot(dict)
    def set_marmara_stats_values(self, mcl_stats):
        mcl_stats_info = mcl_stats.get('info')
        self.stats_height_value_label.setText(str(mcl_stats_info.get('height')))
        self.stats_normal_label_value.setText(str(mcl_stats_info.get('TotalNormals')))
        self.stats_activated_label_value.setText(str(mcl_stats_info.get('TotalActivated')))
        self.stats_in_loops_label_value.setText(str(mcl_stats_info.get('TotalLockedInLoops')))
        self.bottom_info(self.tr('stats values retrieved'))
        self.stats_calculate_pushButton.setEnabled(True)
        self.stats_amount_in_activated_lineEdit.setEnabled(True)
        self.stats_amount_in_loops_lineEdit.setEnabled(True)
        total_supply = int(mcl_stats_info.get('TotalNormals')) + int(mcl_stats_info.get('TotalActivated')) + int(
            mcl_stats_info.get('TotalLockedInLoops'))
        total_normal_percentage = (int(mcl_stats_info.get('TotalNormals')) * 100) / total_supply
        total_activated_percentage = (int(mcl_stats_info.get('TotalActivated')) * 100) / total_supply
        total_inloops_percentage = (int(mcl_stats_info.get('TotalLockedInLoops')) * 100) / total_supply
        total_normal_per = round(total_normal_percentage, 2)
        total_activated_per = round(total_activated_percentage, 2)
        total_inloops_per = round(total_inloops_percentage, 2)
        self.stat_pie_chart(total_normal_per, total_activated_per, total_inloops_per)

    @pyqtSlot(str)
    def set_marmara_stats_err(self, err):
        if err == 'error':
            self.bottom_err_info(self.tr('Error in getting stats values'))

    def stat_pie_chart(self, normal, activated, inloops):
        if self.stats_layout.count() != 0:
            self.stats_layout.removeWidget(self.chartview)
        series = QPieSeries()
        series.append("Normal", normal)
        series.append("Activated", activated)
        series.append("In Loops", inloops)

        series.setLabelsVisible(True)
        # color = [Qt.green, Qt.gray, Qt.magenta]
        series.setLabelsPosition(QtChart.QPieSlice.LabelOutside)
        for qslice in series.slices():
            qslice.setLabel("{:.2f}%".format(100 * qslice.percentage()))
            # qslice.setBrush(color[series.slices().index(qslice)])

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        chart.legend().markers(series)[0].setLabel(self.tr("Total Normal"))
        chart.legend().markers(series)[1].setLabel(self.tr("Total Activated"))
        chart.legend().markers(series)[2].setLabel(self.tr("Total In Loops"))
        self.chartview = QChartView(chart)
        self.chartview.setRenderHint(QPainter.Antialiasing)
        self.stats_layout.addWidget(self.chartview)

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
        calculation = (((amount_activated / total_activated) + (amount_inloops / total_inloops) * 3) / 4) * 32400
        self.stats_estimated_staking_label_value.setText(str(calculation))
        # 30 * 60 * 24 * 0,75  = 32400

    @pyqtSlot()
    def get_wallet_earnings(self):
        if self.chain_status:
            start_datetime = self.earning_start_dateTimeEdit.dateTime()
            stop_datetime = self.earning_stop_dateTimeEdit.dateTime()
            latest_block = self.currentblock_value_label.text()
            beginheigth = int(latest_block) - int(self.change_datetime_to_block_age(start_datetime))
            endheigth = int(latest_block) - int(self.change_datetime_to_block_age(stop_datetime))
            if not beginheigth < endheigth <= int(latest_block):
                self.bottom_info(self.tr('Wrong Date Selection. start date should be less then stop date'))
            else:
                if (endheigth - beginheigth) <= 57600:  # if more less 40 days
                    self.worker_earnings = marmarachain_rpc.RpcHandler()
                    method = cp.getblock
                    params = [beginheigth, endheigth]
                    self.worker_thread(self.thread_earnings, self.worker_earnings, method, params,
                                       worker_output=self.set_earnings_output, execute='wallet_earnings')
                else:
                    self.bottom_info(self.tr('Difference between start and end dates cannot exceed 40 days'))
        else:
            self.bottom_info(self.tr('Marmarachain is not started'))
            logging.warning('Marmarachain is not started')

    @pyqtSlot(tuple)
    def set_earnings_output(self, output):
        if output[2] == 0:
            self.earning_stats_tableWidget.setRowCount(len(output[0]))
            normal_amount_sum = 0
            activated_amount_sum = 0
            row_index = 0
            for n_item, ac_item in zip(output[0], output[1]):
                normal_amount_sum = output[0].get(n_item) + normal_amount_sum
                activated_amount_sum = output[1].get(ac_item) + activated_amount_sum
                normal_amount = str(output[0].get(n_item))
                actve_amount = str(output[1].get(ac_item))
                total_amount = str(output[0].get(n_item) + output[1].get(ac_item))
                if configuration.ApplicationConfig().get_value('USER', 'lang') == 'TR':
                    normal_amount = normal_amount.replace('.', ',')
                    actve_amount = actve_amount.replace('.', ',')
                    total_amount = total_amount.replace('.', ',')
                self.earning_stats_tableWidget.setItem(row_index, 0, QTableWidgetItem(str(n_item)))
                self.earning_stats_tableWidget.setItem(row_index, 1, QTableWidgetItem(normal_amount))
                self.earning_stats_tableWidget.setItem(row_index, 2, QTableWidgetItem(actve_amount))
                self.earning_stats_tableWidget.setItem(row_index, 3, QTableWidgetItem(total_amount))
                self.earning_stats_tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
                self.earning_stats_tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
                self.earning_stats_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
                self.earning_stats_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
                if row_index < len(output[0]) - 1:
                    row_index = row_index + 1
            self.normal_earning_value.setText(str(normal_amount_sum))
            self.activated_earning_value.setText(str(activated_amount_sum))
            self.total_earning_value.setText(str(normal_amount_sum + activated_amount_sum))
            self.bottom_info(self.tr('finished getting earning stats'))
        if output[2] == 1:
            self.bottom_err_info(output[1])

    @pyqtSlot(str)
    def earnings_output_info(self, output):
        if output == 'normal txids':
            self.bottom_info(self.tr('Getting normal addresses transactions'))
        if output == 'activated txids':
            self.bottom_info(self.tr('Getting activated addresses transactions'))
        if output == 'calculating earnings':
            self.bottom_info(self.tr('Calculating earnings for normal and activated addresses'))

    @pyqtSlot()
    def pay_for_export(self):
        if self.earning_stats_tableWidget.rowCount() > 0:
            team_address = 'RXWqisAoJKEGVyXj46Zo3fDZnZTwQA6kQE'
            message_box = self.custom_message(self.tr('Support the team to export'),
                                              self.tr('You are about to send 5 MCL to Marmara Team'),
                                              "question",
                                              QMessageBox.Question)
            if message_box == QMessageBox.Yes:
                self.worker_sendtoaddress = marmarachain_rpc.RpcHandler()
                method = cp.sendtoaddress
                params = [team_address, 5]
                self.worker_thread(self.thread_sendtoaddress, self.worker_sendtoaddress, method, params,
                                   self.export_table_to_csv)

            if message_box == QMessageBox.No:
                self.bottom_info(self.tr('Transaction aborted'))
                logging.info('Transaction aborted')
        else:
            self.bottom_info(self.tr('Table has no data to export'))
            logging.info('Table has no data to export')

    @pyqtSlot(tuple)
    def export_table_to_csv(self, txid):
        if txid[0]:
            logging.info(txid[0])
            self.bottom_info('txid : ' + str(txid[0]).replace('\n', ''))
            earnings_data = self.get_table_datas(self.earning_stats_tableWidget)
            self.export_as_csv_file(earnings_data)
        if txid[1]:
            self.bottom_err_info(txid[1])

    def export_as_csv_file(self, export_data):
        strt_date = str(self.earning_start_dateTimeEdit.dateTime().date().toString(QtCore.Qt.ISODate))
        stp_date = str(self.earning_stop_dateTimeEdit.dateTime().date().toString(QtCore.Qt.ISODate))
        if platform.system() == 'Linux':
            destination_path = str(pathlib.Path.home()) + '/Documents'
            csv_name = '/earning-stats_' + strt_date + '_' + stp_date + '.csv'
        if platform.system() == 'Win64' or platform.system() == 'Windows':
            destination_path = str(pathlib.Path.home()) + '\Documents'
            csv_name = '\earning-stats_' + strt_date + '_' + stp_date + '.csv'

        filename = QFileDialog.getExistingDirectory(self, 'Choose Location to save csv file', str(destination_path))
        configuration.export_as_scv(filename + csv_name, export_data)

    def get_table_datas(self, table):
        col_cnt = table.columnCount()
        table_data = []
        Header = []
        for col_no in range(col_cnt):
            Header.append(table.horizontalHeaderItem(col_no).text())
        table_data.append(Header)
        row_cnt = table.rowCount()
        if row_cnt > 0:
            for row_no in range(row_cnt):
                row_data = []
                for col_no in range(col_cnt):
                    data = table.item(row_no, col_no).text()
                    row_data.append(data)
                table_data.append(row_data)
        return table_data

    # -----------------
    # Market Page
    # -----------------

    def update_exchange_market_combobox(self):
        self.exchange_market_comboBox.clear()
        api_list = api_request.exchange_market_api_list
        for item in api_list:
            self.exchange_market_comboBox.addItem(str(item))

    @pyqtSlot()
    def get_mcl_exchange_market(self):
        self.exchange_market_request_button.setEnabled(False)
        QtCore.QTimer.singleShot(20000, self.enable_market_request)  # after 20 second it will enable button
        index = self.exchange_market_comboBox.currentIndex()
        key = self.exchange_market_comboBox.itemText(index)
        self.mcl_exchange_worker = marmarachain_rpc.ApiWorker()
        self.mcl_exchange_worker.set_api_key(key)
        self.mcl_exchange_worker.moveToThread(self.thread_api_exchange_request)
        self.mcl_exchange_worker.finished.connect(self.thread_api_exchange_request.quit)
        self.thread_api_exchange_request.started.connect(self.mcl_exchange_worker.exchange_api_run)
        self.thread_api_exchange_request.start()
        self.mcl_exchange_worker.out_list.connect(self.set_mcl_exchange_market_result)
        # self.mcl_exchange_worker.out_err.connect(self.err_mcl_exchange_market_result)

    @pyqtSlot(list)
    def set_mcl_exchange_market_result(self, out_list):
        out_json = out_list[0]
        if type(out_json) is list:
            self.mcl_exchange_market_result = out_json
            self.update_exchange_table()
        if type(out_json) is str:
            if out_json == 'error':
                self.bottom_err_info(self.tr('Error in getting exchange values'))
        if out_list[1]:
            if type(out_list[1]) is dict:
                self.mcl_exchange_ticker_result = out_list[1]
                self.update_ticker_table()
            if type(out_list[1]) is str:
                if out_list[1] == 'error':
                    self.bottom_err_info(self.tr('Error in getting exchange values'))

    def update_exchange_table(self):
        self.exchange_market_tableWidget.setRowCount(len(self.mcl_exchange_market_result))
        self.exchange_market_tableWidget.setSortingEnabled(False)
        fiat = self.market_fiat_comboBox.currentText()
        for row in self.mcl_exchange_market_result:
            price = ('%.8f' % row.get('quotes').get(fiat).get('price'))
            volume = ('%.8f' % row.get('quotes').get(fiat).get('volume_24h'))
            row_number = self.mcl_exchange_market_result.index(row)
            self.exchange_market_tableWidget.setItem(row_number, 0, QTableWidgetItem(str(row.get('exchange_name'))))
            self.exchange_market_tableWidget.setItem(row_number, 1, QTableWidgetItem(str(row.get('pair'))))
            self.exchange_market_tableWidget.setItem(row_number, 2, QTableWidgetItem(str(price)))
            self.exchange_market_tableWidget.setItem(row_number, 3, QTableWidgetItem(str(volume)))
            self.exchange_market_tableWidget.setItem(row_number, 4, QTableWidgetItem(
                str(row.get('last_updated')).replace('T', ' ').replace('Z', '')))
            self.exchange_market_tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
            self.exchange_market_tableWidget.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
            self.exchange_market_tableWidget.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
            self.exchange_market_tableWidget.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
            self.exchange_market_tableWidget.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
            self.bottom_info(self.tr('fetched exchange values'))
        self.exchange_market_tableWidget.setSortingEnabled(True)

    def update_ticker_table(self):
        fiat = self.market_fiat_comboBox.currentText()
        price = ('%.8f' % self.mcl_exchange_ticker_result.get(fiat).get('price'))
        volume = ('%.8f' % self.mcl_exchange_ticker_result.get(fiat).get('volume_24h'))
        self.ticker_price_label_value.setText(str(price))
        self.ticker_volume_label_value.setText(str(volume))
        self.ticker_1hour_label_value.setText(
            str(self.mcl_exchange_ticker_result.get(fiat).get('percent_change_1h')))
        self.ticker_24hour_label_value.setText(
            str(self.mcl_exchange_ticker_result.get(fiat).get('percent_change_24h')))
        self.ticker_1week_label_value.setText(
            str(self.mcl_exchange_ticker_result.get(fiat).get('percent_change_7d')))
        self.ticker_1month_label_value.setText(
            str(self.mcl_exchange_ticker_result.get(fiat).get('percent_change_30d')))
        if self.ticker_price_label_value.text():
            self.mcl_amount_lineEdit.setEnabled(True)
            self.usd_amount_lineEdit.setEnabled(True)

    @pyqtSlot()
    def market_fiat_changed(self):
        self.convert_usd_label.setText(self.market_fiat_comboBox.currentText())
        self.calculate_usd_price()
        if self.mcl_exchange_market_result and self.mcl_exchange_ticker_result:
            self.update_exchange_table()
            self.update_ticker_table()

    @pyqtSlot()
    def calculate_usd_price(self):
        if self.mcl_amount_lineEdit.text():
            current_fiat = self.market_fiat_comboBox.currentText()
            price = float(self.mcl_exchange_ticker_result.get(current_fiat).get('price'))
            calculation = float(self.mcl_amount_lineEdit.text()) * price
            self.usd_amount_lineEdit.setText(str('%.8f' % calculation))

    @pyqtSlot()
    def calculate_mcl_price(self):
        if self.usd_amount_lineEdit.text():
            current_fiat = self.market_fiat_comboBox.currentText()
            price = float(self.mcl_exchange_ticker_result.get(current_fiat).get('price'))
            calculation = float(self.usd_amount_lineEdit.text()) / price
            self.mcl_amount_lineEdit.setText(str('%.8f' % calculation))

    @pyqtSlot()
    def enable_market_request(self):
        self.exchange_market_request_button.setEnabled(True)

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
    def enable_ssh_custom_port(self):
        if self.ssh_port_checkBox.isChecked():
            self.ssh_port_lineEdit.setEnabled(True)
        else:
            self.ssh_port_lineEdit.setEnabled(False)
            self.ssh_port_lineEdit.setText('22')

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


if __name__ == '__main__':
    appctxt = ApplicationContext()
    ui = MarmaraMain()
    ui.show()
    exit_code = appctxt.app.exec_()
    sys.exit(exit_code)
