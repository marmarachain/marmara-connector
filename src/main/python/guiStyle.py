from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QDoubleValidator, QIcon
from ThreadGui import ActiveLoops
from guiDesign import Ui_MainWindow
from fbs_runtime.application_context.PyQt5 import ApplicationContext

class GuiStyle(Ui_MainWindow,ApplicationContext):
    def __init__(self):
        self.setupUi(self)

        self.icon_path = self.get_resource("images")
        now = QtCore.QDateTime.currentDateTime()
        self.dateTimeEdit.setDateTime(now)

        self.dateTimeEdit.setMaximumDateTime(QtCore.QDateTime.currentDateTime())
        self.dateTimeEdit.setMinimumDateTime(QtCore.QDateTime(2000, 1, 1, 0, 0, 0))

        self.dateTimeEdit_2.setDateTime(now)
        self.dateTimeEdit_2.setMinimumDateTime(now)

        self.dateTimeEdit_3.setDateTime(now)
        self.dateTimeEdit_3.setMinimumDateTime(now)

        self.dateTimeEdit_4.setDateTime(now)
        self.dateTimeEdit_4.setMinimumDateTime(now)

        self.dateTimeEdit_2.setStyleSheet("QDateTimeEdit::disabled {background-color: rgb(186, 189, 182);color: gray;}"
                                          "QDateTimeEdit::enabled {background-color: rgb(186, 189, 182);color: rgb(0, 0, 0);}")
        self.dateTimeEdit_3.setStyleSheet("QDateTimeEdit::disabled {background-color: rgb(186, 189, 182);color: gray;}"
                                          "QDateTimeEdit::enabled {background-color: rgb(186, 189, 182);color: rgb(0, 0, 0);}")
        self.dateTimeEdit_4.setStyleSheet("QDateTimeEdit::disabled {background-color: rgb(186, 189, 182);color: gray;}"
                                          "QDateTimeEdit::enabled {background-color: rgb(186, 189, 182);color: rgb(0, 0, 0);}")
        self.dateTimeEdit.setStyleSheet("QDateTimeEdit::disabled {background-color: rgb(186, 189, 182);color: gray;}"
                                        "QDateTimeEdit::enabled {background-color: rgb(186, 189, 182);color: rgb(0, 0, 0);}")

        regex = QtCore.QRegExp("[a-zA-Z ]+")
        validator = QtGui.QRegExpValidator(regex)
        self.lineEdit_7.setValidator(validator)

        self.tableWidget.setColumnCount(4)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_2.setColumnCount(4)
        header = self.tableWidget_2.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_3.setColumnCount(2)
        header = self.tableWidget_3.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_4.setColumnCount(3)
        header = self.tableWidget_4.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        self.tableWidget_5.setColumnCount(6)
        header = self.tableWidget_5.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)

        self.onlyDouble = QDoubleValidator()
        self.lineEdit_2.setValidator(self.onlyDouble)

        self.onlyDouble = QDoubleValidator()
        self.lineEdit_15.setValidator(self.onlyDouble)

        self.onlyDouble = QDoubleValidator()
        self.lineEdit_12.setValidator(self.onlyDouble)

        self.onlyDouble = QDoubleValidator()
        self.lineEdit_16.setValidator(self.onlyDouble)

        # Tabwidget
        self.tableWidget.setShowGrid(False)
        # self.tableWidget.verticalHeader().setVisible(False)

        self.tableWidget_2.setShowGrid(False)
        # self.tableWidget_2.verticalHeader().setVisible(False)

        self.tableWidget_3.setShowGrid(False)
        # self.tableWidget_3.verticalHeader().setVisible(False)

        self.tableWidget_4.setShowGrid(False)
        # self.tableWidget_4.verticalHeader().setVisible(False)

        self.tableWidget_5.setShowGrid(False)
        # self.tableWidget_5.verticalHeader().setVisible(False)

        self.tableWidget_6.setShowGrid(False)

        stylesheet = "QHeaderView::section{Background-color:#16A085;border-radius:5px;font: 13pt;color: beige; margin:5px}" \
                     "QTableWidget::QTableCornerButton::section {background: red;border: 2px outset red;border: 0;}" \
                     "QTableWidget::indicator:unchecked {background-color: #d7d6d5;border: 0;}" \
                     "QTableWidget {border: 0;}" \
                     "QTableWidget::item { border-radius:12px;font: 15pt;color: beige; }"

        self.tableWidget.setStyleSheet(stylesheet)
        self.tableWidget_6.setStyleSheet(stylesheet)

        stylesheet_4 = "QHeaderView::section{Background-color:#16A085;border-radius:5px;font: 13pt;color: beige; margin:5px}" \
                       "QTableWidget::QTableCornerButton::section {background: red;border: 2px outset red;border: 0;}" \
                       "QTableWidget::indicator:unchecked {background-color: #d7d6d5;border: 0;}" \
                       "QTableWidget {border: 0;}" \
                       "QTableWidget::item { border-radius:12px;font: 15pt;color: beige; }"

        self.tableWidget_4.setStyleSheet(stylesheet_4)

        stylesheet_5 = "QHeaderView::section{Background-color:#16A085;border-radius:5px;font: 13pt;color: beige; margin:5px}" \
                       "QTableWidget::QTableCornerButton::section {background: red;border: 2px outset red;border: 0;}" \
                       "QTableWidget::indicator:unchecked {background-color: #d7d6d5;border: 0;}" \
                       "QTableWidget {border: 0;}" \
                       "QTableWidget::item { border-radius:12px;font: 15pt;color: beige; }"

        self.tableWidget_5.setStyleSheet(stylesheet_5)

        stylesheet = "QHeaderView::section{Background-color:#16A085;border-radius:5px;font: 13pt;color: beige; margin:5px}" \
                     "QTableWidget::QTableCornerButton::section {background: red;border: 2px outset red;border: 0;}" \
                     "QTableWidget::indicator:unchecked {background-color: #d7d6d5;border: 0;}" \
                     "QTableWidget {border: 0;}" \
                     "QTableWidget::item { border-radius:12px;font: 15pt;color: beige; }"

        self.tableWidget_3.setStyleSheet(stylesheet)

        stylesheet_ = "QHeaderView::section{Background-color:#16A085;border-radius:5px;font: 13pt;color: beige; margin:5px}" \
                      "QTableWidget::QTableCornerButton::section {background: red;border: 2px outset red;border: 0;}" \
                      "QTableWidget::indicator:unchecked {background-color: #d7d6d5;border: 0;}" \
                      "QTableWidget {border: 0;}" \
                      "QTableWidget::item { border-radius:12px;font: 15pt;color: beige; }"

        self.tableWidget_2.setStyleSheet(stylesheet_)

        self.tabWidget_3.setTabIcon(0, QtGui.QIcon(self.icon_path + '/chain_icon.png'))
        self.tabWidget_3.setTabIcon(1, QtGui.QIcon(self.icon_path + '/wallet_icon.png'))
        self.tabWidget_3.setTabIcon(2, QtGui.QIcon(self.icon_path + '/credit.png'))
        self.tabWidget_3.setTabIcon(3, QtGui.QIcon(self.icon_path + '/loop_icon.png'))
        self.tabWidget_3.setTabIcon(4, QtGui.QIcon(self.icon_path + '/persons.png'))
        self.tabWidget_3.setTabIcon(5, QtGui.QIcon(self.icon_path + '/setting_icon.png'))
        self.tabWidget_3.setTabIcon(6, QtGui.QIcon(self.icon_path + '/exit_icon.png'))
        self.tabWidget_3.setTabIcon(7, QtGui.QIcon(self.icon_path + '/log_icon.png'))

        self.tabWidget.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tabWidget_3.tabBar().setStyleSheet('''
                                        QTabBar { font: bold 15pt; font-family: Courier; color: rgb(238, 238, 236); }
                                        QTabBar::tab { border-radius: 10px;   margin: 5px; }
                                        QTabBar::tab:selected {background-color:  #2C3E50; color: white}
                                        QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;}
                                        QTabBar::tab:hover {background-color : #16A085;}
                                    ''')
        self.tabWidget_3.setStyleSheet('''
                                         QTabBar { font: bold 12pt; font-family: Courier; color: rgb(238, 238, 236); }
                                         QTabBar::tab { border-radius: 10px;   }
                                         QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;}
                                         QTabWidget::pane {top: 0px;}
                                         QTabWidget::pane { border: 0; }
        
                                         QTabBar::tab:selected {background-color:  #2C3E50; color: white}
                                         QTabBar::tab:hover {background-color : #16A085;}
                                     ''')

        self.tabWidget_4.setStyleSheet('''
                                QTabWidget { background: transparent;  }
                                QTabWidget::pane {border: 0px solid lightgray;border-radius: 20px;top:-1px;}
                                QTabBar::tab {border: 1px solid beige;padding: 15px;}
                                QTabBar::tab:selected {}''')

        self.tabWidget_4.tabBar().setStyleSheet('''
                                        QTabBar { font: 12pt; font-family: Courier; color: rgb(238, 238, 236); }
                                        QTabBar::tab { border-radius: 10px; }
                                        QTabBar::tab:hover {background-color:  #2C3E50; color: white}
                                        QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;}
                                        QTabBar::tab:selected {background-color : #16A085;}
                                    ''')

        self.tabWidget_3.setIconSize(QtCore.QSize(50, 50))
        # Button
        self.pushButton_21.setIcon(QIcon(self.icon_path + "/connect_icon.png"))
        self.pushButton_21.setIconSize(QtCore.QSize(50, 50))

        self.pushButton_4.setText("")

        self.pushButton_17.setIcon(QIcon(self.icon_path + "/start_icon.png"))
        self.pushButton_17.setIconSize(QtCore.QSize(50, 50))

        self.pushButton_11.setIcon(QIcon(self.icon_path + "/stop_icon.png"))
        self.pushButton_11.setIconSize(QtCore.QSize(60, 60))


        self.icon_path = self.icon_path.replace("\\", "/")

        self.pushButton_31.setStyleSheet("QPushButton          {image: url(" + self.icon_path + "/search_icon.png); border: 0; width: 40px; height: 40px;}"\
                                        "QPushButton::hover   {image: url(" + self.icon_path + "/search_hover.png);border:0px}"\
                                        "QPushButton::pressed {image: url(" + self.icon_path + "/search_press.png);border:0px}")
        self.pushButton_33.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/search_icon.png); border: 0; width: 40px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/search_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/search_press.png);border:0px}")
        self.pushButton_43.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/search_icon.png); border: 0; width: 40px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/search_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/search_press.png);border:0px}")
        self.pushButton_14.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/copy_key_icon.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/copy_key_icon_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/copy_key_icon_press.png);border:0px}")
        self.pushButton_7.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/copy_wallet_icon_.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/copy_wallet_icon_hover_.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/copy_wallet_icon_press_.png);border:0px}")
        self.pushButton_39.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/copy_wallet_icon_.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/copy_wallet_icon_hover_.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/copy_wallet_icon_press_.png);border:0px}")
        self.pushButton_40.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/copy_key_icon.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/copy_key_icon_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/copy_key_icon_press.png);border:0px}")
        self.pushButton_4.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/exit_icon_reg.png);border:0px; width: 7px; height: 7px;border-radius: 200px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/exit_icon_hoever.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/exit_icon_press.png);border:0px}")
        self.pushButton_13.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/coin_lock_icon.png); border: 0; width: 10px; height: 10px;}"
                                                                   "QPushButton::hover   {image: url(" + self.icon_path + "/coin_lock_icon_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/coin_lock_icon_press.png);border:0px}")
        self.pushButton_20.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/coin_unlock_icon.png); border: 0; width: 10px; height: 10px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/coin_unlock_icon_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/coin_unlock_icon_press.png);border:0px}")
        self.pushButton_18.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/send_coin_icon.png); border: 0; width: 20px; height: 20px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/send_coin_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/send_coin_press.png);border:0px}")

        self.pushButton_19.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/copy_wallet_icon.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/copy_wallet_icon_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/copy_wallet_icon_press.png);border:0px}")

        self.pushButton_27.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/request_credit.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/request_credit_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/request_credit_press.png);border:0px}")

        self.pushButton_32.setStyleSheet(
            "QPushButton          {image: url(" + self.icon_path + "/request_credit.png); border: 0; width: 30px; height: 30px;}"
                                                                    "QPushButton::hover   {image: url(" + self.icon_path + "/request_credit_hover.png);border:0px}"
                                                                                                                          "QPushButton::pressed {image: url(" + self.icon_path + "/request_credit_press.png);border:0px}")

        self.pushButton_15.setIcon(QIcon(self.icon_path + "/circle-inactive.png"))
        self.pushButton_15.setStyleSheet("border-color: red;border-radius: 10px")

        self.pushButton_16.setIcon(QIcon(self.icon_path + "/circle-inactive.png"))
        self.pushButton_16.setStyleSheet("border-color: red;border-radius: 10px")

        self.pushButton_3.setStyleSheet("border-color: red;border-radius: 10px")

        self.pushButton_22.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_36.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")
        self.pushButton_37.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")
        self.pushButton_38.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")
        self.pushButton_45.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_48.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_46.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")
        self.pushButton_2.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color:  #5DADE2;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")
        self.pushButton_12.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color:  #5DADE2;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_8.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_8.setIconSize(QtCore.QSize(40, 400))

        self.pushButton_8.setStyleSheet("\
                    QPushButton          {color: beige; border: solid; border-style: outset; border-color: #5DADE2 ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_29.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_29.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_29.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: bold 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 1px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 1px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 1px; border-radius: 10px;}\
                    ")

        self.pushButton_42.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_42.setIconSize(QtCore.QSize(30, 30))
        self.pushButton_42.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 1px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 1px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 1px; border-radius: 10px;}\
                    ")

        self.pushButton_30.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_30.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_30.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: bold 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 1px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 1px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 1px; border-radius: 10px;}\
                    ")
        self.pushButton_34.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_34.setIconSize(QtCore.QSize(50, 50))
        self.pushButton_34.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: bold 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 1px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 1px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 1px; border-radius: 10px;}\
                    ")

        self.pushButton_35.setIcon(QIcon(self.icon_path + "/refresh_icon.png"))
        self.pushButton_35.setIconSize(QtCore.QSize(20, 20))
        self.pushButton_35.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_41.setStyleSheet("\
                            QPushButton          {background-color: #16A085 ;font: 15pt;color: beige; border: solid; border-style: outset; border-color: #5DADE2;border-width: 1px; border-radius: 10px;}\
                            QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 1px; border-radius: 10px;}\
                            QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 1px; border-radius: 10px;}\
                            ")

        self.pushButton_10.setStyleSheet('''
                    QPushButton          {background-color: #16A085 ;border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    QPushButton::hover   {border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                    QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    ''')

        self.pushButton_44.setStyleSheet('''
                    QPushButton          {background-color: #16A085 ;border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    QPushButton::hover   {border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                    QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    ''')

        self.pushButton_47.setStyleSheet('''
                    QPushButton          {background-color: #16A085 ;border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    QPushButton::hover   {border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                    QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    ''')

        self.pushButton_21.setStyleSheet("\
                    QPushButton          {background-color: #16A085 ;font: bold 15pt;color: beige; border: solid; border-style: outset; border-color:  #5DADE2;border-width: 2px; border-radius: 10px;}\
                    QPushButton::hover   {color: lawngreen; border: solid; border-style: outset; border-color: forestgreen ;border-width: 2px; border-radius: 10px;}\
                    QPushButton::pressed {color: lawngreen; border: solid; border-style: outset; border-color: lawngreen ;border-width: 2px; border-radius: 10px;}\
                    ")

        self.pushButton_23.setStyleSheet('''
                    QPushButton          {background-color: #16A085 ;border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                    QPushButton::hover   {border-style: outset; border-color: green;border-width: 2px; border-radius: 10px; }
                    QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                    ''')

        self.pushButton_24.setStyleSheet('''
                            QPushButton          {background-color: #16A085 ;border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                            QPushButton::hover   {border-style: outset; border-color: green;border-width: 2px; border-radius: 10px; }
                            QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                            ''')
        self.pushButton_25.setStyleSheet('''
                            QPushButton          {background-color: #16A085 ;border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                            QPushButton::hover   {border-style: outset; border-color: green;border-width: 2px; border-radius: 10px; }
                            QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                            ''')
        self.pushButton_26.setStyleSheet('''
                            QPushButton          {background-color: #16A085 ;border-style: outset; border-color: blue;border-width: 2px; border-radius: 10px; }
                            QPushButton::hover   {border-style: outset; border-color: green;border-width: 2px; border-radius: 10px; }
                            QPushButton::pressed {border-style: outset; border-color: red;border-width: 2px; border-radius: 10px; }
                            ''')

        self.pushButton.setIcon(QIcon(self.icon_path + "/mcl_.png"))
        self.pushButton.setIconSize(QtCore.QSize(60, 60))
        self.pushButton.setText("")
        self.pushButton.setStyleSheet("border-color: red;border-radius: 10px")

        # Label
        # ---------------------------------------------
        self.label_20.setStyleSheet("border:0;")
        self.label_23.setStyleSheet("border:0;")
        self.label_24.setStyleSheet("border:0;")

        # Line Edit
        # ---------------------------------------------
        self.lineEdit_12.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_16.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_15.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_14.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_10.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_39.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_38.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_31.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_9.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_28.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")

        self.lineEdit_21.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_24.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_13.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_2.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_25.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")
        self.lineEdit_4.setStyleSheet("font-size: 15px;border: 1px solid #16A085; border-radius: 10px;color:white")

        self.lineEdit_31.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_32.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_33.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_36.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")

        self.lineEdit_22.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_27.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_5.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_23.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_26.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_34.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")
        self.lineEdit_35.setStyleSheet("font-size: 15px;border: 1px solid blue; border-radius: 10px;color:white")

        self.lineEdit_29.setStyleSheet(
            "QLineEdit::disabled {font-size: 11px;border: 1px solid blue; border-radius: 5px;color:gray}"
            "QLineEdit::enabled {font-size: 11px;border: 1px solid #16A085; border-radius: 5px;color:white}")

        self.lineEdit_30.setStyleSheet(
            "QLineEdit::disabled {font-size: 11px;border: 1px solid blue; border-radius: 5px;color:gray}"
            "QLineEdit::enabled {font-size: 11px;border: 1px solid #16A085; border-radius: 5px;color:white}")

        self.lineEdit_6.setStyleSheet("border: 1px solid #16A085; border-radius: 10px;color:white")

        self.label_19.setStyleSheet("QLabel {font-size: 20px;background-color: #16A085; border-radius: 20px;}")

        self.label_54.setStyleSheet("QLabel {font-size: 11px; color:white}")
        self.label_55.setStyleSheet("QLabel {font-size: 11px; color:white}")
        self.label_82.setStyleSheet("QLabel {font-size: 18px; color:white}")
        self.label_85.setStyleSheet("QLabel {font-size: 18px; color:white}")

        self.label_21.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_33.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_31.setStyleSheet("QLabel {font-size: 20px; color:white}")

        self.label_46.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_47.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_48.setStyleSheet("QLabel {font-size: 20px; color:white}")

        self.label_30.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_32.setStyleSheet("QLabel {font-size: 20px; color:white}")

        self.label_34.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_22.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_41.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_42.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_49.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_51.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_43.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_53.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_44.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_7.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_17.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_67.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_68.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_69.setStyleSheet("QLabel {font-size: 20px; color:white}")
        self.label_72.setStyleSheet("QLabel {font-size: 15px; color:white}")
        self.label_73.setStyleSheet("QLabel {font-size: 15px; color:white}")
        self.label_74.setStyleSheet("QLabel {font-size: 15px; color:white}")

        self.label_28.setStyleSheet(
            "QLabel {font: medium; font-size: 25px;background-color: #16A085; border-radius: 10px;}")

        # Frame
        # ---------------------------------------------
        self.frame_2.setStyleSheet(
            "QFrame {border-style: outset;border-width: 2px;border-color: beige;border-radius: 10px;color: rgb(238, 238, 236);}")

        self.frame_16.setStyleSheet(
            '''QFrame {border-style: outset;border-width: 2px;border-color: beige;border-radius: 10px;color: rgb(238, 238, 236);}''')
        self.frame.setStyleSheet('''QFrame {border:0;}''')
        self.frame_20.setStyleSheet(
            '''QFrame {border-style: outset;border-width: 2px;border-color: beige;border-radius: 10px}''')

        self.frame_3.setStyleSheet('''
                    QFrame {border-style: outset;border-width: 2px;border-color: blue;border-radius: 30px; background:transparent; ; }
                    QLineEdit {border: 1px solid #16A085; border-radius: 10px}
        
                    ''')

        self.frame_13.setStyleSheet('''QFrame {border:0;}''')
        self.frame_21.setStyleSheet('''QFrame {border:0;}''')
        self.frame_11.setStyleSheet("border-radius: 20px; background-color: #16A085;color: rgb(238, 238, 236);")

        # Groupbox
        # ---------------------------------------------
        self.groupBox.setTitle("")
        self.groupBox.setStyleSheet("border-radius: 20px; background:transparent;  ")

        self.groupBox_10.setStyleSheet('''
                            QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 1ex;}
                            QGroupBox::title {color:white;top: -8px;left: 10px;}
                            ''')
        self.groupBox_16.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_12.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 0px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_17.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 0px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                              ''')
        self.groupBox_7.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_13.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_19.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')

        self.groupBox_14.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_15.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_11.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_5.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_6.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_2.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_8.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_9.setStyleSheet('''
                             QGroupBox {color:white;border: solid;border-width: 2px;border-color: beige;border-radius: 10px;font: 15px consolas;margin-top: 2ex;}
                             QGroupBox::title {color:white;top: -8px;left: 10px;}
                              ''')
        self.groupBox_4.setStyleSheet('''
                        QRadioButton {color:beige;font: 20px consolas;}
                        QRadioButton::indicator {width: 25px; height: 25px;color:beige;}
                        QGroupBox {border:0;}
                        ''')
        self.comboBox_2.setStyleSheet('''
                        QComboBox::down-arrow{border: solid;border-width: 5px;border-color: #16A085;border-radius: 0px}
                        QComboBox{color:beige;border: solid;border-style: outset;border-width: 1px;border-color: #16A085;
                                 border-top-left-radius : 0px;
                                 border-top-right-radius : 0px;
                                 border-bottom-left-radius:0px;
                                 border-bottom-right-radius : 0px;}                        
                        QListView{background-color: teal;color:white;border: solid;border-style: outset;border-width: 2px;border-color: beige;border-radius: 5px;}
                                 ''')
        self.stackedWidget.setStyleSheet('''QFrame {border:0;}''')
        self.stackedWidget_2.setStyleSheet('''
                    QStackedWidget > QWidget{border-radius: 10px;}
                    QFrame {border:0;}''')

        self.frame_28.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color:  #021C1E}")
        self.frame_37.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color:  #021C1E}")
        self.frame_39.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color: #021C1E; }")
        self.frame_40.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color: #021C1E; }")
        self.frame_41.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color: #021C1E; }")
        self.frame_38.setStyleSheet(
            "QFrame {border-style: outset;border-width: 0px;border-color: beige;border-radius: 10px; background-color: #021C1E; }")

        #Here we hide the button with designer. Then we create our own button.
        self.pushButton_6.setVisible(False)
        self.pushButton_9.setVisible(False)

        from SwitchButton import MySwitch
        self.pushButton_6 = MySwitch(self.frame_18)
        self.pushButton_6.setObjectName("pushButton_6")
        self.horizontalLayout_12.addWidget(self.pushButton_6)

        self.pushButton_9 = MySwitch(self.frame_19)
        self.pushButton_9.setObjectName("pushButton_9")
        self.horizontalLayout_13.addWidget(self.pushButton_9)

        self.checkBox.setStyleSheet("QCheckBox {font-size: 15px; color:white}"
                                    "QCheckBox::indicator:pressed {background-color : lightgreen;}")