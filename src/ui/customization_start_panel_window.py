# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'customization_start_panel_window.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLineEdit, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class CostStartPanelWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(528, 277)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.path_root_folder = QLineEdit(self.centralwidget)
        self.path_root_folder.setObjectName(u"path_root_folder")

        self.verticalLayout.addWidget(self.path_root_folder)

        self.but_dialog_create_folder = QPushButton(self.centralwidget)
        self.but_dialog_create_folder.setObjectName(u"but_dialog_create_folder")

        self.verticalLayout.addWidget(self.but_dialog_create_folder)

        self.but_create_bookmarks = QPushButton(self.centralwidget)
        self.but_create_bookmarks.setObjectName(u"but_create_bookmarks")

        self.verticalLayout.addWidget(self.but_create_bookmarks)

        self.but_clear_user_button = QPushButton(self.centralwidget)
        self.but_clear_user_button.setObjectName(u"but_clear_user_button")

        self.verticalLayout.addWidget(self.but_clear_user_button)

        self.but_contents_start_panel = QPushButton(self.centralwidget)
        self.but_contents_start_panel.setObjectName(u"but_contents_start_panel")

        self.verticalLayout.addWidget(self.but_contents_start_panel)

        self.but_contents_tree_files = QPushButton(self.centralwidget)
        self.but_contents_tree_files.setObjectName(u"but_contents_tree_files")

        self.verticalLayout.addWidget(self.but_contents_tree_files)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.but_close_save_minutes = QPushButton(self.centralwidget)
        self.but_close_save_minutes.setObjectName(u"but_close_save_minutes")

        self.horizontalLayout_2.addWidget(self.but_close_save_minutes)

        self.but_close_window = QPushButton(self.centralwidget)
        self.but_close_window.setObjectName(u"but_close_window")

        self.horizontalLayout_2.addWidget(self.but_close_window)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 528, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041c\u0435\u043d\u0435\u0434\u0436\u0435\u0440 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b \u043f\u0440\u043e\u0435\u043a\u0442\u0430", None))
        self.but_dialog_create_folder.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u043a\u043e\u0440\u043d\u0435\u0432\u0443\u044e \u043f\u0430\u043f\u043a\u0443", None))
        self.but_create_bookmarks.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0437\u0434\u0430\u0442\u044c \u0437\u0430\u043a\u043b\u0430\u0434\u043a\u0438", None))
        self.but_clear_user_button.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u0443\u044e \u043f\u0430\u043d\u0435\u043b\u044c", None))
        self.but_contents_start_panel.setText(QCoreApplication.translate("MainWindow", u"\u041a\u043d\u043e\u043f\u043a\u0438 \u0441\u0442\u0430\u0440\u0442\u043e\u0432\u043e\u0439 \u043f\u0430\u043d\u0435\u043b\u0438", None))
        self.but_contents_tree_files.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0434\u0435\u0440\u0436\u0430\u043d\u0438\u0435 JSON \u0434\u043b\u044f st \u0438 md \u0444\u0430\u0439\u043b\u043e\u0432", None))
        self.but_close_save_minutes.setText(QCoreApplication.translate("MainWindow", u"\u0421\u043e\u0445\u0440\u0430\u043d\u0438\u0442\u044c \u0438\u0437\u043c\u0438\u043d\u0435\u043d\u0438\u044f \u0438 \u0437\u0430\u043a\u0440\u044b\u0442\u044c", None))
        self.but_close_window.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0430\u043a\u0440\u044b\u0442\u044c", None))
    # retranslateUi

