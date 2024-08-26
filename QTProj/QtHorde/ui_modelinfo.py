# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modelinfo.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTextEdit, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(664, 448)
        self.formLayoutWidget = QWidget(Dialog)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(-1, -1, 671, 411))
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.nameLabel = QLabel(self.formLayoutWidget)
        self.nameLabel.setObjectName(u"nameLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.nameLabel)

        self.nameLineEdit = QLineEdit(self.formLayoutWidget)
        self.nameLineEdit.setObjectName(u"nameLineEdit")
        self.nameLineEdit.setEnabled(False)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.nameLineEdit)

        self.baselineLabel = QLabel(self.formLayoutWidget)
        self.baselineLabel.setObjectName(u"baselineLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.baselineLabel)

        self.baselineLineEdit = QLineEdit(self.formLayoutWidget)
        self.baselineLineEdit.setObjectName(u"baselineLineEdit")
        self.baselineLineEdit.setEnabled(False)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.baselineLineEdit)

        self.inpaintingLabel = QLabel(self.formLayoutWidget)
        self.inpaintingLabel.setObjectName(u"inpaintingLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.inpaintingLabel)

        self.inpaintingCheckBox = QCheckBox(self.formLayoutWidget)
        self.inpaintingCheckBox.setObjectName(u"inpaintingCheckBox")
        self.inpaintingCheckBox.setEnabled(False)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.inpaintingCheckBox)

        self.versionLabel = QLabel(self.formLayoutWidget)
        self.versionLabel.setObjectName(u"versionLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.versionLabel)

        self.versionLineEdit = QLineEdit(self.formLayoutWidget)
        self.versionLineEdit.setObjectName(u"versionLineEdit")
        self.versionLineEdit.setEnabled(False)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.versionLineEdit)

        self.styleLabel = QLabel(self.formLayoutWidget)
        self.styleLabel.setObjectName(u"styleLabel")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.styleLabel)

        self.styleLineEdit = QLineEdit(self.formLayoutWidget)
        self.styleLineEdit.setObjectName(u"styleLineEdit")
        self.styleLineEdit.setEnabled(False)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.styleLineEdit)

        self.nsfwLabel = QLabel(self.formLayoutWidget)
        self.nsfwLabel.setObjectName(u"nsfwLabel")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.nsfwLabel)

        self.nsfwCheckBox = QCheckBox(self.formLayoutWidget)
        self.nsfwCheckBox.setObjectName(u"nsfwCheckBox")
        self.nsfwCheckBox.setEnabled(False)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.nsfwCheckBox)

        self.unsupportedFeaturesLabel = QLabel(self.formLayoutWidget)
        self.unsupportedFeaturesLabel.setObjectName(u"unsupportedFeaturesLabel")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.unsupportedFeaturesLabel)

        self.requirementsLabel = QLabel(self.formLayoutWidget)
        self.requirementsLabel.setObjectName(u"requirementsLabel")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.requirementsLabel)

        self.descriptionLabel = QLabel(self.formLayoutWidget)
        self.descriptionLabel.setObjectName(u"descriptionLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.descriptionLabel)

        self.descriptionBox = QTextEdit(self.formLayoutWidget)
        self.descriptionBox.setObjectName(u"descriptionBox")
        self.descriptionBox.setEnabled(False)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.descriptionBox)

        self.unsupportedFeaturesLineEdit = QLineEdit(self.formLayoutWidget)
        self.unsupportedFeaturesLineEdit.setObjectName(u"unsupportedFeaturesLineEdit")
        self.unsupportedFeaturesLineEdit.setEnabled(False)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.unsupportedFeaturesLineEdit)

        self.requirementsLineEdit = QLineEdit(self.formLayoutWidget)
        self.requirementsLineEdit.setObjectName(u"requirementsLineEdit")
        self.requirementsLineEdit.setEnabled(False)

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.requirementsLineEdit)

        self.widget = QWidget(Dialog)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(0, 420, 661, 26))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.openHomepage = QPushButton(self.widget)
        self.openHomepage.setObjectName(u"openHomepage")

        self.horizontalLayout.addWidget(self.openHomepage)

        self.useAndCloseButton = QPushButton(self.widget)
        self.useAndCloseButton.setObjectName(u"useAndCloseButton")

        self.horizontalLayout.addWidget(self.useAndCloseButton)

        self.closeButton = QPushButton(self.widget)
        self.closeButton.setObjectName(u"closeButton")

        self.horizontalLayout.addWidget(self.closeButton)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.nameLabel.setText(QCoreApplication.translate("Dialog", u"Name", None))
        self.baselineLabel.setText(QCoreApplication.translate("Dialog", u"Baseline", None))
        self.inpaintingLabel.setText(QCoreApplication.translate("Dialog", u"Inpainting", None))
        self.inpaintingCheckBox.setText("")
        self.versionLabel.setText(QCoreApplication.translate("Dialog", u"Version", None))
        self.styleLabel.setText(QCoreApplication.translate("Dialog", u"Style", None))
        self.nsfwLabel.setText(QCoreApplication.translate("Dialog", u"NSFW", None))
        self.unsupportedFeaturesLabel.setText(QCoreApplication.translate("Dialog", u"Unsupported Features", None))
        self.requirementsLabel.setText(QCoreApplication.translate("Dialog", u"Requirements", None))
        self.descriptionLabel.setText(QCoreApplication.translate("Dialog", u"Description", None))
        self.openHomepage.setText(QCoreApplication.translate("Dialog", u"Open Model Homepage", None))
        self.useAndCloseButton.setText(QCoreApplication.translate("Dialog", u"Use Model", None))
        self.closeButton.setText(QCoreApplication.translate("Dialog", u"Close", None))
    # retranslateUi

