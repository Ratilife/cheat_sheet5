# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'start_panel_buttons_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHeaderView, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget)

class StartPanelButtonsWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(461, 278)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_2 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.table_buttons = QTableWidget(self.centralwidget)
        if (self.table_buttons.columnCount() < 2):
            self.table_buttons.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.table_buttons.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.table_buttons.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.table_buttons.setObjectName(u"table_buttons")

        self.verticalLayout_2.addWidget(self.table_buttons)

        self.but_delete_selected_line = QPushButton(self.centralwidget)
        self.but_delete_selected_line.setObjectName(u"but_delete_selected_line")

        self.verticalLayout_2.addWidget(self.but_delete_selected_line)

        self.but_close_window = QPushButton(self.centralwidget)
        self.but_close_window.setObjectName(u"but_close_window")

        self.verticalLayout_2.addWidget(self.but_close_window)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 461, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041a\u043d\u043e\u043f\u043a\u0438 \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u043e\u0439 \u043f\u0430\u043d\u0435\u043b\u0438", None))
        ___qtablewidgetitem = self.table_buttons.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"column_name", None));
        ___qtablewidgetitem1 = self.table_buttons.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"path_to_program_file", None));
        self.but_delete_selected_line.setText(QCoreApplication.translate("MainWindow", u"\u0423\u0434\u0430\u043b\u0438\u0442\u044c \u0441\u0442\u0440\u043e\u043a\u0443", None))
        self.but_close_window.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043a\u0440\u044b\u0442\u044c", None))
    # retranslateUi

