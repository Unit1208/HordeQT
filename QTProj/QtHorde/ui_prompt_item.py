# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'prompt_item.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(600, 204)
        self.horizontalLayoutWidget = QWidget(Form)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(10, 160, 581, 41))
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.copyButton = QPushButton(self.horizontalLayoutWidget)
        self.copyButton.setObjectName(u"copyButton")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyButton.setIcon(icon)

        self.horizontalLayout.addWidget(self.copyButton)

        self.useButton = QPushButton(self.horizontalLayoutWidget)
        self.useButton.setObjectName(u"useButton")
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ContactNew))
        self.useButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.useButton)

        self.deleteButton = QPushButton(self.horizontalLayoutWidget)
        self.deleteButton.setObjectName(u"deleteButton")
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.deleteButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.deleteButton)

        self.formLayoutWidget = QWidget(Form)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(10, 0, 581, 161))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.fieldLabel = QLabel(self.formLayoutWidget)
        self.fieldLabel.setObjectName(u"fieldLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.fieldLabel)

        self.fieldLineEdit = QLineEdit(self.formLayoutWidget)
        self.fieldLineEdit.setObjectName(u"fieldLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.fieldLineEdit)

        self.valueLabel = QLabel(self.formLayoutWidget)
        self.valueLabel.setObjectName(u"valueLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.valueLabel)

        self.plainTextEdit = QPlainTextEdit(self.formLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.plainTextEdit)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.copyButton.setText(QCoreApplication.translate("Form", u"Copy", None))
        self.useButton.setText(QCoreApplication.translate("Form", u"Use", None))
        self.deleteButton.setText(QCoreApplication.translate("Form", u"Delete", None))
        self.fieldLabel.setText(QCoreApplication.translate("Form", u"Field", None))
        self.valueLabel.setText(QCoreApplication.translate("Form", u"Value", None))
    # retranslateUi

