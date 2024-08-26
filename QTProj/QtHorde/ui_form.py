# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractSpinBox, QApplication, QCheckBox, QComboBox,
    QDoubleSpinBox, QFormLayout, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QProgressBar,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QTextEdit, QTreeView, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(792, 879)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabBarAutoHide(False)
        self.create_tab = QWidget()
        self.create_tab.setObjectName(u"create_tab")
        self.PromptBox = QTextEdit(self.create_tab)
        self.PromptBox.setObjectName(u"PromptBox")
        self.PromptBox.setGeometry(QRect(20, 30, 731, 70))
        self.PromptBox.setTabChangesFocus(True)
        self.NegativePromptBox = QTextEdit(self.create_tab)
        self.NegativePromptBox.setObjectName(u"NegativePromptBox")
        self.NegativePromptBox.setGeometry(QRect(20, 110, 731, 70))
        self.NegativePromptBox.setTabChangesFocus(True)
        self.frame = QFrame(self.create_tab)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(20, 220, 731, 531))
        self.scrollArea = QScrollArea(self.frame)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setGeometry(QRect(0, 10, 731, 541))
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 729, 539))
        self.gridLayoutWidget = QWidget(self.scrollAreaWidgetContents)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(0, 0, 721, 511))
        self.formLayout = QFormLayout(self.gridLayoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFormAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.formLayout.setVerticalSpacing(6)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.imagesLabel = QLabel(self.gridLayoutWidget)
        self.imagesLabel.setObjectName(u"imagesLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.imagesLabel)

        self.imagesSpinBox = QSpinBox(self.gridLayoutWidget)
        self.imagesSpinBox.setObjectName(u"imagesSpinBox")
        self.imagesSpinBox.setMinimum(1)
        self.imagesSpinBox.setMaximum(50)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.imagesSpinBox)

        self.stepsLabel = QLabel(self.gridLayoutWidget)
        self.stepsLabel.setObjectName(u"stepsLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.stepsLabel)

        self.stepsSpinBox = QSpinBox(self.gridLayoutWidget)
        self.stepsSpinBox.setObjectName(u"stepsSpinBox")
        self.stepsSpinBox.setMinimum(1)
        self.stepsSpinBox.setMaximum(150)
        self.stepsSpinBox.setValue(20)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.stepsSpinBox)

        self.modelLabel = QLabel(self.gridLayoutWidget)
        self.modelLabel.setObjectName(u"modelLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.modelLabel)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.modelComboBox = QComboBox(self.gridLayoutWidget)
        self.modelComboBox.addItem("")
        self.modelComboBox.setObjectName(u"modelComboBox")
        self.modelComboBox.setEnabled(True)
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.modelComboBox.sizePolicy().hasHeightForWidth())
        self.modelComboBox.setSizePolicy(sizePolicy1)
        self.modelComboBox.setEditable(True)

        self.horizontalLayout_2.addWidget(self.modelComboBox)

        self.modelDetailsButton = QPushButton(self.gridLayoutWidget)
        self.modelDetailsButton.setObjectName(u"modelDetailsButton")
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemSearch))
        self.modelDetailsButton.setIcon(icon)
        self.modelDetailsButton.setFlat(False)

        self.horizontalLayout_2.addWidget(self.modelDetailsButton)


        self.formLayout.setLayout(2, QFormLayout.FieldRole, self.horizontalLayout_2)

        self.presetLabel = QLabel(self.gridLayoutWidget)
        self.presetLabel.setObjectName(u"presetLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.presetLabel)

        self.presetComboBox = QComboBox(self.gridLayoutWidget)
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.addItem("")
        self.presetComboBox.setObjectName(u"presetComboBox")
        self.presetComboBox.setEditable(False)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.presetComboBox)

        self.widthLabel = QLabel(self.gridLayoutWidget)
        self.widthLabel.setObjectName(u"widthLabel")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.widthLabel)

        self.widthSpinBox = QSpinBox(self.gridLayoutWidget)
        self.widthSpinBox.setObjectName(u"widthSpinBox")
        self.widthSpinBox.setMinimum(64)
        self.widthSpinBox.setMaximum(3072)
        self.widthSpinBox.setSingleStep(64)
        self.widthSpinBox.setValue(768)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.widthSpinBox)

        self.heightLabel = QLabel(self.gridLayoutWidget)
        self.heightLabel.setObjectName(u"heightLabel")

        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.heightLabel)

        self.heightSpinBox = QSpinBox(self.gridLayoutWidget)
        self.heightSpinBox.setObjectName(u"heightSpinBox")
        self.heightSpinBox.setMinimum(64)
        self.heightSpinBox.setMaximum(3072)
        self.heightSpinBox.setSingleStep(64)
        self.heightSpinBox.setValue(1024)

        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.heightSpinBox)

        self.samplerLabel = QLabel(self.gridLayoutWidget)
        self.samplerLabel.setObjectName(u"samplerLabel")

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.samplerLabel)

        self.samplerComboBox = QComboBox(self.gridLayoutWidget)
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.addItem("")
        self.samplerComboBox.setObjectName(u"samplerComboBox")

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.samplerComboBox)

        self.seedLabel = QLabel(self.gridLayoutWidget)
        self.seedLabel.setObjectName(u"seedLabel")

        self.formLayout.setWidget(7, QFormLayout.LabelRole, self.seedLabel)

        self.seedSpinBox = QSpinBox(self.gridLayoutWidget)
        self.seedSpinBox.setObjectName(u"seedSpinBox")
        self.seedSpinBox.setMaximum(2147483647)
        self.seedSpinBox.setDisplayIntegerBase(10)

        self.formLayout.setWidget(7, QFormLayout.FieldRole, self.seedSpinBox)

        self.guidenceLabel = QLabel(self.gridLayoutWidget)
        self.guidenceLabel.setObjectName(u"guidenceLabel")

        self.formLayout.setWidget(8, QFormLayout.LabelRole, self.guidenceLabel)

        self.guidenceDoubleSpinBox = QDoubleSpinBox(self.gridLayoutWidget)
        self.guidenceDoubleSpinBox.setObjectName(u"guidenceDoubleSpinBox")
        self.guidenceDoubleSpinBox.setDecimals(1)
        self.guidenceDoubleSpinBox.setMinimum(0.000000000000000)
        self.guidenceDoubleSpinBox.setMaximum(100.000000000000000)
        self.guidenceDoubleSpinBox.setSingleStep(0.500000000000000)
        self.guidenceDoubleSpinBox.setValue(5.000000000000000)

        self.formLayout.setWidget(8, QFormLayout.FieldRole, self.guidenceDoubleSpinBox)

        self.clipSkipLabel = QLabel(self.gridLayoutWidget)
        self.clipSkipLabel.setObjectName(u"clipSkipLabel")

        self.formLayout.setWidget(9, QFormLayout.LabelRole, self.clipSkipLabel)

        self.clipSkipSpinBox = QSpinBox(self.gridLayoutWidget)
        self.clipSkipSpinBox.setObjectName(u"clipSkipSpinBox")
        self.clipSkipSpinBox.setMinimum(1)
        self.clipSkipSpinBox.setMaximum(12)

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.clipSkipSpinBox)

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.GenerateButton = QPushButton(self.create_tab)
        self.GenerateButton.setObjectName(u"GenerateButton")
        self.GenerateButton.setGeometry(QRect(600, 190, 151, 31))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.InsertImage))
        self.GenerateButton.setIcon(icon1)
        self.horizontalLayoutWidget = QWidget(self.create_tab)
        self.horizontalLayoutWidget.setObjectName(u"horizontalLayoutWidget")
        self.horizontalLayoutWidget.setGeometry(QRect(20, 769, 721, 41))
        self.horizontalLayout_3 = QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.progressBar = QProgressBar(self.horizontalLayoutWidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)
        self.progressBar.setInvertedAppearance(False)

        self.horizontalLayout_3.addWidget(self.progressBar)

        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.tabWidget.addTab(self.create_tab, icon2, "")
        self.curr_items_tab = QWidget()
        self.curr_items_tab.setObjectName(u"curr_items_tab")
        self.groupBox_2 = QGroupBox(self.curr_items_tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setGeometry(QRect(10, 30, 761, 771))
        self.tableWidget = QTableWidget(self.groupBox_2)
        if (self.tableWidget.columnCount() < 5):
            self.tableWidget.setColumnCount(5)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        if (self.tableWidget.rowCount() < 1):
            self.tableWidget.setRowCount(1)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, __qtablewidgetitem5)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setGeometry(QRect(0, 0, 771, 771))
        self.label_4 = QLabel(self.curr_items_tab)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 10, 211, 16))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.tabWidget.addTab(self.curr_items_tab, icon3, "")
        self.gallery_tab = QWidget()
        self.gallery_tab.setObjectName(u"gallery_tab")
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentPrintPreview))
        self.tabWidget.addTab(self.gallery_tab, icon4, "")
        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")
        self.formLayoutWidget = QWidget(self.settings_tab)
        self.formLayoutWidget.setObjectName(u"formLayoutWidget")
        self.formLayoutWidget.setGeometry(QRect(0, 10, 761, 801))
        self.settingsLayout = QFormLayout(self.formLayoutWidget)
        self.settingsLayout.setObjectName(u"settingsLayout")
        self.settingsLayout.setContentsMargins(0, 0, 0, 0)
        self.APIKeyLabel = QLabel(self.formLayoutWidget)
        self.APIKeyLabel.setObjectName(u"APIKeyLabel")
        self.APIKeyLabel.setScaledContents(False)

        self.settingsLayout.setWidget(0, QFormLayout.LabelRole, self.APIKeyLabel)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.apiKeyEntry = QLineEdit(self.formLayoutWidget)
        self.apiKeyEntry.setObjectName(u"apiKeyEntry")
        self.apiKeyEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.apiKeyEntry.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.apiKeyEntry)

        self.showAPIKey = QPushButton(self.formLayoutWidget)
        self.showAPIKey.setObjectName(u"showAPIKey")
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        self.showAPIKey.setIcon(icon5)

        self.horizontalLayout.addWidget(self.showAPIKey)

        self.saveAPIkey = QPushButton(self.formLayoutWidget)
        self.saveAPIkey.setObjectName(u"saveAPIkey")
        icon6 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.saveAPIkey.setIcon(icon6)

        self.horizontalLayout.addWidget(self.saveAPIkey)

        self.copyAPIkey = QPushButton(self.formLayoutWidget)
        self.copyAPIkey.setObjectName(u"copyAPIkey")
        icon7 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyAPIkey.setIcon(icon7)
        self.copyAPIkey.setFlat(False)

        self.horizontalLayout.addWidget(self.copyAPIkey)


        self.settingsLayout.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout)

        self.NSFWLabel = QLabel(self.formLayoutWidget)
        self.NSFWLabel.setObjectName(u"NSFWLabel")

        self.settingsLayout.setWidget(1, QFormLayout.LabelRole, self.NSFWLabel)

        self.NSFWCheckBox = QCheckBox(self.formLayoutWidget)
        self.NSFWCheckBox.setObjectName(u"NSFWCheckBox")
        self.NSFWCheckBox.setTristate(False)

        self.settingsLayout.setWidget(1, QFormLayout.FieldRole, self.NSFWCheckBox)

        self.maxJobsLabel = QLabel(self.formLayoutWidget)
        self.maxJobsLabel.setObjectName(u"maxJobsLabel")

        self.settingsLayout.setWidget(2, QFormLayout.LabelRole, self.maxJobsLabel)

        self.maxJobsSpinBox = QSpinBox(self.formLayoutWidget)
        self.maxJobsSpinBox.setObjectName(u"maxJobsSpinBox")
        self.maxJobsSpinBox.setMinimum(1)
        self.maxJobsSpinBox.setMaximum(20)
        self.maxJobsSpinBox.setValue(5)

        self.settingsLayout.setWidget(2, QFormLayout.FieldRole, self.maxJobsSpinBox)

        self.tabWidget.addTab(self.settings_tab, icon3, "")
        self.userInfoPage = QWidget()
        self.userInfoPage.setObjectName(u"userInfoPage")
        self.formLayoutWidget_2 = QWidget(self.userInfoPage)
        self.formLayoutWidget_2.setObjectName(u"formLayoutWidget_2")
        self.formLayoutWidget_2.setGeometry(QRect(-1, 9, 771, 801))
        self.formLayout_2 = QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.usernameLabel = QLabel(self.formLayoutWidget_2)
        self.usernameLabel.setObjectName(u"usernameLabel")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.usernameLabel)

        self.usernameLineEdit = QLineEdit(self.formLayoutWidget_2)
        self.usernameLineEdit.setObjectName(u"usernameLineEdit")
        self.usernameLineEdit.setEnabled(True)
        self.usernameLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.usernameLineEdit)

        self.idLabel = QLabel(self.formLayoutWidget_2)
        self.idLabel.setObjectName(u"idLabel")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.idLabel)

        self.idLineEdit = QLineEdit(self.formLayoutWidget_2)
        self.idLineEdit.setObjectName(u"idLineEdit")
        self.idLineEdit.setEnabled(True)
        self.idLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.idLineEdit)

        self.kudosLabel = QLabel(self.formLayoutWidget_2)
        self.kudosLabel.setObjectName(u"kudosLabel")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.kudosLabel)

        self.kudosSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.kudosSpinBox.setObjectName(u"kudosSpinBox")
        self.kudosSpinBox.setEnabled(True)
        self.kudosSpinBox.setReadOnly(True)
        self.kudosSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.kudosSpinBox)

        self.trustedLabel = QLabel(self.formLayoutWidget_2)
        self.trustedLabel.setObjectName(u"trustedLabel")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.trustedLabel)

        self.trustedCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.trustedCheckBox.setObjectName(u"trustedCheckBox")
        self.trustedCheckBox.setEnabled(False)
        self.trustedCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.trustedCheckBox.setCheckable(True)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.trustedCheckBox)

        self.maximumConcurrencyLabel = QLabel(self.formLayoutWidget_2)
        self.maximumConcurrencyLabel.setObjectName(u"maximumConcurrencyLabel")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.maximumConcurrencyLabel)

        self.maxConcurrencySpinBox = QSpinBox(self.formLayoutWidget_2)
        self.maxConcurrencySpinBox.setObjectName(u"maxConcurrencySpinBox")
        self.maxConcurrencySpinBox.setEnabled(True)
        self.maxConcurrencySpinBox.setReadOnly(True)
        self.maxConcurrencySpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.maxConcurrencySpinBox)

        self.moderatorLabel = QLabel(self.formLayoutWidget_2)
        self.moderatorLabel.setObjectName(u"moderatorLabel")

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.moderatorLabel)

        self.moderatorCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.moderatorCheckBox.setObjectName(u"moderatorCheckBox")
        self.moderatorCheckBox.setEnabled(False)
        self.moderatorCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.moderatorCheckBox.setCheckable(True)

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.moderatorCheckBox)

        self.numberOfWorkersLabel = QLabel(self.formLayoutWidget_2)
        self.numberOfWorkersLabel.setObjectName(u"numberOfWorkersLabel")

        self.formLayout_2.setWidget(6, QFormLayout.LabelRole, self.numberOfWorkersLabel)

        self.numberOfWorkersSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.numberOfWorkersSpinBox.setObjectName(u"numberOfWorkersSpinBox")
        self.numberOfWorkersSpinBox.setEnabled(True)
        self.numberOfWorkersSpinBox.setReadOnly(True)
        self.numberOfWorkersSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.numberOfWorkersSpinBox)

        self.line_4 = QFrame(self.formLayoutWidget_2)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(7, QFormLayout.LabelRole, self.line_4)

        self.flaggedLabel = QLabel(self.formLayoutWidget_2)
        self.flaggedLabel.setObjectName(u"flaggedLabel")

        self.formLayout_2.setWidget(8, QFormLayout.LabelRole, self.flaggedLabel)

        self.flaggedCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.flaggedCheckBox.setObjectName(u"flaggedCheckBox")
        self.flaggedCheckBox.setEnabled(False)
        self.flaggedCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.flaggedCheckBox.setCheckable(True)
        self.flaggedCheckBox.setChecked(False)

        self.formLayout_2.setWidget(8, QFormLayout.FieldRole, self.flaggedCheckBox)

        self.VPNLabel = QLabel(self.formLayoutWidget_2)
        self.VPNLabel.setObjectName(u"VPNLabel")

        self.formLayout_2.setWidget(9, QFormLayout.LabelRole, self.VPNLabel)

        self.VPNCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.VPNCheckBox.setObjectName(u"VPNCheckBox")
        self.VPNCheckBox.setEnabled(False)
        self.VPNCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.VPNCheckBox.setCheckable(True)
        self.VPNCheckBox.setChecked(False)

        self.formLayout_2.setWidget(9, QFormLayout.FieldRole, self.VPNCheckBox)

        self.serviceLabel = QLabel(self.formLayoutWidget_2)
        self.serviceLabel.setObjectName(u"serviceLabel")

        self.formLayout_2.setWidget(10, QFormLayout.LabelRole, self.serviceLabel)

        self.serviceCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.serviceCheckBox.setObjectName(u"serviceCheckBox")
        self.serviceCheckBox.setEnabled(False)
        self.serviceCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.serviceCheckBox.setCheckable(True)
        self.serviceCheckBox.setChecked(False)

        self.formLayout_2.setWidget(10, QFormLayout.FieldRole, self.serviceCheckBox)

        self.educationLabel = QLabel(self.formLayoutWidget_2)
        self.educationLabel.setObjectName(u"educationLabel")

        self.formLayout_2.setWidget(11, QFormLayout.LabelRole, self.educationLabel)

        self.educationCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.educationCheckBox.setObjectName(u"educationCheckBox")
        self.educationCheckBox.setEnabled(False)
        self.educationCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.educationCheckBox.setCheckable(True)
        self.educationCheckBox.setChecked(False)

        self.formLayout_2.setWidget(11, QFormLayout.FieldRole, self.educationCheckBox)

        self.customizerLabel = QLabel(self.formLayoutWidget_2)
        self.customizerLabel.setObjectName(u"customizerLabel")

        self.formLayout_2.setWidget(12, QFormLayout.LabelRole, self.customizerLabel)

        self.customizerCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.customizerCheckBox.setObjectName(u"customizerCheckBox")
        self.customizerCheckBox.setEnabled(False)
        self.customizerCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.customizerCheckBox.setCheckable(True)
        self.customizerCheckBox.setChecked(False)

        self.formLayout_2.setWidget(12, QFormLayout.FieldRole, self.customizerCheckBox)

        self.specialLabel = QLabel(self.formLayoutWidget_2)
        self.specialLabel.setObjectName(u"specialLabel")

        self.formLayout_2.setWidget(13, QFormLayout.LabelRole, self.specialLabel)

        self.specialCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.specialCheckBox.setObjectName(u"specialCheckBox")
        self.specialCheckBox.setEnabled(False)
        self.specialCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.specialCheckBox.setCheckable(True)
        self.specialCheckBox.setChecked(False)

        self.formLayout_2.setWidget(13, QFormLayout.FieldRole, self.specialCheckBox)

        self.pseudonymousLabel = QLabel(self.formLayoutWidget_2)
        self.pseudonymousLabel.setObjectName(u"pseudonymousLabel")

        self.formLayout_2.setWidget(14, QFormLayout.LabelRole, self.pseudonymousLabel)

        self.pseudonymousCheckBox = QCheckBox(self.formLayoutWidget_2)
        self.pseudonymousCheckBox.setObjectName(u"pseudonymousCheckBox")
        self.pseudonymousCheckBox.setEnabled(False)
        self.pseudonymousCheckBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pseudonymousCheckBox.setCheckable(True)
        self.pseudonymousCheckBox.setChecked(False)

        self.formLayout_2.setWidget(14, QFormLayout.FieldRole, self.pseudonymousCheckBox)

        self.line_3 = QFrame(self.formLayoutWidget_2)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(15, QFormLayout.LabelRole, self.line_3)

        self.accountAgeLabel = QLabel(self.formLayoutWidget_2)
        self.accountAgeLabel.setObjectName(u"accountAgeLabel")

        self.formLayout_2.setWidget(16, QFormLayout.LabelRole, self.accountAgeLabel)

        self.accountAgeLineEdit = QLineEdit(self.formLayoutWidget_2)
        self.accountAgeLineEdit.setObjectName(u"accountAgeLineEdit")
        self.accountAgeLineEdit.setEnabled(True)
        self.accountAgeLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(16, QFormLayout.FieldRole, self.accountAgeLineEdit)

        self.accountCreatedLabel = QLabel(self.formLayoutWidget_2)
        self.accountCreatedLabel.setObjectName(u"accountCreatedLabel")

        self.formLayout_2.setWidget(17, QFormLayout.LabelRole, self.accountCreatedLabel)

        self.accountCreatedLineEdit = QLineEdit(self.formLayoutWidget_2)
        self.accountCreatedLineEdit.setObjectName(u"accountCreatedLineEdit")
        self.accountCreatedLineEdit.setEnabled(True)
        self.accountCreatedLineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(17, QFormLayout.FieldRole, self.accountCreatedLineEdit)

        self.line_2 = QFrame(self.formLayoutWidget_2)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(18, QFormLayout.LabelRole, self.line_2)

        self.textGeneratedLabel = QLabel(self.formLayoutWidget_2)
        self.textGeneratedLabel.setObjectName(u"textGeneratedLabel")

        self.formLayout_2.setWidget(19, QFormLayout.LabelRole, self.textGeneratedLabel)

        self.textGeneratedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.textGeneratedSpinBox.setObjectName(u"textGeneratedSpinBox")
        self.textGeneratedSpinBox.setEnabled(True)
        self.textGeneratedSpinBox.setReadOnly(True)
        self.textGeneratedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(19, QFormLayout.FieldRole, self.textGeneratedSpinBox)

        self.imageGeneratedLabel = QLabel(self.formLayoutWidget_2)
        self.imageGeneratedLabel.setObjectName(u"imageGeneratedLabel")

        self.formLayout_2.setWidget(20, QFormLayout.LabelRole, self.imageGeneratedLabel)

        self.imageGeneratedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.imageGeneratedSpinBox.setObjectName(u"imageGeneratedSpinBox")
        self.imageGeneratedSpinBox.setEnabled(True)
        self.imageGeneratedSpinBox.setReadOnly(True)
        self.imageGeneratedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(20, QFormLayout.FieldRole, self.imageGeneratedSpinBox)

        self.interrogationGeneratedLabel_2 = QLabel(self.formLayoutWidget_2)
        self.interrogationGeneratedLabel_2.setObjectName(u"interrogationGeneratedLabel_2")

        self.formLayout_2.setWidget(21, QFormLayout.LabelRole, self.interrogationGeneratedLabel_2)

        self.interrogationGeneratedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.interrogationGeneratedSpinBox.setObjectName(u"interrogationGeneratedSpinBox")
        self.interrogationGeneratedSpinBox.setEnabled(True)
        self.interrogationGeneratedSpinBox.setReadOnly(True)
        self.interrogationGeneratedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(21, QFormLayout.FieldRole, self.interrogationGeneratedSpinBox)

        self.line = QFrame(self.formLayoutWidget_2)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(22, QFormLayout.LabelRole, self.line)

        self.textRequestedLabel = QLabel(self.formLayoutWidget_2)
        self.textRequestedLabel.setObjectName(u"textRequestedLabel")

        self.formLayout_2.setWidget(23, QFormLayout.LabelRole, self.textRequestedLabel)

        self.textRequestedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.textRequestedSpinBox.setObjectName(u"textRequestedSpinBox")
        self.textRequestedSpinBox.setEnabled(True)
        self.textRequestedSpinBox.setReadOnly(True)
        self.textRequestedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(23, QFormLayout.FieldRole, self.textRequestedSpinBox)

        self.imagesRequestedLabel = QLabel(self.formLayoutWidget_2)
        self.imagesRequestedLabel.setObjectName(u"imagesRequestedLabel")

        self.formLayout_2.setWidget(24, QFormLayout.LabelRole, self.imagesRequestedLabel)

        self.imagesRequestedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.imagesRequestedSpinBox.setObjectName(u"imagesRequestedSpinBox")
        self.imagesRequestedSpinBox.setEnabled(True)
        self.imagesRequestedSpinBox.setReadOnly(True)
        self.imagesRequestedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(24, QFormLayout.FieldRole, self.imagesRequestedSpinBox)

        self.interrogationRequestedLabel = QLabel(self.formLayoutWidget_2)
        self.interrogationRequestedLabel.setObjectName(u"interrogationRequestedLabel")

        self.formLayout_2.setWidget(25, QFormLayout.LabelRole, self.interrogationRequestedLabel)

        self.interrogationRequestedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.interrogationRequestedSpinBox.setObjectName(u"interrogationRequestedSpinBox")
        self.interrogationRequestedSpinBox.setEnabled(True)
        self.interrogationRequestedSpinBox.setReadOnly(True)
        self.interrogationRequestedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(25, QFormLayout.FieldRole, self.interrogationRequestedSpinBox)

        self.tokensRequestedLabel = QLabel(self.formLayoutWidget_2)
        self.tokensRequestedLabel.setObjectName(u"tokensRequestedLabel")

        self.formLayout_2.setWidget(27, QFormLayout.LabelRole, self.tokensRequestedLabel)

        self.tokensRequestedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.tokensRequestedSpinBox.setObjectName(u"tokensRequestedSpinBox")
        self.tokensRequestedSpinBox.setEnabled(True)
        self.tokensRequestedSpinBox.setReadOnly(True)
        self.tokensRequestedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(27, QFormLayout.FieldRole, self.tokensRequestedSpinBox)

        self.megapixelstepsRequestedLabel = QLabel(self.formLayoutWidget_2)
        self.megapixelstepsRequestedLabel.setObjectName(u"megapixelstepsRequestedLabel")

        self.formLayout_2.setWidget(28, QFormLayout.LabelRole, self.megapixelstepsRequestedLabel)

        self.megapixelstepsRequestedDoubleSpinBox = QDoubleSpinBox(self.formLayoutWidget_2)
        self.megapixelstepsRequestedDoubleSpinBox.setObjectName(u"megapixelstepsRequestedDoubleSpinBox")
        self.megapixelstepsRequestedDoubleSpinBox.setEnabled(True)
        self.megapixelstepsRequestedDoubleSpinBox.setReadOnly(True)
        self.megapixelstepsRequestedDoubleSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.megapixelstepsRequestedDoubleSpinBox.setMaximum(2147483647.000000000000000)
        self.megapixelstepsRequestedDoubleSpinBox.setSingleStep(0.000000000000000)
        self.megapixelstepsRequestedDoubleSpinBox.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)

        self.formLayout_2.setWidget(28, QFormLayout.FieldRole, self.megapixelstepsRequestedDoubleSpinBox)

        self.tokensGeneratedLabel = QLabel(self.formLayoutWidget_2)
        self.tokensGeneratedLabel.setObjectName(u"tokensGeneratedLabel")

        self.formLayout_2.setWidget(30, QFormLayout.LabelRole, self.tokensGeneratedLabel)

        self.tokensGeneratedSpinBox = QSpinBox(self.formLayoutWidget_2)
        self.tokensGeneratedSpinBox.setObjectName(u"tokensGeneratedSpinBox")
        self.tokensGeneratedSpinBox.setEnabled(True)
        self.tokensGeneratedSpinBox.setReadOnly(True)
        self.tokensGeneratedSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.formLayout_2.setWidget(30, QFormLayout.FieldRole, self.tokensGeneratedSpinBox)

        self.megapixelstepsGeneratedLabel = QLabel(self.formLayoutWidget_2)
        self.megapixelstepsGeneratedLabel.setObjectName(u"megapixelstepsGeneratedLabel")

        self.formLayout_2.setWidget(31, QFormLayout.LabelRole, self.megapixelstepsGeneratedLabel)

        self.megapixelstepsGeneratedDoubleSpinBox = QDoubleSpinBox(self.formLayoutWidget_2)
        self.megapixelstepsGeneratedDoubleSpinBox.setObjectName(u"megapixelstepsGeneratedDoubleSpinBox")
        self.megapixelstepsGeneratedDoubleSpinBox.setEnabled(True)
        self.megapixelstepsGeneratedDoubleSpinBox.setReadOnly(True)
        self.megapixelstepsGeneratedDoubleSpinBox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.megapixelstepsGeneratedDoubleSpinBox.setMaximum(2147483647.000000000000000)
        self.megapixelstepsGeneratedDoubleSpinBox.setSingleStep(0.000000000000000)
        self.megapixelstepsGeneratedDoubleSpinBox.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)

        self.formLayout_2.setWidget(31, QFormLayout.FieldRole, self.megapixelstepsGeneratedDoubleSpinBox)

        self.line_5 = QFrame(self.formLayoutWidget_2)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(29, QFormLayout.LabelRole, self.line_5)

        self.line_6 = QFrame(self.formLayoutWidget_2)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.Shape.HLine)
        self.line_6.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(26, QFormLayout.LabelRole, self.line_6)

        icon8 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.UserOffline))
        self.tabWidget.addTab(self.userInfoPage, icon8, "")
        self.Stats_Tab = QWidget()
        self.Stats_Tab.setObjectName(u"Stats_Tab")
        self.localStats = QTreeView(self.Stats_Tab)
        self.localStats.setObjectName(u"localStats")
        self.localStats.setGeometry(QRect(0, 10, 771, 801))
        icon9 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.tabWidget.addTab(self.Stats_Tab, icon9, "")
        self.About_tab = QWidget()
        self.About_tab.setObjectName(u"About_tab")
        self.verticalLayoutWidget = QWidget(self.About_tab)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(-1, -1, 771, 691))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.verticalLayout.addItem(self.horizontalSpacer)

        icon10 = QIcon()
        icon10.addFile(u"../../../Pictures/QTHordeAssets/IconSmaller.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.tabWidget.addTab(self.About_tab, icon10, "")

        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 792, 21))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.modelComboBox.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.PromptBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Prompt", None))
        self.NegativePromptBox.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Negative Prompt", None))
        self.imagesLabel.setText(QCoreApplication.translate("MainWindow", u"Images", None))
        self.stepsLabel.setText(QCoreApplication.translate("MainWindow", u"Steps", None))
        self.modelLabel.setText(QCoreApplication.translate("MainWindow", u"Model", None))
        self.modelComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Loading...", None))

        self.modelComboBox.setCurrentText(QCoreApplication.translate("MainWindow", u"Loading...", None))
        self.modelComboBox.setPlaceholderText("")
        self.modelDetailsButton.setText(QCoreApplication.translate("MainWindow", u"Model Details ", None))
        self.presetLabel.setText(QCoreApplication.translate("MainWindow", u"Preset", None))
        self.presetComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Custom", None))
        self.presetComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Portrait", None))
        self.presetComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"Landscape", None))
        self.presetComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"Large Portrait", None))
        self.presetComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"Large Landscape", None))
        self.presetComboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"Square", None))
        self.presetComboBox.setItemText(6, QCoreApplication.translate("MainWindow", u"Large Square", None))

        self.widthLabel.setText(QCoreApplication.translate("MainWindow", u"Width", None))
        self.heightLabel.setText(QCoreApplication.translate("MainWindow", u"Height", None))
        self.samplerLabel.setText(QCoreApplication.translate("MainWindow", u"Sampler", None))
        self.samplerComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"k_euler", None))
        self.samplerComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"k_euler_a", None))
        self.samplerComboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"k_lms", None))
        self.samplerComboBox.setItemText(3, QCoreApplication.translate("MainWindow", u"k_heun", None))
        self.samplerComboBox.setItemText(4, QCoreApplication.translate("MainWindow", u"k_dpm_2", None))
        self.samplerComboBox.setItemText(5, QCoreApplication.translate("MainWindow", u"k_dpm_2_a", None))
        self.samplerComboBox.setItemText(6, QCoreApplication.translate("MainWindow", u"k_dpm_adaptive", None))
        self.samplerComboBox.setItemText(7, QCoreApplication.translate("MainWindow", u"k_dpm_fast", None))
        self.samplerComboBox.setItemText(8, QCoreApplication.translate("MainWindow", u"k_dpmpp_2m", None))
        self.samplerComboBox.setItemText(9, QCoreApplication.translate("MainWindow", u"k_dpmpp_2s_a", None))
        self.samplerComboBox.setItemText(10, QCoreApplication.translate("MainWindow", u"k_dpmpp_sde", None))
        self.samplerComboBox.setItemText(11, QCoreApplication.translate("MainWindow", u"DDIM", None))
        self.samplerComboBox.setItemText(12, QCoreApplication.translate("MainWindow", u"lcm", None))
        self.samplerComboBox.setItemText(13, QCoreApplication.translate("MainWindow", u"dpmsolver", None))

        self.seedLabel.setText(QCoreApplication.translate("MainWindow", u"Seed", None))
#if QT_CONFIG(tooltip)
        self.seedSpinBox.setToolTip(QCoreApplication.translate("MainWindow", u"0 for unseeded generations", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.seedSpinBox.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.guidenceLabel.setText(QCoreApplication.translate("MainWindow", u"Guidence", None))
        self.clipSkipLabel.setText(QCoreApplication.translate("MainWindow", u"Clip Skip", None))
#if QT_CONFIG(tooltip)
        self.GenerateButton.setToolTip(QCoreApplication.translate("MainWindow", u"Shortcut Ctrl + Enter", None))
#endif // QT_CONFIG(tooltip)
        self.GenerateButton.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
#if QT_CONFIG(shortcut)
        self.GenerateButton.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Return", None))
#endif // QT_CONFIG(shortcut)
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.create_tab), QCoreApplication.translate("MainWindow", u"Create", None))
        self.groupBox_2.setTitle("")
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"ID", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtablewidgetitem2 = self.tableWidget.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"Prompt", None));
        ___qtablewidgetitem3 = self.tableWidget.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"Model", None));
        ___qtablewidgetitem4 = self.tableWidget.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"ETA", None));
        ___qtablewidgetitem5 = self.tableWidget.verticalHeaderItem(0)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"Example 1", None));
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Current In-progress items", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.curr_items_tab), QCoreApplication.translate("MainWindow", u"Current Items", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.gallery_tab), QCoreApplication.translate("MainWindow", u"Gallery", None))
        self.APIKeyLabel.setText(QCoreApplication.translate("MainWindow", u"API Key", None))
        self.apiKeyEntry.setPlaceholderText(QCoreApplication.translate("MainWindow", u"API Key", None))
        self.showAPIKey.setText(QCoreApplication.translate("MainWindow", u"Show API Key", None))
        self.saveAPIkey.setText(QCoreApplication.translate("MainWindow", u"Save API Key", None))
        self.copyAPIkey.setText(QCoreApplication.translate("MainWindow", u"Copy API Key", None))
        self.NSFWLabel.setText(QCoreApplication.translate("MainWindow", u"NSFW", None))
#if QT_CONFIG(tooltip)
        self.NSFWCheckBox.setToolTip(QCoreApplication.translate("MainWindow", u"Whether to allow the generation of NSFW content. Accidental NSFW content will be censored by workers.", None))
#endif // QT_CONFIG(tooltip)
        self.NSFWCheckBox.setText("")
        self.maxJobsLabel.setText(QCoreApplication.translate("MainWindow", u"Max jobs", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.settings_tab), QCoreApplication.translate("MainWindow", u"Settings", None))
        self.usernameLabel.setText(QCoreApplication.translate("MainWindow", u"Username", None))
        self.idLabel.setText(QCoreApplication.translate("MainWindow", u"ID", None))
        self.kudosLabel.setText(QCoreApplication.translate("MainWindow", u"Kudos", None))
        self.trustedLabel.setText(QCoreApplication.translate("MainWindow", u"Trusted", None))
        self.maximumConcurrencyLabel.setText(QCoreApplication.translate("MainWindow", u"Maximum Concurrency", None))
        self.moderatorLabel.setText(QCoreApplication.translate("MainWindow", u"Moderator", None))
        self.numberOfWorkersLabel.setText(QCoreApplication.translate("MainWindow", u"Number of Workers", None))
        self.flaggedLabel.setText(QCoreApplication.translate("MainWindow", u"Flagged", None))
        self.VPNLabel.setText(QCoreApplication.translate("MainWindow", u"VPN", None))
        self.serviceLabel.setText(QCoreApplication.translate("MainWindow", u"Service", None))
        self.educationLabel.setText(QCoreApplication.translate("MainWindow", u"Education", None))
        self.customizerLabel.setText(QCoreApplication.translate("MainWindow", u"Customizer", None))
        self.specialLabel.setText(QCoreApplication.translate("MainWindow", u"Special", None))
        self.pseudonymousLabel.setText(QCoreApplication.translate("MainWindow", u"Pseudonymous", None))
        self.accountAgeLabel.setText(QCoreApplication.translate("MainWindow", u"Account Age", None))
        self.accountCreatedLabel.setText(QCoreApplication.translate("MainWindow", u"Account Created", None))
        self.textGeneratedLabel.setText(QCoreApplication.translate("MainWindow", u"Text Generated", None))
        self.textGeneratedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" message(s)", None))
        self.imageGeneratedLabel.setText(QCoreApplication.translate("MainWindow", u"Image Generated", None))
        self.imageGeneratedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" image(s)", None))
        self.interrogationGeneratedLabel_2.setText(QCoreApplication.translate("MainWindow", u"Interrogation Generated", None))
        self.interrogationGeneratedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" interrogation(s)", None))
        self.textRequestedLabel.setText(QCoreApplication.translate("MainWindow", u"Text Requested", None))
        self.textRequestedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" message(s)", None))
        self.imagesRequestedLabel.setText(QCoreApplication.translate("MainWindow", u"Images Requested", None))
        self.imagesRequestedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" image(s)", None))
        self.interrogationRequestedLabel.setText(QCoreApplication.translate("MainWindow", u"Interrogation Requested", None))
        self.interrogationRequestedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" interrogation(s)", None))
        self.tokensRequestedLabel.setText(QCoreApplication.translate("MainWindow", u"Tokens Requested", None))
        self.tokensRequestedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" token(s)", None))
        self.megapixelstepsRequestedLabel.setText(QCoreApplication.translate("MainWindow", u"Megapixelsteps Requested", None))
        self.megapixelstepsRequestedDoubleSpinBox.setPrefix("")
        self.megapixelstepsRequestedDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" megapixelstep(s)", None))
        self.tokensGeneratedLabel.setText(QCoreApplication.translate("MainWindow", u"Tokens Generated", None))
        self.tokensGeneratedSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" token(s)", None))
        self.megapixelstepsGeneratedLabel.setText(QCoreApplication.translate("MainWindow", u"Megapixelsteps Generated", None))
        self.megapixelstepsGeneratedDoubleSpinBox.setPrefix("")
        self.megapixelstepsGeneratedDoubleSpinBox.setSuffix(QCoreApplication.translate("MainWindow", u" megapixelstep(s)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.userInfoPage), QCoreApplication.translate("MainWindow", u"User Info", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Stats_Tab), QCoreApplication.translate("MainWindow", u"Stats", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.About_tab), QCoreApplication.translate("MainWindow", u"About", None))
    # retranslateUi

