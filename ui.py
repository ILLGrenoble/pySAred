try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    from PyQt6.QtWidgets import QMainWindow
    qt_ver = 6
except ImportError:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtWidgets import QMainWindow
    qt_ver = 5
print("Using Qt version %d." % qt_ver)

import pyqtgraph as pg
import numpy as np
import pkgutil, platform


if qt_ver < 6:
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)


class Ui_MainWindow(QMainWindow):

    def __create_element(self, object, geometry, objectName, text=None, font=None, placeholder=None, visible=None, stylesheet=None, checked=None, title=None, combo=None, enabled=None):

        object.setObjectName(objectName)

        if not geometry == [999, 999, 999, 999]: object.setGeometry(QtCore.QRect(geometry[0], geometry[1], geometry[2], geometry[3]))

        if not text == None: object.setText(text)
        if not title == None: object.setTitle(title)
        if not font == None: object.setFont(font)
        if not placeholder == None: object.setPlaceholderText(placeholder)
        if not visible == None: object.setVisible(visible)
        if not checked == None: object.setChecked(checked)
        if not enabled == None: object.setEnabled(enabled)

        if not stylesheet == None: object.setStyleSheet(stylesheet)

        if not combo == None:
            for i in combo: object.addItem(str(i))

    ##--> define user interface elements
    def setupUi(self, MainWindow):

        # Fonts
        font_headline = QtGui.QFont()
        font_headline.setPointSize(11 if platform.system() == 'Windows' else 12)
        font_headline.setBold(True)

        font_button = QtGui.QFont()
        font_button.setPointSize(10 if platform.system() == 'Windows' else 11)
        font_button.setBold(True)

        font_graphs = QtGui.QFont()
        font_graphs.setPixelSize(11 if platform.system() == 'Windows' else 12)
        font_graphs.setBold(False)

        font_ee = QtGui.QFont()
        font_ee.setPointSize(8 if platform.system() == 'Windows' else 10)
        font_ee.setBold(False)

        # Main Window
        MainWindow.setObjectName("MainWindow")
        MainWindow_size = [1180, 721] if platform.system() == 'Windows' else [1180, 701]
        MainWindow.resize(MainWindow_size[0], MainWindow_size[1])
        if qt_ver < 6:
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        else:
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(MainWindow_size[0], MainWindow_size[1]))
        MainWindow.setMaximumSize(QtCore.QSize(MainWindow_size[0], MainWindow_size[1]))
        if qt_ver < 6:
            MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
            MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowNestedDocks|QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        else:
            MainWindow.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
            MainWindow.setDockOptions(QtWidgets.QMainWindow.DockOption.AllowNestedDocks|QtWidgets.QMainWindow.DockOption.AllowTabbedDocks|QtWidgets.QMainWindow.DockOption.AnimatedDocks)
        MainWindow.setWindowTitle("pySAred")

        # when we create .exe with pyinstaller, we need to store icon inside it. Then we find it inside unpacked temp directory.
        for i in pkgutil.iter_importers():
            path = str(i).split("'")[1].replace("\\\\", "\\") if str(i).find('FileFinder')>=0 else None
            if path != None: self.iconpath = path + "\\images\\icon.ico"
        MainWindow.setWindowIcon(QtGui.QIcon(self.iconpath))
        MainWindow.setIconSize(QtCore.QSize(30, 30))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Block: .h5 files
        self.label_h5Scans = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_h5Scans, [15, 5, 200, 20], "label_h5Scans", text=".h5 files", font=font_headline, stylesheet="QLabel { color : blue; }")
        self.groupBox_data = QtWidgets.QGroupBox(self.centralwidget)
        self.__create_element(self.groupBox_data, [10, 20, 279, 658], "groupBox_data", font=font_ee)
        self.label_dataFiles = QtWidgets.QLabel(self.groupBox_data)
        self.__create_element(self.label_dataFiles, [10, 11, 121, 21], "label_dataFiles", text="Data", font=font_headline)
        self.tableWidget_scans = QtWidgets.QTableWidget(self.groupBox_data)
        self.__create_element(self.tableWidget_scans, [10, 36, 260, 342], "tableWidget_scans", font=font_ee)

        if qt_ver < 6:
            self.tableWidget_scans.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.tableWidget_scans.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.tableWidget_scans.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
            self.tableWidget_scans.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            self.tableWidget_scans.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableWidget_scans.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableWidget_scans.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
            self.tableWidget_scans.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget_scans.setAutoScroll(True)
        self.tableWidget_scans.setColumnCount(4)
        self.tableWidget_scans.setRowCount(0)
        headers_table_scans = ["Scan", "DB", "Scan_file_full_path"]
        for i in range(0,3):
            self.tableWidget_scans.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem())
            self.tableWidget_scans.horizontalHeaderItem(i).setText(headers_table_scans[i])
        self.tableWidget_scans.horizontalHeader().setVisible(True)
        self.tableWidget_scans.verticalHeader().setVisible(False)
        self.tableWidget_scans.setColumnWidth(0, 200)
        self.tableWidget_scans.setColumnWidth(1, int(self.tableWidget_scans.width()) - int(self.tableWidget_scans.columnWidth(0)) - 2)
        self.tableWidget_scans.setColumnWidth(2, 0)
        self.pushButton_deleteScans = QtWidgets.QPushButton(self.groupBox_data)
        self.__create_element(self.pushButton_deleteScans, [10, 381, 81, 20], "pushButton_deleteScans", text="Delete scans", font=font_ee)
        self.pushButton_importScans = QtWidgets.QPushButton(self.groupBox_data)
        self.__create_element(self.pushButton_importScans, [189, 381, 81, 20], "pushButton_importScans", text="Import scans", font=font_ee)
        self.label_DB_files = QtWidgets.QLabel(self.groupBox_data)
        self.__create_element(self.label_DB_files, [10, 415, 191, 23], "label_DB_files", text="Direct Beam(s)", font=font_headline)
        self.checkBox_rearrangeDbAfter = QtWidgets.QCheckBox(self.groupBox_data)
        self.__create_element(self.checkBox_rearrangeDbAfter, [10, 445, 210, 20], "checkBox_rearrangeDbAfter", text="DB's were measured after the scans", font=font_ee)
        self.tableWidget_DB = QtWidgets.QTableWidget(self.groupBox_data)
        self.__create_element(self.tableWidget_DB, [10, 446, 260, 183], "tableWidget_DB", font=font_ee)
        if qt_ver < 6:
            self.tableWidget_DB.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.tableWidget_DB.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
            self.tableWidget_DB.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
            self.tableWidget_DB.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        else:
            self.tableWidget_DB.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableWidget_DB.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.tableWidget_DB.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.AllEditTriggers)
            self.tableWidget_DB.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tableWidget_DB.setAutoScroll(True)
        self.tableWidget_DB.setColumnCount(2)
        self.tableWidget_DB.setRowCount(0)
        headers_table_db = ["Scan", "Path"]
        for i in range(0, 2):
            self.tableWidget_DB.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem())
            self.tableWidget_DB.horizontalHeaderItem(i).setText(headers_table_db[i])
        self.tableWidget_DB.horizontalHeader().setVisible(False)
        self.tableWidget_DB.verticalHeader().setVisible(False)
        self.tableWidget_DB.setColumnWidth(0, self.tableWidget_DB.width())
        self.tableWidget_DB.setColumnWidth(1, 0)
        self.tableWidget_DB.setSortingEnabled(True)
        self.pushButton_deleteDB = QtWidgets.QPushButton(self.groupBox_data)
        self.__create_element(self.pushButton_deleteDB, [10, 631, 81, 20], "pushButton_deleteDB", text="Delete DB", font=font_ee)
        self.pushButton_importDB = QtWidgets.QPushButton(self.groupBox_data)
        self.__create_element(self.pushButton_importDB, [189, 631, 81, 20], "pushButton_importDB", text="Import DB", font=font_ee)

        # Block: Sample
        self.label_sample = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_sample, [305, 5, 200, 20], "label_sample", text="Sample", font=font_headline, stylesheet="QLabel { color : blue; }")
        self.groupBox_sampleLen = QtWidgets.QGroupBox(self.centralwidget)
        self.__create_element(self.groupBox_sampleLen, [300, 20, 282, 38], "groupBox_sampleLen", font=font_ee)
        self.label_sampleLen = QtWidgets.QLabel(self.groupBox_sampleLen)
        self.__create_element(self.label_sampleLen, [10, 15, 131, 16], "label_sampleLen", text="Sample length (mm)", font=font_ee)
        self.lineEdit_sampleLen = QtWidgets.QLineEdit(self.groupBox_sampleLen)
        self.__create_element(self.lineEdit_sampleLen, [192, 13, 83, 21], "lineEdit_sampleLen", text="50")

        # Block: Reductions and Instrument settings
        self.label_reductions = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_reductions, [305, 65, 200, 16], "label_reductions", text="Reductions", font=font_headline, stylesheet="QLabel { color : blue; }")
        self.tabWidget_reductions = QtWidgets.QTabWidget(self.centralwidget)
        self.__create_element(self.tabWidget_reductions, [300, 87, 281, 226], "tabWidget_reductions", font=font_ee)
        if qt_ver < 6:
            self.tabWidget_reductions.setTabPosition(QtWidgets.QTabWidget.North)
            self.tabWidget_reductions.setTabShape(QtWidgets.QTabWidget.Rounded)
            self.tabWidget_reductions.setElideMode(QtCore.Qt.ElideNone)
        else:
            self.tabWidget_reductions.setTabPosition(QtWidgets.QTabWidget.TabPosition.North)
            self.tabWidget_reductions.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
            self.tabWidget_reductions.setElideMode(QtCore.Qt.TextElideMode.ElideNone)

        # Tab: Reductions
        self.tab_reductions = QtWidgets.QWidget()
        self.tab_reductions.setObjectName("tab_reductions")
        self.checkBox_reductions_divideByMonitorOrTime = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_divideByMonitorOrTime, [10, 10, 131, 18], "checkBox_reductions_divideByMonitorOrTime", font=font_ee, text="Divide by")
        self.comboBox_reductions_divideByMonitorOrTime = QtWidgets.QComboBox(self.tab_reductions)
        self.__create_element(self.comboBox_reductions_divideByMonitorOrTime, [80, 9, 70, 20], "comboBox_reductions_divideByMonitorOrTime", font=font_ee, combo=["monitor", "time"])
        self.checkBox_reductions_normalizeByDB = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_normalizeByDB, [10, 35, 181, 18], "checkBox_reductions_normalizeByDB", text="Normalize by direct beam", font=font_ee)
        # User will need Attenuator only with DB. Otherwice I hide this option and replace with Scale factor
        self.checkBox_reductions_attenuatorDB = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_attenuatorDB, [10, 60, 161, 18], "checkBox_reductions_attenuatorDB", text="Direct beam attenuator", font=font_ee, checked=True, visible=False)
        self.lineEdit_reductions_attenuatorDB = QtWidgets.QLineEdit(self.tab_reductions)
        self.__create_element(self.lineEdit_reductions_attenuatorDB, [30, 85, 221, 20], "lineEdit_reductions_subtractBkg_Skip", text="", font=font_ee, placeholder="Attenuator correction factor [default 10]", visible=False)
        self.checkBox_reductions_scaleFactor = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_scaleFactor, [10, 60, 161, 18], "checkBox_reductions_scaleFactor", text="Scale factor", font=font_ee, checked=False)
        self.lineEdit_reductions_scaleFactor = QtWidgets.QLineEdit(self.tab_reductions)
        self.__create_element(self.lineEdit_reductions_scaleFactor, [30, 85, 221, 20], "lineEdit_reductions_scaleFactor", text="",  font=font_ee, placeholder="Divide reflectivity curve by [default 10]")
        self.checkBox_reductions_subtractBkg = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_subtractBkg, [10, 115, 231, 18], "checkBox_reductions_subtractBkg", text="Subtract background (using 1 ROI)", font=font_ee)
        self.lineEdit_reductions_subtractBkg_Skip = QtWidgets.QLineEdit(self.tab_reductions)
        self.__create_element(self.lineEdit_reductions_subtractBkg_Skip, [30, 140, 221, 20], "lineEdit_reductions_subtractBkg_Skip", text="", font=font_ee, placeholder="Skip background corr. at Qz < [default 0]")
        self.checkBox_reductions_overilluminationCorr = QtWidgets.QCheckBox(self.tab_reductions)
        self.__create_element(self.checkBox_reductions_overilluminationCorr, [10, 170, 181, 18], "checkBox_reductions_overilluminationCorr", text="Overillumination correction", font=font_ee)
        self.tabWidget_reductions.addTab(self.tab_reductions, "")
        self.tabWidget_reductions.setTabText(0, "Reductions")

        # Tab: Instrument settings
        self.tab_instrumentSettings = QtWidgets.QWidget()
        self.tab_instrumentSettings.setObjectName("tab_instrumentSettings")
        self.label_instrument_wavelength = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_wavelength, [10, 10, 111, 16], "label_instrument_wavelength", text="Wavelength (A)", font=font_ee)
        self.lineEdit_instrument_wavelength = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_wavelength, [225, 10, 41, 18], "lineEdit_instrument_wavelength", font=font_ee, text="5.183")
        self.label_instrument_wavelengthResolution = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_wavelengthResolution, [10, 33, 271, 16], "label_instrument_wavelengthResolution", text="Wavelength resolution (d_lambda/lambda)", font=font_ee)
        self.lineEdit_instrument_wavelengthResolution = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_wavelengthResolution, [225, 33, 41, 18], "lineEdit_instrument_wavelengthResolution", font=font_ee, text="0.004")
        self.label_instrument_distanceS1ToSample = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_distanceS1ToSample, [10, 56, 241, 16], "label_instrument_distanceS1ToSample", font=font_ee, text="Mono_slit to Samplle distance (mm)")
        self.lineEdit_instrument_distanceS1ToSample = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_distanceS1ToSample, [225, 56, 41, 18], "lineEdit_instrument_distanceS1ToSample", font=font_ee, text="2300")
        self.label_instrument_distanceS2ToSample = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_distanceS2ToSample, [10, 79, 241, 16], "label_instrument_distanceS2ToSample", font=font_ee, text="Sample_slit to Sample distance (mm)")
        self.lineEdit_instrument_distanceS2ToSample = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_distanceS2ToSample, [225, 79, 41, 18], "lineEdit_instrument_distanceS2ToSample", font=font_ee, text="290")
        self.label_instrument_distanceSampleToDetector = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_distanceSampleToDetector, [10, 102, 241, 16], "label_instrument_distanceSampleToDetector", font=font_ee, text="Sample to Detector distance (mm)")
        self.lineEdit_instrument_distanceSampleToDetector = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_distanceSampleToDetector, [225, 102, 41, 18], "lineEdit_instrument_distanceSampleToDetector", font=font_ee, text="2500")
        self.label_instrument_sampleCurvature = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_sampleCurvature, [10, 152, 241, 16], "label_instrument_sampleCurvature", font=font_ee, text="Sample curvature (in ROI) (SFM) (rad)")
        self.lineEdit_instrument_sampleCurvature = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_sampleCurvature, [225, 152, 41, 18], "lineEdit_instrument_sampleCurvature", font=font_ee, text="0")
        self.label_instrument_offsetFull = QtWidgets.QLabel(self.tab_instrumentSettings)
        self.__create_element(self.label_instrument_offsetFull, [10, 175, 241, 16], "label_instrument_offsetFull", font=font_ee, text="Sample angle offset (th - deg)")
        self.lineEdit_instrument_offsetFull = QtWidgets.QLineEdit(self.tab_instrumentSettings)
        self.__create_element(self.lineEdit_instrument_offsetFull, [225, 175, 41, 18], "lineEdit_instrument_offsetFull", font=font_ee, text="0")
        self.tabWidget_reductions.addTab(self.tab_instrumentSettings, "")
        self.tabWidget_reductions.setTabText(1, "Instrument / Corrections")

        # Tab: Export options
        self.tab_exportOptions = QtWidgets.QWidget()
        self.tab_exportOptions.setObjectName("tab_exportOptions")
        self.checkBox_export_addResolutionColumn = QtWidgets.QCheckBox(self.tab_exportOptions)
        self.__create_element(self.checkBox_export_addResolutionColumn, [10, 10, 260, 18], "checkBox_export_addResolutionColumn", text="Include ang. resolution column in the output file", font=font_ee, checked=True)
        self.checkBox_export_resolutionLikeSared = QtWidgets.QCheckBox(self.tab_exportOptions)
        self.__create_element(self.checkBox_export_resolutionLikeSared, [10, 35, 250, 18], "checkBox_export_resolutionLikeSared", text="Use original 'Sared' way for ang. resolution calc.", font=font_ee, checked=False)
        self.checkBox_export_removeZeros = QtWidgets.QCheckBox(self.tab_exportOptions)
        self.__create_element(self.checkBox_export_removeZeros, [10, 60, 250, 18], "checkBox_export_removeZeros", text="Remove zeros from reduced files", font=font_ee, checked=False)
        self.label_export_angle = QtWidgets.QLabel(self.tab_exportOptions)
        self.__create_element(self.label_export_angle, [10, 85, 70, 18], "label_export_angle", font=font_ee, text="Export angle:")
        self.comboBox_export_angle = QtWidgets.QComboBox(self.tab_exportOptions)
        self.__create_element(self.comboBox_export_angle, [85, 84, 70, 20], "comboBox_export_angle", font=font_ee, combo=["Qz", "Degrees", "Radians"])
        self.tabWidget_reductions.addTab(self.tab_exportOptions, "")
        self.tabWidget_reductions.setTabText(2, "Export")

        # Block: Save reduced files at
        self.label_saveAt = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_saveAt, [305, 320, 200, 20], "label_saveAt", font=font_headline, text="Save reduced files at", stylesheet="QLabel { color : blue; }")
        self.groupBox_saveAt = QtWidgets.QGroupBox(self.centralwidget)
        self.__create_element(self.groupBox_saveAt, [299, 335, 282, 39], "groupBox_saveAt", font=font_ee, title="")
        self.lineEdit_saveAt = QtWidgets.QLineEdit(self.groupBox_saveAt)
        self.__create_element(self.lineEdit_saveAt, [10, 12, 225, 22], "lineEdit_saveAt", font=font_ee, text=self.dir_current)
        self.toolButton_saveAt = QtWidgets.QToolButton(self.groupBox_saveAt)
        self.__create_element(self.toolButton_saveAt, [248, 12, 27, 22], "toolButton_saveAt", font=font_ee, text="...")

        # Button: Clear
        self.pushButton_clear = QtWidgets.QPushButton(self.centralwidget)
        self.__create_element(self.pushButton_clear, [300, 380, 88, 30], "pushButton_clear", font=font_button, text="Clear all")

        # Button: Reduce all
        self.pushButton_reduceAll = QtWidgets.QPushButton(self.centralwidget)
        self.__create_element(self.pushButton_reduceAll, [493, 380, 88, 30], "pushButton_reduceAll", font=font_button, text="Reduce all")

        # Block: Recheck following files in SFM
        self.label_recheckFilesInSFM = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_recheckFilesInSFM, [305, 490, 250, 20], "label_recheckFilesInSFM", font=font_headline, text="Recheck following files in SFM", stylesheet="QLabel { color : blue; }")
        self.groupBox_recheckFilesInSFM = QtWidgets.QGroupBox(self.centralwidget)
        self.__create_element(self.groupBox_recheckFilesInSFM, [299, 509, 282, 169], "groupBox_recheckFilesInSFM", font=font_ee, title="")
        self.listWidget_recheckFilesInSFM = QtWidgets.QListWidget(self.groupBox_recheckFilesInSFM)
        self.__create_element(self.listWidget_recheckFilesInSFM, [10, 18, 262, 143], "listWidget_recheckFilesInSFM")

        # Block: Single File Mode
        self.label_SFM = QtWidgets.QLabel(self.centralwidget)
        self.__create_element(self.label_SFM, [596, 5, 200, 20], "label_SFM", font=font_headline, text="Single File Mode (SFM)", stylesheet="QLabel { color : blue; }")
        self.groupBox_SFM_scan = QtWidgets.QGroupBox(self.centralwidget)
        self.__create_element(self.groupBox_SFM_scan, [591, 20, 472, 38], "groupBox_SFM_scan", font=font_ee)
        self.label_SFM_scan = QtWidgets.QLabel(self.groupBox_SFM_scan)
        self.__create_element(self.label_SFM_scan, [10, 15, 47, 16], "label_SFM_scan", font=font_ee, text="Scan")
        self.comboBox_SFM_scan = QtWidgets.QComboBox(self.groupBox_SFM_scan)
        self.__create_element(self.comboBox_SFM_scan, [40, 13, 300, 21], "comboBox_SFM_scan", font=font_ee)
        self.label_SFM_DB = QtWidgets.QLabel(self.groupBox_SFM_scan)
        self.__create_element(self.label_SFM_DB, [360, 15, 20, 16], "label_SFM_DB", font=font_ee, text="DB")
        self.comboBox_SFM_DB = QtWidgets.QComboBox(self.groupBox_SFM_scan)
        self.__create_element(self.comboBox_SFM_DB, [380, 13, 85, 21], "comboBox_SFM_DB", font=font_ee)
        pg.setConfigOption('background', (255, 255, 255))
        pg.setConfigOption('foreground', 'k')

        # Button: Reduce SFM
        self.pushButton_reduceSFM = QtWidgets.QPushButton(self.centralwidget)
        self.__create_element(self.pushButton_reduceSFM, [1070, 28, 100, 31], "pushButton_reduceSFM", font=font_button, text="Reduce SFM")

        # Block: Detector Images and Reflectivity preview
        self.tabWidget_SFM = QtWidgets.QTabWidget(self.centralwidget)
        self.__create_element(self.tabWidget_SFM, [592, 65, 578, 613], "tabWidget_SFM", font=font_ee)

        # Tab: Detector images
        linedit_size_X = 30
        linedit_size_Y = 18
        self.tab_SFM_detectorImage = QtWidgets.QWidget()
        self.tab_SFM_detectorImage.setObjectName("tab_SFM_detectorImage")
        self.graphicsView_SFM_detectorImage_roi = pg.PlotWidget(self.tab_SFM_detectorImage, viewBox=pg.ViewBox())
        self.__create_element(self.graphicsView_SFM_detectorImage_roi, [0, 450, 577, 90], "graphicsView_SFM_detectorImage_roi")
        self.graphicsView_SFM_detectorImage_roi.hideAxis("left")
        self.graphicsView_SFM_detectorImage_roi.getAxis("bottom").tickFont = font_graphs
        self.graphicsView_SFM_detectorImage_roi.getAxis("bottom").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_detectorImage_roi.setMouseEnabled(y=False)
        self.graphicsView_SFM_detectorImage = pg.ImageView(self.tab_SFM_detectorImage, view=pg.PlotItem(viewBox=pg.ViewBox()))
        self.graphicsView_SFM_detectorImage.setGeometry(QtCore.QRect(0, 30, 577, 510))
        self.graphicsView_SFM_detectorImage.setObjectName("graphicsView_SFM_detectorImage")
        self.graphicsView_SFM_detectorImage.ui.histogram.hide()
        self.graphicsView_SFM_detectorImage.ui.menuBtn.hide()
        self.graphicsView_SFM_detectorImage.ui.roiBtn.hide()
        self.graphicsView_SFM_detectorImage.view.showAxis("left", False)
        self.graphicsView_SFM_detectorImage.view.showAxis("bottom", False)
        self.graphicsView_SFM_detectorImage.view.getViewBox().setXLink(self.graphicsView_SFM_detectorImage_roi)
        self.label_SFM_detectorImage_incidentAngle = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_incidentAngle, [10, 7, 100, 16], "label_SFM_detectorImage_incidentAngle", font=font_ee, text="Incident ang. (deg)")
        self.comboBox_SFM_detectorImage_incidentAngle = QtWidgets.QComboBox(self.tab_SFM_detectorImage)
        self.__create_element(self.comboBox_SFM_detectorImage_incidentAngle, [110, 5, 55, 20], "comboBox_SFM_detectorImage_incidentAngle", font=font_ee)
        self.label_SFM_detectorImage_polarisation = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_polarisation, [180, 7, 60, 16], "label_SFM_detectorImage_polarisation", font=font_ee, text="Polarisation")
        self.comboBox_SFM_detectorImage_polarisation = QtWidgets.QComboBox(self.tab_SFM_detectorImage)
        self.__create_element(self.comboBox_SFM_detectorImage_polarisation, [240, 5, 40, 20], "comboBox_SFM_detectorImage_polarisation", font=font_ee)
        self.label_SFM_detectorImage_colorScheme = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_colorScheme, [295, 7, 60, 16], "label_SFM_detectorImage_colorScheme", font=font_ee, text="Colors")
        self.comboBox_SFM_detectorImage_colorScheme = QtWidgets.QComboBox(self.tab_SFM_detectorImage)
        self.__create_element(self.comboBox_SFM_detectorImage_colorScheme, [330, 5, 90, 20], "comboBox_SFM_detectorImage_colorScheme", font=font_ee, combo=["Green / Blue", "White / Black"])
        self.pushButton_SFM_detectorImage_showIntegratedRoi = QtWidgets.QPushButton(self.tab_SFM_detectorImage)
        self.__create_element(self.pushButton_SFM_detectorImage_showIntegratedRoi, [445, 5, 120, 20], "pushButton_SFM_detectorImage_showIntegratedRoi", font=font_ee, text="Integrated ROI")
        self.label_SFM_detectorImage_roi = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roi, [10, 545, 31, 16], "label_SFM_detectorImage_roi", font=font_ee, text="ROI (")
        self.checkBox_SFM_detectorImage_lockRoi = QtWidgets.QCheckBox(self.tab_SFM_detectorImage)
        self.__create_element(self.checkBox_SFM_detectorImage_lockRoi, [38, 545, 50, 16], "checkBox_SFM_detectorImage_lockRoi", text="lock):", font=font_ee)
        self.label_SFM_detectorImage_roiX_left = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roiX_left, [85, 545, 51, 16], "label_SFM_detectorImage_roiX_left", font=font_ee, text="left")
        self.lineEdit_SFM_detectorImage_roiX_left = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roiX_left, [115, 544, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roiX_left", font=font_ee)
        self.label_SFM_detectorImage_roiX_right = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roiX_right, [85, 565, 51, 16], "label_SFM_detectorImage_roiX_right", font=font_ee, text="right")
        self.lineEdit_SFM_detectorImage_roiX_right = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roiX_right, [115, 564, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roiX_right", font=font_ee)
        self.label_SFM_detectorImage_roiY_bottom = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roiY_bottom, [155, 545, 51, 16], "label_SFM_detectorImage_roiY_bottom", font=font_ee, text="bottom")
        self.lineEdit_SFM_detectorImage_roiY_bottom = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roiY_bottom, [195, 544, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roiY_bottom", font=font_ee)
        self.label_SFM_detectorImage_roiY_top = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roiY_top, [155, 565, 51, 16], "label_SFM_detectorImage_roiY_top", font=font_ee, text="top")
        self.lineEdit_SFM_detectorImage_roiY_top = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roiY_top, [195, 564, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roiY_top", font=font_ee)
        self.label_SFM_detectorImage_roi_bkg = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roi_bkg, [245, 545, 47, 16], "label_SFM_detectorImage_roi_bkg", font=font_ee, text="BKG:")
        self.label_SFM_detectorImage_roi_bkgX_left = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roi_bkgX_left, [270, 545, 51, 16], "label_SFM_detectorImage_roi_bkgX_left", font=font_ee, text="left")
        self.lineEdit_SFM_detectorImage_roi_bkgX_left = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roi_bkgX_left, [300, 544, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roi_bkgX_left", font=font_ee, enabled=False, stylesheet="color:rgb(0,0,0)")
        self.label_SFM_detectorImage_roi_bkgX_right = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_roi_bkgX_right, [270, 565, 51, 16], "label_SFM_detectorImage_roi_bkgX_right", font=font_ee, text="right")
        self.lineEdit_SFM_detectorImage_roi_bkgX_right = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_roi_bkgX_right, [300, 564, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_roi_bkgX_right", font=font_ee)
        self.label_SFM_detectorImage_time = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_time, [350, 545, 71, 16], "label_SFM_detectorImage_time", font=font_ee, text="Time (s):")
        self.lineEdit_SFM_detectorImage_time = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_time, [400, 544, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_time", font=font_ee, enabled=False, stylesheet="color:rgb(0,0,0)")
        self.label_SFM_detectorImage_slits = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_slits, [450, 545, 51, 16], "label_SFM_detectorImage_slits", font=font_ee, text="Slits (mm):")
        self.label_SFM_detectorImage_slits_s1hg = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_slits_s1hg, [505, 545, 41, 16], "label_SFM_detectorImage_slits_s1hg", font=font_ee, text="s1hg")
        self.lineEdit_SFM_detectorImage_slits_s1hg = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_slits_s1hg, [535, 544, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_slits_s1hg", font=font_ee, enabled=False, stylesheet="color:rgb(0,0,0)")
        self.label_SFM_detectorImage_slits_s2hg = QtWidgets.QLabel(self.tab_SFM_detectorImage)
        self.__create_element(self.label_SFM_detectorImage_slits_s2hg, [505, 565, 30, 16], "label_SFM_detectorImage_slits_s2hg", font=font_ee, text="s2hg")
        self.lineEdit_SFM_detectorImage_slits_s2hg = QtWidgets.QLineEdit(self.tab_SFM_detectorImage)
        self.__create_element(self.lineEdit_SFM_detectorImage_slits_s2hg, [535, 564, linedit_size_X, linedit_size_Y], "lineEdit_SFM_detectorImage_slits_s2hg", font=font_ee, enabled=False, stylesheet="color:rgb(0,0,0)")
        self.tabWidget_SFM.addTab(self.tab_SFM_detectorImage, "")
        self.tabWidget_SFM.setTabText(self.tabWidget_SFM.indexOf(self.tab_SFM_detectorImage), "Detector Image")

        # Tab: Reflectivity preview
        self.tab_SFM_reflectivityPreview = QtWidgets.QWidget()
        self.tab_SFM_reflectivityPreview.setObjectName("tabreflectivity_preview")
        self.graphicsView_SFM_reflectivityPreview = pg.PlotWidget(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.graphicsView_SFM_reflectivityPreview, [0, 30, 577, 530], "graphicsView_SFM_reflectivityPreview")
        self.graphicsView_SFM_reflectivityPreview.getAxis("bottom").tickFont = font_graphs
        self.graphicsView_SFM_reflectivityPreview.getAxis("bottom").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_reflectivityPreview.getAxis("left").tickFont = font_graphs
        self.graphicsView_SFM_reflectivityPreview.getAxis("left").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_reflectivityPreview.showAxis("top")
        self.graphicsView_SFM_reflectivityPreview.getAxis("top").setTicks([])
        self.graphicsView_SFM_reflectivityPreview.showAxis("right")
        self.graphicsView_SFM_reflectivityPreview.getAxis("right").setTicks([])
        self.checkBox_SFM_reflectivityPreview_showOverillumination = QtWidgets.QCheckBox(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.checkBox_SFM_reflectivityPreview_showOverillumination, [10, 6, 140, 18], "checkBox_SFM_reflectivityPreview_showOverillumination", text="Show Overillumination", font=font_ee)
        self.checkBox_SFM_reflectivityPreview_showZeroLevel = QtWidgets.QCheckBox(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.checkBox_SFM_reflectivityPreview_showZeroLevel, [150, 6, 150, 18], "checkBox_SFM_reflectivityPreview_showZeroLevel", text="Show Zero level", font=font_ee)
        self.label_SFM_reflectivityPreview_view_reflectivity = QtWidgets.QLabel(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.label_SFM_reflectivityPreview_view_reflectivity, [320, 7, 100, 16], "label_SFM_reflectivityPreview_view_reflectivity", text="View: Reflectivity", font=font_ee)
        self.comboBox_SFM_reflectivityPreview_view_reflectivity = QtWidgets.QComboBox(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.comboBox_SFM_reflectivityPreview_view_reflectivity, [410, 5, 50, 20], "comboBox_SFM_reflectivityPreview_view_reflectivity", font=font_ee, combo=["Log", "Lin"])
        self.label_SFM_reflectivityPreview_view_angle = QtWidgets.QLabel(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.label_SFM_reflectivityPreview_view_angle, [470, 7, 50, 16], "label_SFM_reflectivityPreview_view_angle", text="vs Angle", font=font_ee)
        self.comboBox_SFM_reflectivityPreview_view_angle = QtWidgets.QComboBox(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.comboBox_SFM_reflectivityPreview_view_angle, [515, 5, 50, 20], "comboBox_SFM_reflectivityPreview_view_angle", font=font_ee, combo=["Qz", "Deg"])
        self.checkBox_SFM_reflectivityPreview_includeErrorbars = QtWidgets.QCheckBox(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.checkBox_SFM_reflectivityPreview_includeErrorbars, [10, 565, 111, 18], "checkBox_SFM_reflectivityPreview_includeErrorbars", text="Include Error Bars", font=font_ee)
        self.label_SFM_reflectivityPreview_skipPoints_left = QtWidgets.QLabel(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.label_SFM_reflectivityPreview_skipPoints_left, [372, 565, 100, 16], "label_SFM_reflectivityPreview_skipPoints_left", text="Points to skip:  left", font=font_ee)
        self.lineEdit_SFM_reflectivityPreview_skipPoints_left = QtWidgets.QLineEdit(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.lineEdit_SFM_reflectivityPreview_skipPoints_left, [470, 565, linedit_size_X, linedit_size_Y], "lineEdit_SFM_reflectivityPreview_skipPoints_left", text="0", font=font_ee)
        self.label_SFM_reflectivityPreview_skipPoints_right = QtWidgets.QLabel(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.label_SFM_reflectivityPreview_skipPoints_right, [510, 565, 80, 16], "label_SFM_reflectivityPreview_skipPoints_right", text="right", font=font_ee)
        self.lineEdit_SFM_reflectivityPreview_skipPoints_right = QtWidgets.QLineEdit(self.tab_SFM_reflectivityPreview)
        self.__create_element(self.lineEdit_SFM_reflectivityPreview_skipPoints_right, [535, 565, linedit_size_X, linedit_size_Y], "lineEdit_SFM_reflectivityPreview_skipPoints_right", text="0", font=font_ee)
        self.tabWidget_SFM.addTab(self.tab_SFM_reflectivityPreview, "")
        self.tabWidget_SFM.setTabText(self.tabWidget_SFM.indexOf(self.tab_SFM_reflectivityPreview), "Reflectivity preview")

        # Tab: 2D Map
        self.tab_2Dmap = QtWidgets.QWidget()
        self.tab_2Dmap.setObjectName("tab_2Dmap")
        # scaling options are different for different views
        # "scale" for "Qx vs Qz"
        self.checkBox_SFM_2Dmap_flip = QtWidgets.QCheckBox(self.tab_2Dmap)
        self.__create_element(self.checkBox_SFM_2Dmap_flip, [10, 6, 160, 18], "checkBox_SFM_2Dmap_flip", text="Flip (when Analyzer used)", font=font_ee, visible=False)
        self.label_SFM_2Dmap_QxzThreshold = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_QxzThreshold, [5, 7, 220, 16], "label_SFM_2Dmap_QxzThreshold", text="Threshold for the view (number of neutrons):", font=font_ee, visible=False)
        self.comboBox_SFM_2Dmap_QxzThreshold = QtWidgets.QComboBox(self.tab_2Dmap)
        self.__create_element(self.comboBox_SFM_2Dmap_QxzThreshold, [230, 5, 40, 20], "comboBox_SFM_2Dmap_QxzThreshold", font=font_ee, visible=False, combo=[1, 2, 5, 10])
        self.label_SFM_2Dmap_view_scale = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_view_scale, [183, 7, 40, 16], "label_SFM_2Dmap_view_scale", text="View", font=font_ee)
        self.comboBox_SFM_2Dmap_view_scale = QtWidgets.QComboBox(self.tab_2Dmap)
        self.__create_element(self.comboBox_SFM_2Dmap_view_scale, [210, 5, 50, 20], "comboBox_SFM_2Dmap_view_scale", font=font_ee, combo=["Log", "Lin"])
        self.label_SFM_2Dmap_polarisation = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_polarisation, [284, 7, 71, 16], "label_SFM_2Dmap_polarisation", text="Polarisation", font=font_ee)
        self.comboBox_SFM_2Dmap_polarisation = QtWidgets.QComboBox(self.tab_2Dmap)
        self.__create_element(self.comboBox_SFM_2Dmap_polarisation, [344, 5, 40, 20], "comboBox_SFM_2Dmap_polarisation", font=font_ee)
        self.label_SFM_2Dmap_axes = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_axes, [405, 7, 71, 16], "label_SFM_2Dmap_axes", text="Axes", font=font_ee)
        self.comboBox_SFM_2Dmap_axes = QtWidgets.QComboBox(self.tab_2Dmap)
        self.__create_element(self.comboBox_SFM_2Dmap_axes, [435, 5, 130, 20], "comboBox_SFM_2Dmap_axes", font=font_ee, combo=["Pixel vs. Point", "Alpha_i vs. Alpha_f", "Qx vs. Qz"])
        self.graphicsView_SFM_2Dmap = pg.ImageView(self.tab_2Dmap, view=pg.PlotItem())
        self.__create_element(self.graphicsView_SFM_2Dmap, [0, 30, 577, 522], "graphicsView_SFM_2Dmap")
        self.graphicsView_SFM_2Dmap.ui.menuBtn.hide()
        self.graphicsView_SFM_2Dmap.ui.roiBtn.hide()
        colmap = pg.ColorMap(np.array([0, 0.3333, 0.6666, 1]), np.array([[0, 0, 0, 255],[185, 0, 0, 255],[255, 220, 0, 255], [255, 255, 255, 255]], dtype=np.ubyte))
        self.graphicsView_SFM_2Dmap.setColorMap(colmap)
        self.graphicsView_SFM_2Dmap.view.showAxis("left")
        self.graphicsView_SFM_2Dmap.view.getAxis("left").tickFont = font_graphs
        self.graphicsView_SFM_2Dmap.view.getAxis("left").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_2Dmap.view.showAxis("bottom")
        self.graphicsView_SFM_2Dmap.view.getAxis("bottom").tickFont = font_graphs
        self.graphicsView_SFM_2Dmap.view.getAxis("bottom").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_2Dmap.view.showAxis("top")
        self.graphicsView_SFM_2Dmap.view.getAxis("top").setTicks([])
        self.graphicsView_SFM_2Dmap.view.showAxis("right")
        self.graphicsView_SFM_2Dmap.view.getAxis("right").setTicks([])
        self.graphicsView_SFM_2Dmap.getView().getViewBox().invertY(b=False)

        # 2D map for "Qx vs Qz" is a plot, compared to "Pixel vs Points" which is Image.
        # I rescale graphicsView_SFM_2Dmap_Qxz_theta to show/hide it
        self.graphicsView_SFM_2Dmap_Qxz_theta = pg.PlotWidget(self.tab_2Dmap)
        self.__create_element(self.graphicsView_SFM_2Dmap_Qxz_theta, [0, 0, 0, 0], "graphicsView_SFM_2Dmap_Qxz_theta")
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("bottom").tickFont = font_graphs
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("bottom").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("left").tickFont = font_graphs
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("left").setStyle(tickTextOffset=10)
        self.graphicsView_SFM_2Dmap_Qxz_theta.showAxis("top")
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("top").setTicks([])
        self.graphicsView_SFM_2Dmap_Qxz_theta.showAxis("right")
        self.graphicsView_SFM_2Dmap_Qxz_theta.getAxis("right").setTicks([])
        self.label_SFM_2Dmap_lowerNumberOfPointsBy = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_lowerNumberOfPointsBy, [5, 561, 211, 16], "label_SFM_2Dmap_lowerNumberOfPointsBy", text="Lower the number of points by factor", font=font_ee, visible=False)
        self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy = QtWidgets.QComboBox(self.tab_2Dmap)
        self.__create_element(self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy, [195, 559, 40, 20], "comboBox_SFM_2Dmap_lowerNumberOfPointsBy", font=font_ee, visible=False, combo=[5, 4, 3, 2, 1])
        self.label_SFM_2Dmap_rescaleImage_x = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_rescaleImage_x, [5, 561, 85, 16], "label_SFM_2Dmap_rescaleImage_x", text="Rescale image: x", font=font_ee)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_x = QtWidgets.QSlider(self.tab_2Dmap)
        self.__create_element(self.horizontalSlider_SFM_2Dmap_rescaleImage_x, [95, 560, 80, 22], "horizontalSlider_SFM_2Dmap_rescaleImage_x")
        if qt_ver < 6:
            self.horizontalSlider_SFM_2Dmap_rescaleImage_x.setOrientation(QtCore.Qt.Horizontal)
        else:
            self.horizontalSlider_SFM_2Dmap_rescaleImage_x.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_x.setMinimum(1)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_x.setMaximum(15)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_x.setValue(1)
        self.label_SFM_2Dmap_rescaleImage_y = QtWidgets.QLabel(self.tab_2Dmap)
        self.__create_element(self.label_SFM_2Dmap_rescaleImage_y, [185, 561, 20, 16], "label_SFM_2Dmap_rescaleImage_y", text="y", font=font_ee)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_y = QtWidgets.QSlider(self.tab_2Dmap)
        self.__create_element(self.horizontalSlider_SFM_2Dmap_rescaleImage_y, [195, 560, 80, 22], "horizontalSlider_SFM_2Dmap_rescaleImage_y")
        if qt_ver < 6:
            self.horizontalSlider_SFM_2Dmap_rescaleImage_y.setOrientation(QtCore.Qt.Horizontal)
        else:
            self.horizontalSlider_SFM_2Dmap_rescaleImage_y.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_y.setMinimum(1)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_y.setMaximum(15)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_y.setValue(1)
        self.pushButton_SFM_2Dmap_export = QtWidgets.QPushButton(self.tab_2Dmap)
        self.__create_element(self.pushButton_SFM_2Dmap_export, [445, 555, 120, 25], "pushButton_SFM_2Dmap_export", text="Export 2D map", font=font_button)
        self.tabWidget_SFM.addTab(self.tab_2Dmap, "")
        self.tabWidget_SFM.setTabText(self.tabWidget_SFM.indexOf(self.tab_2Dmap), "2D map")

        # StatusBar
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # MenuBar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.__create_element(self.menubar, [0, 0, 1000, 21], "menubar")
        self.menu_help = QtWidgets.QMenu(self.menubar)
        self.__create_element(self.menu_help, [999, 999, 999, 999], "menu_help", title="Help")
        MainWindow.setMenuBar(self.menubar)
        if qt_ver < 6:
            self.action_version = QtWidgets.QAction(MainWindow)
        else:
            self.action_version = QtGui.QAction(MainWindow)
        self.__create_element(self.action_version, [999, 999, 999, 999], "action_version", text="V1.5.1")
        self.menu_help.addAction(self.action_version)
        self.menubar.addAction(self.menu_help.menuAction())

        self.tabWidget_reductions.setCurrentIndex(0)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    ##<--
