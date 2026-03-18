#!/bin/python3
#
# Install with:
#   * Windows - pyinstaller --onefile --noconsole -i"C:\icon.ico" --add-data C:\icon.ico;images C:\pySAred_V1.5.1.py
#   * MacOS - sudo pyinstaller --onefile --windowed pySAred_V1.5.1.py
#

import ui
from ui import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import loader
import os, sys, platform
from scipy.interpolate import griddata


class GUI(ui.Ui_MainWindow):

    dir_current = ""
    if platform.system() == 'Windows': dir_current = os.getcwd().replace("\\", "/") + "/"
    else:
        for i in sys.argv[0].split("/")[:-4]: dir_current += i + "/"

    def __init__(self):

        super(GUI, self).__init__()
        self.setupUi(self)

        # Some parameters
        self.roiLocked = []
        self.SFM_FILE, self.SFMFileAlreadyAnalized, self.SFMFile2dCalculatedParams = "", "", []  # current file in Single File Mode
        self.SFM_psdUU, self.SFM_psdDU, self.SFM_psdUD, self.SFM_psdDD = [], [], [], []          # 2d arrays of pol detector
        self.th_current = ""                                                                     # current th point
        self.dict_overillCoeff = {}                                                              # write calculated overillumination coefficients into library
        self.DB_INFO, self.dbAlreadyAnalized = {}, []                                            # Write DB info into library
        self.roi_draw, self.roi_draw_bkg, self.roi_draw_2Dmap = [], [], []                       # ROI frames
        self.roi_oldCoord_Y, self.roi_draw_int = [], []                                          # Recalc intens if Y roi is changed
        self.trigger_showDetInt = True                                                           # Trigger to switch the detector image view
        self.res_aif = []                                                                        # Alpha_i vs Alpha_f array
        self.sampleCurvature_last = []                                                           # Last sample curvature (lets avoid extra recalcs)

        # Triggers
        self.action_version.triggered.connect(self.f_menu_info)

        # Triggers: Buttons
        self.pushButton_importScans.clicked.connect(self.f_button_importRemoveScans)
        self.pushButton_deleteScans.clicked.connect(self.f_button_importRemoveScans)
        self.pushButton_importDB.clicked.connect(self.f_button_importRemoveDB)
        self.pushButton_deleteDB.clicked.connect(self.f_button_importRemoveDB)
        self.toolButton_saveAt.clicked.connect(self.f_button_saveDir)
        self.pushButton_reduceAll.clicked.connect(self.f_button_reduceAll)
        self.pushButton_reduceSFM.clicked.connect(self.f_button_reduceSFM)
        self.pushButton_clear.clicked.connect(self.f_button_clear)
        self.pushButton_SFM_2Dmap_export.clicked.connect(self.f_SFM_2Dmap_export)
        self.pushButton_SFM_detectorImage_showIntegratedRoi.clicked.connect(self.f_SFM_detectorImage_draw)

        # Triggers: LineEdits
        arr_LE_roi = [self.lineEdit_SFM_detectorImage_roiX_left, self.lineEdit_SFM_detectorImage_roiX_right, self.lineEdit_SFM_detectorImage_roiY_bottom, self.lineEdit_SFM_detectorImage_roiY_top, self.lineEdit_SFM_detectorImage_roi_bkgX_right]
        arr_LE_instr = [self.lineEdit_instrument_wavelength, self.lineEdit_instrument_distanceSampleToDetector, self.lineEdit_instrument_sampleCurvature]
        arr_LE_otherParam = [self.lineEdit_sampleLen, self.lineEdit_reductions_attenuatorDB, self.lineEdit_reductions_scaleFactor, self.lineEdit_reductions_subtractBkg_Skip,  self.lineEdit_instrument_wavelengthResolution, self.lineEdit_instrument_distanceS1ToSample, self.lineEdit_instrument_distanceS2ToSample, self.lineEdit_instrument_offsetFull, self.lineEdit_SFM_reflectivityPreview_skipPoints_right, self.lineEdit_SFM_reflectivityPreview_skipPoints_left]

        [i.editingFinished.connect(self.f_SFM_roi_update) for i in arr_LE_roi]
        [i.editingFinished.connect(self.f_SFM_reflectivityPreview_load) for i in arr_LE_otherParam + arr_LE_instr]
        [i.editingFinished.connect(self.f_SFM_2Dmap_draw) for i in arr_LE_instr + arr_LE_roi]

        # Triggers: ComboBoxes
        arr_CoB_detectorImage = [self.comboBox_SFM_detectorImage_incidentAngle, self.comboBox_SFM_detectorImage_polarisation, self.comboBox_SFM_detectorImage_colorScheme]
        arr_CoB_reflectivityPreview = [self.comboBox_reductions_divideByMonitorOrTime, self.comboBox_export_angle, self.comboBox_SFM_DB, self.comboBox_SFM_scan, self.comboBox_SFM_reflectivityPreview_view_angle, self.comboBox_SFM_reflectivityPreview_view_reflectivity]
        arr_CoB_2dmap = [self.comboBox_SFM_2Dmap_QxzThreshold, self.comboBox_SFM_2Dmap_polarisation, self.comboBox_SFM_2Dmap_axes, self.comboBox_SFM_scan,
                        self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy, self.comboBox_SFM_2Dmap_view_scale]

        self.comboBox_SFM_scan.currentIndexChanged.connect(self.f_SFM_detectorImage_load)
        self.comboBox_reductions_divideByMonitorOrTime.currentIndexChanged.connect(self.f_DB_analaze)
        [i.currentIndexChanged.connect(self.f_SFM_detectorImage_draw) for i in arr_CoB_detectorImage]
        [i.currentIndexChanged.connect(self.f_SFM_reflectivityPreview_load) for i in arr_CoB_reflectivityPreview]
        [i.currentIndexChanged.connect(self.f_SFM_2Dmap_draw) for i in arr_CoB_2dmap]

        # Triggers: CheckBoxes
        self.checkBox_reductions_divideByMonitorOrTime.stateChanged.connect(self.f_DB_analaze)
        self.checkBox_reductions_normalizeByDB.stateChanged.connect(self.f_DB_analaze)
        self.checkBox_SFM_2Dmap_flip.stateChanged.connect(self.f_SFM_2Dmap_draw)

        arr_ChB_reflectivityPreview = [self.checkBox_reductions_divideByMonitorOrTime, self.checkBox_reductions_normalizeByDB, self.checkBox_reductions_attenuatorDB, self.checkBox_reductions_overilluminationCorr, self.checkBox_reductions_subtractBkg, self.checkBox_SFM_reflectivityPreview_showOverillumination, self.checkBox_SFM_reflectivityPreview_showZeroLevel, self.checkBox_SFM_reflectivityPreview_includeErrorbars, self.checkBox_rearrangeDbAfter, self.checkBox_reductions_scaleFactor, self.checkBox_export_resolutionLikeSared, self.checkBox_export_addResolutionColumn]
        [i.stateChanged.connect(self.f_SFM_reflectivityPreview_load) for i in arr_ChB_reflectivityPreview]

        self.checkBox_rearrangeDbAfter.stateChanged.connect(self.f_DB_assign)
        self.checkBox_reductions_subtractBkg.stateChanged.connect(self.f_SFM_detectorImage_draw)

        # Triggers: Sliders
        self.horizontalSlider_SFM_2Dmap_rescaleImage_x.valueChanged.connect(self.f_SFM_2Dmap_draw)
        self.horizontalSlider_SFM_2Dmap_rescaleImage_y.valueChanged.connect(self.f_SFM_2Dmap_draw)

    ##--> menu options
    def f_menu_info(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon(self.iconpath))
        msgBox.setText("pySAred " + self.action_version.text() + "\n\n"
                       "Alexey.Klechikov@gmail.com\n\n"
                       "Check new version at https://github.com/Alexey-Klechikov/pySAred/releases")
        msgBox.exec_()
    ##<--

    ##--> Main window buttons
    def f_button_importRemoveScans(self):

        if self.sender().objectName() == "pushButton_importScans":

            files_import = QtWidgets.QFileDialog().getOpenFileNames(None, "FileNames", self.dir_current, ".h5 (*.h5)")
            if files_import[0] == []: return
            # Next "Import scans" will open last dir
            self.dir_current = files_import[0][0][:files_import[0][0].rfind("/")]

            for FILE in files_import[0]:
                self.tableWidget_scans.insertRow(self.tableWidget_scans.rowCount())
                self.tableWidget_scans.setRowHeight(self.tableWidget_scans.rowCount()-1, 10)
                # File name (row 0) and full path (row 2)
                for j in range(0, 3): self.tableWidget_scans.setItem(self.tableWidget_scans.rowCount()-1, j, QtWidgets.QTableWidgetItem())
                self.tableWidget_scans.item(self.tableWidget_scans.rowCount() - 1, 0).setText(FILE[FILE.rfind("/") + 1:])
                self.tableWidget_scans.item(self.tableWidget_scans.rowCount() - 1, 2).setText(FILE)

                # add file into SFM / Scan ComboBox
                self.comboBox_SFM_scan.addItem(str(FILE[FILE.rfind("/") + 1:]))

                self.f_DB_analaze()
                self.f_SFM_reflectivityPreview_load()

        if self.sender().objectName() == "pushButton_deleteScans":

            files_remove = self.tableWidget_scans.selectedItems()
            if not files_remove: return

            for FILE in files_remove:
                self.tableWidget_scans.removeRow(self.tableWidget_scans.row(FILE))

            # update SFM list
            self.comboBox_SFM_scan.clear()
            for i in range(0, self.tableWidget_scans.rowCount()):
                self.comboBox_SFM_scan.addItem(self.tableWidget_scans.item(i, 2).text()[self.tableWidget_scans.item(i, 2).text().rfind("/") + 1:])

    def f_button_importRemoveDB(self):

        if self.sender().objectName() == "pushButton_importDB":

            files_import = QtWidgets.QFileDialog().getOpenFileNames(None, "FileNames", self.dir_current, ".h5 (*.h5)")
            if files_import[0] == []: return
            # Next "Import scans" will open last dir
            self.dir_current = files_import[0][0][:files_import[0][0].rfind("/")]

            # I couldnt make tablewidget sorting work when adding files to not empty table, so this is the solution for making the list of DB files sorted
            for i in range(self.tableWidget_DB.rowCount()-1, -1, -1):
                files_import[0].append(self.tableWidget_DB.item(i, 1).text())
                self.tableWidget_DB.removeRow(i)

            for FILE in sorted(files_import[0]):
                self.tableWidget_DB.insertRow(self.tableWidget_DB.rowCount())
                self.tableWidget_DB.setRowHeight(self.tableWidget_DB.rowCount()-1, 10)
                # File name (row 0) and full path (row 2)
                for j in range(0, 2): self.tableWidget_DB.setItem(self.tableWidget_DB.rowCount()-1, j, QtWidgets.QTableWidgetItem())
                self.tableWidget_DB.item(self.tableWidget_DB.rowCount() - 1, 0).setText(FILE[FILE.rfind("/") + 1:])
                self.tableWidget_DB.item(self.tableWidget_DB.rowCount() - 1, 1).setText(FILE)

                # add file into SFM / DB ComboBox
                self.comboBox_SFM_DB.addItem(str(FILE[FILE.rfind("/") + 1:][:5]))

            self.f_DB_analaze()
            self.f_SFM_reflectivityPreview_load()

        elif self.sender().objectName() == "pushButton_deleteDB":

            files_remove = self.tableWidget_DB.selectedItems()
            if not files_remove: return

            for FILE in files_remove: self.tableWidget_DB.removeRow(self.tableWidget_DB.row(FILE))

            # update SFM list
            self.comboBox_SFM_DB.clear()
            for i in range(0, self.tableWidget_DB.rowCount()):
                self.comboBox_SFM_DB.addItem(self.tableWidget_DB.item(i, 1).text()[self.tableWidget_DB.item(i, 1).text().rfind("/") + 1:][:5])

            self.f_DB_analaze()

    def f_button_saveDir(self):
        saveAt = QtWidgets.QFileDialog().getExistingDirectory()
        if not saveAt: return
        self.lineEdit_saveAt.setText(str(saveAt) + ("" if str(saveAt)[-1] == "/" else "/"))

    def f_button_reduceAll(self):
        self.listWidget_recheckFilesInSFM.clear()

        bkg_skip = float(self.lineEdit_reductions_subtractBkg_Skip.text()) if self.lineEdit_reductions_subtractBkg_Skip.text() else 0

        dir_saveFile = self.lineEdit_saveAt.text() if self.lineEdit_saveAt.text() else self.dir_current

        if self.statusbar.currentMessage().find("Error") == 0: return

        if self.checkBox_reductions_normalizeByDB.isChecked():
            self.f_DB_analaze()

            DB_attenFactor = 1
            if self.checkBox_reductions_attenuatorDB.isChecked():
                DB_attenFactor = 10 if self.lineEdit_reductions_attenuatorDB.text() == "" else float(self.lineEdit_reductions_attenuatorDB.text())

        # iterate through table with scans
        for i in range(0, self.tableWidget_scans.rowCount()):
            file_name = self.tableWidget_scans.item(i, 2).text()[self.tableWidget_scans.item(i, 2).text().rfind("/") + 1: -3]

            # find full name DB file if there are several of them
            FILE_DB = self.tableWidget_scans.item(i, 1).text() if self.checkBox_reductions_normalizeByDB.isChecked() else ""

            file = loader.H5Loader(self.tableWidget_scans.item(i, 2).text())
            if not file.is_ok():
                print("Error reading file %s." % self.tableWidget_scans.item(i, 2).text())
                continue

            th_list = file.get_th()
            s1hg_list = file.get_s1hg()
            s2hg_list = file.get_s2hg()

            checkThisFile = 0

            monitor_unpol_list = file.get_mon()
            monitor_uu_list, monitor_dd_list, monitor_du_list, monitor_ud_list = file.get_mon_pol()
            time_list = file.get_time()

            # check if we have several polarisations
            for detector in file.get_det_types():
                if detector == "psd": monitor_list = monitor_unpol_list
                elif detector == "psd_uu": monitor_list = monitor_uu_list
                elif detector == "psd_dd": monitor_list = monitor_dd_list
                elif detector == "psd_du": monitor_list = monitor_du_list
                elif detector == "psd_ud": monitor_list = monitor_ud_list
                else: continue

                original_roi_coord = file.get_roi()
                scan_intens = file.get_psd()[:, int(original_roi_coord[0]): int(original_roi_coord[1]), :].sum(axis=1)

                new_file = open(dir_saveFile + file_name + "_" + detector + " (" + FILE_DB + ")" + ".dat", "w")

                # iterate through th points
                for index, th in enumerate(th_list):
                    th = th - float(self.lineEdit_instrument_offsetFull.text())  # th offset

                    # analize integrated intensity for ROI
                    Intens = scan_intens[index] if len(scan_intens.shape) == 1 else sum(scan_intens[index][int(original_roi_coord[2]): int(original_roi_coord[3])])

                    if Intens == 0 and self.checkBox_export_removeZeros.isChecked(): continue

                    IntensErr = 1 if Intens == 0 else np.sqrt(Intens)

                    # read motors
                    Qz, s1hg, s2hg = (4 * np.pi / float(self.lineEdit_instrument_wavelength.text())) * np.sin(np.radians(th)), s1hg_list[index], s2hg_list[index]
                    monitor = monitor_list[index] if self.comboBox_reductions_divideByMonitorOrTime.currentText() == "monitor" else time_list[index]

                    # check if we are not in a middle of ROI in Qz approx 0.02)
                    if round(Qz, 3) > 0.015 and round(Qz, 3) < 0.03 and checkThisFile == 0:
                        scanData_0_015 = scan_intens[index][int(original_roi_coord[2]): int(original_roi_coord[3])]

                        if not max(scanData_0_015) == max(scanData_0_015[round((len(scanData_0_015) / 3)):-round((len(scanData_0_015) / 3))]):
                            self.listWidget_recheckFilesInSFM.addItem(file_name)
                            checkThisFile = 1

                    coeff = self.f_overilluminationCorrCoeff(s1hg, s2hg, round(th, 4))
                    FWHM_proj,  overillCorr = coeff[1], coeff[0] if self.checkBox_reductions_overilluminationCorr.isChecked() else 1

                    # calculate resolution in Gunnar's Sared way or other (also using overillumination correction)
                    if self.checkBox_export_resolutionLikeSared.isChecked():
                        Resolution = np.sqrt(
                            ((2 * np.pi / float(self.lineEdit_instrument_wavelength.text())) ** 2) * ((np.cos(np.radians(th))) ** 2) * (0.68 ** 2) * ((s1hg ** 2) + (s2hg ** 2)) / (
                                        (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())) ** 2) + (
                                        (float(self.lineEdit_instrument_wavelengthResolution.text()) ** 2) * (Qz ** 2)))
                    else:
                        d_alpha = np.arctan((s1hg + [s2hg if FWHM_proj == s2hg else FWHM_proj][0]) / (
                                (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())) * 2))
                        if self.comboBox_export_angle.currentText() == "Qz":
                            k_0 = 2 * np.pi / float(self.lineEdit_instrument_wavelength.text())
                            Resolution = np.sqrt((k_0 ** 2) * (
                                        (((np.cos(np.radians(th))) ** 2) * d_alpha ** 2) + ((float(self.lineEdit_instrument_wavelengthResolution.text()) ** 2) * ((np.sin(np.radians(th))) ** 2))))
                        else: Resolution = d_alpha if self.comboBox_export_angle.currentText() == "Radians" else np.degrees(d_alpha)

                    # Save resolution in sigma rather than in FWHM units
                    Resolution = Resolution / (2 * np.sqrt(2 * np.log(2)))

                    # minus background, divide by monitor, overillumination correct + calculate errors
                    if self.checkBox_reductions_subtractBkg.isChecked() and Qz > bkg_skip:
                        Intens_bkg = sum(scan_intens[index][int(original_roi_coord[2]) - 2 * (int(original_roi_coord[3]) - int(original_roi_coord[2])): int(original_roi_coord[2]) - (int(original_roi_coord[3]) - int(original_roi_coord[2]))])

                        if Intens_bkg > 0: IntensErr, Intens = np.sqrt(Intens + Intens_bkg), Intens - Intens_bkg

                    if self.checkBox_reductions_divideByMonitorOrTime.isChecked():
                        if self.comboBox_reductions_divideByMonitorOrTime.currentText() == "monitor":
                            monitor, IntensErr = monitor_list[index], IntensErr / monitor if Intens == 0 else (Intens / monitor) * np.sqrt((IntensErr / Intens) ** 2 + (1 / monitor))
                        elif self.comboBox_reductions_divideByMonitorOrTime.currentText() == "time":
                            monitor, IntensErr = time_list[index], IntensErr / monitor

                        Intens = Intens / monitor

                    if self.checkBox_reductions_overilluminationCorr.isChecked(): IntensErr, Intens = IntensErr / overillCorr, Intens / overillCorr

                    if self.checkBox_reductions_normalizeByDB.isChecked():
                        try:
                            DB_intens = float(self.DB_INFO[str(FILE_DB) + ";" + str(s1hg) + ";" + str(s2hg)].split(";")[0]) * DB_attenFactor
                            DB_err = overillCorr * float(self.DB_INFO[str(FILE_DB) + ";" + str(s1hg) + ";" + str(s2hg)].split(";")[1]) * self.DB_attenFactor

                            IntensErr = IntensErr + DB_err if Intens == 0 else (Intens / DB_intens) * np.sqrt((DB_err / DB_intens) ** 2 + (IntensErr / Intens) ** 2)
                            Intens = Intens / DB_intens
                        except:
                            if checkThisFile == 0:
                                self.listWidget_recheckFilesInSFM.addItem(file_name)
                                checkThisFile = 1

                        self.checkBox_reductions_scaleFactor.setChecked(False)

                    if self.checkBox_reductions_scaleFactor.isChecked(): IntensErr, Intens = IntensErr / self.scaleFactor, Intens / self.scaleFactor

                    # check desired output angle and do conversion if needed
                    if self.comboBox_export_angle.currentText() == "Qz": angle = round(Qz, 10)
                    elif self.comboBox_export_angle.currentText() == "Degrees": angle = round(np.degrees(np.arcsin(Qz * float(self.lineEdit_instrument_wavelength.text()) / (4 * np.pi))), 10)
                    elif self.comboBox_export_angle.currentText() == "Radians": angle = round(np.arcsin(Qz * float(self.lineEdit_instrument_wavelength.text()) / (4 * np.pi)), 10)

                    # skip the points with zero intensity
                    if (Intens == 0 and self.checkBox_export_removeZeros.isChecked()): continue

                    new_file.write(str(angle) + ' ' + str(Intens) + ' ' + str(IntensErr) + ' ')
                    if self.checkBox_export_addResolutionColumn.isChecked(): new_file.write(str(Resolution))
                    new_file.write('\n')

                # close files
                new_file.close()

                # check if file is empty - then comment inside
                if os.stat(dir_saveFile + file_name + "_" + detector + " (" + FILE_DB + ")" + ".dat").st_size == 0:
                    with open(dir_saveFile + file_name + "_" + detector + " (" + FILE_DB + ")" + ".dat", "w") as empty_file:
                        empty_file.write("All points are either zeros or negatives.")

        self.statusbar.showMessage(str(self.tableWidget_scans.rowCount()) + " files reduced, " + str(self.listWidget_recheckFilesInSFM.count()) + " file(s) might need extra care.")

    def f_button_reduceSFM(self):

        dir_saveFile = self.lineEdit_saveAt.text() if self.lineEdit_saveAt.text() else self.dir_current

        # polarisation order - uu, dd, ud, du
        detector = ["uu", "du", "ud", "dd"]

        for i in range(0, len(self.SFM_export_Qz)):

            SFM_DB_file_export = self.SFM_DB_FILE if self.checkBox_reductions_normalizeByDB.isChecked() else ""

            with open(dir_saveFile + self.SFM_FILE[self.SFM_FILE.rfind("/") + 1 : -3] + "_" + str(detector[i]) + " (" + SFM_DB_file_export + ")" + " SFM.dat", "w") as new_file:
                for j in range(0, len(self.SFM_export_Qz[i])):
                    if self.SFM_export_I[i][j] == 0 and self.checkBox_export_removeZeros.isChecked(): continue

                    if self.comboBox_export_angle.currentText() == "Qz": angle = round(self.SFM_export_Qz[i][j], 10)
                    elif self.comboBox_export_angle.currentText() == "Degrees":
                        angle = round(np.degrees(np.arcsin(self.SFM_export_Qz[i][j] * float(self.lineEdit_instrument_wavelength.text())/ (4* np.pi))), 10)
                    elif self.comboBox_export_angle.currentText() == "Radians":
                        angle = round(np.arcsin(self.SFM_export_Qz[i][j] * float(self.lineEdit_instrument_wavelength.text()) / (4 * np.pi)), 10)

                    new_file.write(str(angle) + ' ' + str(self.SFM_export_I[i][j]) + ' ' + str(self.SFM_export_dI[i][j]) + ' ')

                    if self.checkBox_export_addResolutionColumn.isChecked(): new_file.write(str(self.SFM_export_resolution[i][j]))
                    new_file.write('\n')

            # close new file
            new_file.close()

        self.statusbar.showMessage(self.SFM_FILE[self.SFM_FILE.rfind("/") + 1:] + " file is reduced in SFM.")

    def f_button_clear(self):

        for item in (self.comboBox_SFM_scan, self.listWidget_recheckFilesInSFM, self.graphicsView_SFM_detectorImage, self.graphicsView_SFM_2Dmap, self.graphicsView_SFM_reflectivityPreview.getPlotItem(),self.comboBox_SFM_detectorImage_incidentAngle, self.comboBox_SFM_detectorImage_polarisation, self.comboBox_SFM_2Dmap_polarisation):
            item.clear()

        for i in range(self.tableWidget_scans.rowCount(), -1, -1): self.tableWidget_scans.removeRow(i)
        for i in range(self.tableWidget_DB.rowCount(), -1, -1): self.tableWidget_DB.removeRow(i)
    ##<--

    ##--> extra functions to shorten the code
    def f_overilluminationCorrCoeff(self, s1hg, s2hg, th):

        # Check for Sample Length input
        try:
            sample_len = float(self.lineEdit_sampleLen.text())
        except: return [1, s2hg]

        config = str(s1hg) + " " + str(s2hg) + " " + str(th) + " " + str(sample_len) + " " + self.lineEdit_instrument_distanceS1ToSample.text() + " " + self.lineEdit_instrument_distanceS2ToSample.text()

        # check if we already calculated overillumination for current configuration
        if config in self.dict_overillCoeff: coeff = self.dict_overillCoeff[config]
        else:
            coeff = [0, 0]

            # for trapezoid beam - find (half of) widest beam width (OC) and flat region (OB) with max intensity
            if s1hg < s2hg:
                OB = abs(((float(self.lineEdit_instrument_distanceS1ToSample.text()) * (s2hg - s1hg)) / (2 * (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())))) + s1hg / 2)
                OC = ((float(self.lineEdit_instrument_distanceS1ToSample.text()) * (s2hg + s1hg)) / (2 * (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())))) - s1hg / 2
            elif s1hg > s2hg:
                OB = abs(((s2hg * float(self.lineEdit_instrument_distanceS1ToSample.text())) - (s1hg * float(self.lineEdit_instrument_distanceS2ToSample.text()))) / (2 * (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text()))))
                OC = (float(self.lineEdit_instrument_distanceS1ToSample.text()) / (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text()))) * (s2hg + s1hg) / 2 - (s1hg / 2)
            elif s1hg == s2hg:
                OB = s1hg / 2
                OC = s1hg * (float(self.lineEdit_instrument_distanceS1ToSample.text()) / (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())) - 1 / 2)

            BC = OC - OB
            AO = 1 / (BC/2 + OB)  # normalized height of trapezoid
            FWHM_beam = BC/2 + OB  # half of the beam FWHM
            sampleLen_relative = float(sample_len) * np.sin(np.radians(np.fabs(th if not th == 0 else 0.00001)))  # projection of sample surface on the beam

            # "coeff" represents how much of total beam intensity illuminates the sample
            if sampleLen_relative / 2 >= OC: coeff[0] = 1
            else:  # check if we use only middle part of the beam or trapezoid "shoulders" also
                if sampleLen_relative / 2 <= OB: coeff[0] = AO*sampleLen_relative/2 # Square part
                elif sampleLen_relative / 2 > OB: coeff[0] = AO * (OB + BC/2 - ((OC-sampleLen_relative/2)**2) / (2*BC)) # Square part + triangle - edge of triangle that dont cover the sample

            # for the beam resolution calcultion we check how much of the beam FHWM we cover by the sample
            coeff[1] = s2hg if sampleLen_relative / 2 >= FWHM_beam else sampleLen_relative

            self.dict_overillCoeff[config] = coeff

        return coeff

    def f_DB_analaze(self):

        self.DB_INFO = {}

        for i in range(0, self.tableWidget_DB.rowCount()):
            file = loader.H5Loader(self.tableWidget_DB.item(i,1).text())
            if not file.is_ok():
                print("Error reading file %s." % self.tableWidget_DB.item(i,1).text())
                continue

            th_list = file.get_th()
            s1hg_list = file.get_s1hg()
            s2hg_list = file.get_s2hg()

            if self.checkBox_reductions_divideByMonitorOrTime.isChecked(): monitor = monitor_list if self.comboBox_reductions_divideByMonitorOrTime.currentText() == "monitor" else time_list
            else: monitor = np.ones_like(intens_list)

            for j in range(0, len(th_list)):
                DB_intens = float(intens_list[j]) / float(monitor[j])
                if self.checkBox_reductions_divideByMonitorOrTime.isChecked() and self.comboBox_reductions_divideByMonitorOrTime.currentText() == "monitor":
                    DB_err = DB_intens * np.sqrt(1/float(intens_list[j]) + 1/float(monitor[j]))
                else: DB_err = np.sqrt(float(intens_list[j])) / float(monitor[j])

                scan_slitsMonitor = self.tableWidget_DB.item(i, 0).text()[:5] + ";" + str(s1hg_list[j]) + ";" + str(s2hg_list[j])
                self.DB_INFO[scan_slitsMonitor] = str(DB_intens) + ";" + str(DB_err)

        if self.tableWidget_DB.rowCount() == 0: return
        else: self.f_DB_assign()

    def f_DB_assign(self):

        DB_list = []
        for DB_scan_number in self.DB_INFO: DB_list.append(DB_scan_number.split(";")[0])

        for i in range(self.tableWidget_scans.rowCount()):
            scan_number = self.tableWidget_scans.item(i, 0).text()[:5]

            # find nearest DB file if there are several of them
            if len(DB_list) == 0: FILE_DB = ""
            elif len(DB_list) == 1: FILE_DB = DB_list[0][:5]
            else:
                if self.checkBox_rearrangeDbAfter.isChecked():
                    for j, DB_scan in enumerate(DB_list):
                        FILE_DB = DB_scan[:5]
                        if int(DB_scan[:5]) > int(scan_number[:5]): break
                else:
                    for j, DB_scan in enumerate(reversed(DB_list)):
                        FILE_DB = DB_scan[:5]
                        if int(DB_scan[:5]) < int(scan_number[:5]): break

            self.tableWidget_scans.item(i, 1).setText(FILE_DB)

    ##<--

    ##--> SFM
    def f_SFM_detectorImage_load(self):

        if self.comboBox_SFM_scan.currentText() == "": return

        self.comboBox_SFM_detectorImage_incidentAngle.clear()
        self.comboBox_SFM_detectorImage_polarisation.clear()
        self.comboBox_SFM_2Dmap_polarisation.clear()

        # we need to find full path for the SFM file from the table
        for i in range(0, self.tableWidget_scans.rowCount()):
            self.SFM_FILE = self.tableWidget_scans.item(i, 2).text() if self.tableWidget_scans.item(i, 0).text() == self.comboBox_SFM_scan.currentText() else self.SFM_FILE

        file = loader.H5Loader(self.SFM_FILE)
        if not file.is_ok():
            print("Error reading file %s." % self.SFM_FILE)
            return

        if not self.roiLocked == [] and self.checkBox_SFM_detectorImage_lockRoi.isChecked(): original_roi_coord = np.array(self.roiLocked[0])
        else: original_roi_coord = file.get_roi()

        roi_width = int(str(original_roi_coord[3])[:-2]) - int(str(original_roi_coord[2])[:-2])

        # ROI
        self.lineEdit_SFM_detectorImage_roiX_left.setText(str(original_roi_coord[2])[:-2])
        self.lineEdit_SFM_detectorImage_roiX_right.setText(str(original_roi_coord[3])[:-2])
        self.lineEdit_SFM_detectorImage_roiY_bottom.setText(str(original_roi_coord[1])[:-2])
        self.lineEdit_SFM_detectorImage_roiY_top.setText(str(original_roi_coord[0])[:-2])

        # BKG ROI
        if not self.roiLocked == [] and self.checkBox_SFM_detectorImage_lockRoi.isChecked(): self.lineEdit_SFM_detectorImage_roi_bkgX_right.setText(str(self.roiLocked[1]))
        else: self.lineEdit_SFM_detectorImage_roi_bkgX_right.setText(str(int(self.lineEdit_SFM_detectorImage_roiX_left.text()) - roi_width))
        self.lineEdit_SFM_detectorImage_roi_bkgX_left.setText(str(int(self.lineEdit_SFM_detectorImage_roi_bkgX_right.text()) - roi_width))

        for index, th in enumerate(file.get_th()):
            self.comboBox_SFM_detectorImage_incidentAngle.addItem(str(round(th, 3)))

        det_uu_list, det_dd_list, det_du_list, det_ud_list = file.get_ponos_pol()

        if len(file.get_ponos_types()) == 1:
            for item in (self.comboBox_SFM_detectorImage_polarisation, self.comboBox_SFM_2Dmap_polarisation): item.addItem("uu")

        for polarisation in file.get_ponos_types():
            det_list = None
            if polarisation == "data_uu": det_list = det_uu_list
            elif polarisation == "data_dd": det_list = det_dd_list
            elif polarisation == "data_du": det_list = det_du_list
            elif polarisation == "data_ud": det_list = det_ud_list
            else: continue

            if np.any(np.array(det_list)):
                for item in (self.comboBox_SFM_detectorImage_polarisation, self.comboBox_SFM_2Dmap_polarisation): item.addItem(polarisation[-2:])

        self.comboBox_SFM_detectorImage_polarisation.setCurrentIndex(0)
        self.comboBox_SFM_2Dmap_polarisation.setCurrentIndex(0)

    def f_SFM_detectorImage_draw(self):

        if self.comboBox_SFM_detectorImage_polarisation.currentText() == "" or self.comboBox_SFM_detectorImage_incidentAngle.currentText() == "": return

        for item in (self.graphicsView_SFM_detectorImage, self.graphicsView_SFM_detectorImage_roi): item.clear()

        if self.SFM_FILE == "": return

        file = loader.H5Loader(self.SFM_FILE)
        if not file.is_ok():
            print("Error reading file %s." % self.SFM_FILE)
            return
        self.th_current = self.comboBox_SFM_detectorImage_incidentAngle.currentText()

        self.th_list = file.get_th()
        self.tth_list = file.get_tth()
        self.s1hg_list = file.get_s1hg()
        self.s2hg_list = file.get_s2hg()
        time_list = file.get_time()

        psdUU, psdDD, psdDU, psdUD = file.get_psd_pol()
        psdUnpol = file.get_psd()
        detector_images = None

        for i in file.get_det_types():
            if i not in ("psd", "psd_uu", "psd_dd", "psd_du", "psd_ud"): continue
            scan_psd = "psd" if i == "psd" else "psd_" + self.comboBox_SFM_detectorImage_polarisation.currentText()
            if scan_psd == "psd": detector_images = psdUnpol
            elif scan_psd == "psd_uu": detector_images = psdUU
            elif scan_psd == "psd_dd": detector_images = psdDD
            elif scan_psd == "psd_du": detector_images = psdDU
            elif scan_psd == "psd_ud": detector_images = psdUD

        for index, th in enumerate(self.th_list):
            # check th
            if self.th_current == str(round(th, 3)):
                self.lineEdit_SFM_detectorImage_slits_s1hg.setText(str(self.s1hg_list[index]))
                self.lineEdit_SFM_detectorImage_slits_s2hg.setText(str(self.s2hg_list[index]))
                self.lineEdit_SFM_detectorImage_time.setText(str(time_list[index]))

                # seems to be a bug in numpy arrays imported from hdf5 files. Problem is solved after I subtract ZEROs array with the same dimentions.
                detector_image = np.around(detector_images[index], decimals=0).astype(int)
                detector_image = np.subtract(detector_image, np.zeros((detector_image.shape[0], detector_image.shape[1])))
                # integrate detector image with respect to ROI Y coordinates
                detector_image_int = detector_image[int(self.lineEdit_SFM_detectorImage_roiY_top.text()): int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()), :].sum(axis=0).astype(int)

                self.graphicsView_SFM_detectorImage.setImage(detector_image, axes={'x':1, 'y':0}, levels=(0,0.1))
                self.graphicsView_SFM_detectorImage_roi.addItem(pg.PlotCurveItem(y = detector_image_int, pen=pg.mkPen(color=(0, 0, 0), width=2), brush=pg.mkBrush(color=(255, 0, 0), width=3)))

                if self.comboBox_SFM_detectorImage_colorScheme.currentText() == "White / Black":
                    self.color_det_image = np.array([[0, 0, 0, 255], [255, 255, 255, 255], [255, 255, 255, 255]], dtype=np.ubyte)
                elif self.comboBox_SFM_detectorImage_colorScheme.currentText() == "Green / Blue":
                    self.color_det_image = np.array([[0, 0, 255, 255], [255, 0, 0, 255], [0, 255, 0, 255]], dtype=np.ubyte)
                pos = np.array([0.0, 0.1, 1.0])

                self.graphicsView_SFM_detectorImage.setColorMap(pg.ColorMap(pos, self.color_det_image))

                # add ROI rectangular
                spots_ROI_detInt = []
                if self.roi_draw: self.graphicsView_SFM_detectorImage.removeItem(self.roi_draw)
                if self.roi_draw_bkg: self.graphicsView_SFM_detectorImage.removeItem(self.roi_draw_bkg)

                # add ROI rectangular
                spots_ROI_det_view = {'x': (int(self.lineEdit_SFM_detectorImage_roiX_left.text()), int(self.lineEdit_SFM_detectorImage_roiX_right.text()), int(self.lineEdit_SFM_detectorImage_roiX_right.text()), int(self.lineEdit_SFM_detectorImage_roiX_left.text()), int(self.lineEdit_SFM_detectorImage_roiX_left.text())),
                                'y': (int(self.lineEdit_SFM_detectorImage_roiY_top.text()), int(self.lineEdit_SFM_detectorImage_roiY_top.text()), int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()), int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()), int(self.lineEdit_SFM_detectorImage_roiY_top.text()))}

                self.roi_draw = pg.PlotDataItem(spots_ROI_det_view, pen=pg.mkPen(255, 255, 255), connect="all")
                self.graphicsView_SFM_detectorImage.addItem(self.roi_draw)

                # add BKG ROI rectangular
                if self.checkBox_reductions_subtractBkg.isChecked():
                    spots_ROI_det_view = {'x': (int(self.lineEdit_SFM_detectorImage_roi_bkgX_left.text()), int(self.lineEdit_SFM_detectorImage_roi_bkgX_right.text()),
                                                int(self.lineEdit_SFM_detectorImage_roi_bkgX_right.text()), int(self.lineEdit_SFM_detectorImage_roi_bkgX_left.text()),
                                                int(self.lineEdit_SFM_detectorImage_roi_bkgX_left.text())),
                                            'y': (int(self.lineEdit_SFM_detectorImage_roiY_top.text()), int(self.lineEdit_SFM_detectorImage_roiY_top.text()),
                                                int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()), int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()),
                                                int(self.lineEdit_SFM_detectorImage_roiY_top.text()))}

                    self.roi_draw_bkg = pg.PlotDataItem(spots_ROI_det_view, pen=pg.mkPen(color=(255, 255, 255), style=QtCore.Qt.DashLine), connect="all")
                    self.graphicsView_SFM_detectorImage.addItem(self.roi_draw_bkg)

                if self.roi_draw_int: self.graphicsView_SFM_detectorImage_roi.removeItem(self.roi_draw_int)

                for i in range(0, detector_image_int.max()):
                    spots_ROI_detInt.append({'x': int(self.lineEdit_SFM_detectorImage_roiX_left.text()), 'y': i})
                    spots_ROI_detInt.append({'x': int(self.lineEdit_SFM_detectorImage_roiX_right.text()), 'y': i})

                self.roi_draw_int = pg.ScatterPlotItem(spots=spots_ROI_detInt, size=1, pen=pg.mkPen(255, 0, 0))
                self.graphicsView_SFM_detectorImage_roi.addItem(self.roi_draw_int)

                break

        # Show "integrated roi" part
        if self.sender().objectName() == "pushButton_SFM_detectorImage_showIntegratedRoi":
            (height, trigger) = (420, False) if self.trigger_showDetInt else (510, True)
            self.graphicsView_SFM_detectorImage.setGeometry(QtCore.QRect(0, 30, 577, height))
            self.trigger_showDetInt = trigger

    def f_SFM_reflectivityPreview_load(self):

        self.graphicsView_SFM_reflectivityPreview.getPlotItem().clear()
        bkg_skip = 0

        self.SFM_export_Qz, self.SFM_export_I, self.SFM_export_dI, self.SFM_export_resolution = [], [], [], []

        # change interface (Include ang resolution..., Use original Sared way...)
        self.checkBox_export_resolutionLikeSared.setEnabled(True if self.checkBox_export_addResolutionColumn.isChecked() else False)

        # change interface (Scale factor, DB correction, DB attenuator)
        if self.checkBox_reductions_normalizeByDB.isChecked():
            hidden = [False, False, True, True]
            self.checkBox_reductions_scaleFactor.setChecked(False)
        else: hidden = [True, True, False, False]

        for index, element in enumerate([self.checkBox_reductions_attenuatorDB, self.lineEdit_reductions_attenuatorDB, self.checkBox_reductions_scaleFactor, self.lineEdit_reductions_scaleFactor]):
            element.setHidden(hidden[index])

        if self.comboBox_SFM_scan.currentText() == "": return

        # Input checkups
        self.statusbar.clearMessage()

        if self.checkBox_reductions_overilluminationCorr.isChecked() or self.checkBox_SFM_reflectivityPreview_showOverillumination.isChecked():
            try:
                _ = float(self.lineEdit_sampleLen.text())
            except:
                self.statusbar.showMessage("Error: Recheck 'Sample length' field.")

        if self.checkBox_reductions_normalizeByDB.isChecked() and self.tableWidget_DB.rowCount() == 0:
            self.statusbar.showMessage("Error: Direct beam file is missing.")

        if int(self.lineEdit_SFM_detectorImage_roiX_left.text()) > int(self.lineEdit_SFM_detectorImage_roiX_right.text()) or int(self.lineEdit_SFM_detectorImage_roiY_bottom.text()) < int(self.lineEdit_SFM_detectorImage_roiY_top.text()) or (self.checkBox_reductions_subtractBkg.checkState() and int(self.lineEdit_SFM_detectorImage_roi_bkgX_left.text()) < 0):
            self.statusbar.showMessage("Error: Recheck your ROI input.")

        self.scaleFactor = 1
        if self.checkBox_reductions_scaleFactor.isChecked():
            try:
                self.scaleFactor = 10 if self.lineEdit_reductions_scaleFactor.text() == "" else float(self.lineEdit_reductions_scaleFactor.text())
            except:
                self.statusbar.showMessage("Error: Recheck 'Scale Factor' field.")

        self.DB_attenFactor = 1
        if self.checkBox_reductions_attenuatorDB.isChecked():
            try:
                self.DB_attenFactor = 10 if self.lineEdit_reductions_attenuatorDB.text() == "" else float(self.lineEdit_reductions_attenuatorDB.text())
            except:
                self.statusbar.showMessage("Error: Recheck 'Direct Beam Attenuator Factor' field.")

        if self.lineEdit_reductions_subtractBkg_Skip.text():
            try:
                bkg_skip = float(self.lineEdit_reductions_subtractBkg_Skip.text())
            except:
                self.statusbar.showMessage("Error: Recheck 'Skip background' field.")

        try:
            _ = 1/float(self.lineEdit_instrument_wavelength.text())
            _ = float(self.lineEdit_instrument_wavelengthResolution.text())
            _ = float(self.lineEdit_instrument_distanceS1ToSample.text())
            _ = float(self.lineEdit_instrument_distanceS2ToSample.text())
            _ = float(self.lineEdit_instrument_distanceSampleToDetector.text())
            _ = float(self.lineEdit_instrument_sampleCurvature.text())
            _ = float(self.lineEdit_instrument_offsetFull.text())
        except:
            self.statusbar.showMessage("Error: Recheck 'Instrument / Corrections' tab for typos.")

        if self.statusbar.currentMessage(): return

        # Define analized file and DB
        for i in range(0, self.tableWidget_scans.rowCount()):
            if self.tableWidget_scans.item(i, 0).text() == self.comboBox_SFM_scan.currentText(): self.SFM_FILE = self.tableWidget_scans.item(i, 2).text()
        self.SFM_DB_FILE = self.comboBox_SFM_DB.currentText()

        # Open analized file
        file = loader.H5Loader(self.SFM_FILE)
        if not file.is_ok():
            print("Error reading file %s." % self.SFM_FILE)
            return

        roi_coord_Y = [int(self.lineEdit_SFM_detectorImage_roiY_top.text()), int(self.lineEdit_SFM_detectorImage_roiY_bottom.text())]
        roi_coord_X = [int(self.lineEdit_SFM_detectorImage_roiX_left.text()), int(self.lineEdit_SFM_detectorImage_roiX_right.text())]
        roi_coord_X_BKG = [int(self.lineEdit_SFM_detectorImage_roi_bkgX_left.text()), int(self.lineEdit_SFM_detectorImage_roi_bkgX_right.text())]

        # recalculate if ROI was changed
        if not roi_coord_Y == self.roi_oldCoord_Y: self.SFMFileAlreadyAnalized = ""
        self.roi_oldCoord_Y = roi_coord_Y

        monitor_list = file.get_mon()
        monitor_uu_list, monitor_dd_list, monitor_du_list, monitor_ud_list = file.get_mon_pol()
        time_list = file.get_time()

        if not self.SFM_FILE == self.SFMFileAlreadyAnalized:
            self.SFM_psdUU = self.SFM_psdDD = self.SFM_psdUD = self.SFM_psdDU = []

        # get or create 2-dimentional intensity array for each polarisation

        sampleCurvature_recalc = True if self.sampleCurvature_last == [i.text() for i in [self.lineEdit_instrument_sampleCurvature, self.lineEdit_SFM_detectorImage_roiX_left, self.lineEdit_SFM_detectorImage_roiX_right, self.lineEdit_SFM_detectorImage_roiY_bottom, self.lineEdit_SFM_detectorImage_roiY_top]] else False

        # avoid reSUM of intensity after each action
        # reSUM if we change SFM file or Sample curvature
        if not (self.SFM_FILE == self.SFMFileAlreadyAnalized and sampleCurvature_recalc):
            if file.is_pol():
                self.SFM_psdUU, self.SFM_psdDD, self.SFM_psdDU, self.SFM_psdUD = file.get_psd_pol()
                if self.SFM_psdUU != None: self.SFM_psdUU = self.SFM_psdUU[:, int(roi_coord_Y[0]): int(roi_coord_Y[1]), :].sum(axis=1)
                if self.SFM_psdDD != None: self.SFM_psdDD = self.SFM_psdDD[:, int(roi_coord_Y[0]): int(roi_coord_Y[1]), :].sum(axis=1)
                if self.SFM_psdDU != None: self.SFM_psdDU = self.SFM_psdDU[:, int(roi_coord_Y[0]): int(roi_coord_Y[1]), :].sum(axis=1)
                if self.SFM_psdUD != None: self.SFM_psdUD = self.SFM_psdUD[:, int(roi_coord_Y[0]): int(roi_coord_Y[1]), :].sum(axis=1)
            else:
                self.SFM_psdUU = file.get_psd()[:, int(roi_coord_Y[0]) : int(roi_coord_Y[1]), :].sum(axis=1)

        if not self.SFM_FILE == self.SFMFileAlreadyAnalized: self.SFMFileAlreadyAnalized, self.sampleCurvature_last = self.SFM_FILE, "0"

        # Sample curvature correction - we need to adjust integrated 2D map when we first make it
        # perform correction if it was changed on the form
        if not sampleCurvature_recalc:

            for index, SFM_curvatureCorrection in enumerate([self.SFM_psdUU, self.SFM_psdDU, self.SFM_psdUD, self.SFM_psdDD]):

                if self.lineEdit_instrument_sampleCurvature.text() == "0": continue
                if SFM_curvatureCorrection == []: continue

                SFM_curvatureCorrection_slice = SFM_curvatureCorrection[:, roi_coord_X[0]:roi_coord_X[1]]

                detImage_recalc = [[],[],[]] # x, y, value

                for x, col in enumerate(np.flipud(np.rot90(SFM_curvatureCorrection_slice))):
                    displacement = x * np.tan(float(self.lineEdit_instrument_sampleCurvature.text()))
                    for y, value in enumerate(col):
                        detImage_recalc[0].append(x)
                        detImage_recalc[1].append(y + displacement)
                        detImage_recalc[2].append(value)
                np.rot90(SFM_curvatureCorrection_slice, -1)

                # find middle of roi to define zero level
                roi_coord_X_middle = (SFM_curvatureCorrection_slice.shape[1]) / 2
                zero_level = int(round(roi_coord_X_middle * np.tan(float(self.lineEdit_instrument_sampleCurvature.text())) - min(detImage_recalc[1])))

                grid_x, grid_y = np.mgrid[0:SFM_curvatureCorrection_slice.shape[1]:1, min(detImage_recalc[1]):max(detImage_recalc[1]):1]
                SFM_curvatureCorrection_slice = np.flipud(np.rot90(griddata((detImage_recalc[0], detImage_recalc[1]), detImage_recalc[2], (grid_x, grid_y), method="linear", fill_value=float(0))))[zero_level:zero_level+SFM_curvatureCorrection_slice.shape[0], :]

                SFM_curvatureCorrection[:, roi_coord_X[0]:roi_coord_X[1]] = SFM_curvatureCorrection_slice

                if index == 0: self.SFM_psdUU = SFM_curvatureCorrection
                elif index == 1: self.SFM_psdDU = SFM_curvatureCorrection
                elif index == 2: self.SFM_psdUD = SFM_curvatureCorrection
                elif index == 3: self.SFM_psdDD = SFM_curvatureCorrection

            self.sampleCurvature_last = [i.text() for i in [self.lineEdit_instrument_sampleCurvature, self.lineEdit_SFM_detectorImage_roiX_left, self.lineEdit_SFM_detectorImage_roiX_right, self.lineEdit_SFM_detectorImage_roiY_bottom, self.lineEdit_SFM_detectorImage_roiY_top]]

        for colorIndex, SFM_scanIntens in enumerate([self.SFM_psdUU, self.SFM_psdDU, self.SFM_psdUD, self.SFM_psdDD]):

            SFM_export_Qz_onePol, SFM_export_I_onePol, SFM_export_dI_onePol, SFM_export_resolution_onePol = [], [], [], []

            plot_I, plot_angle, plot_dI_err_bottom, plot_dI_err_top, plot_overillumination = [], [], [], [], []

            if isinstance(SFM_scanIntens, list) and SFM_scanIntens == []: continue

            if colorIndex == 0: color, monitorData = [0, 0, 0], [monitor_list if np.count_nonzero(monitor_uu_list) == 0 else monitor_uu_list][0] # ++
            elif colorIndex == 1: color, monitorData = [0, 0, 255], monitor_du_list # -+
            elif colorIndex == 2: color, monitorData = [0, 255, 0], monitor_ud_list # +-
            elif colorIndex == 3: color, monitorData = [255, 0, 0], monitor_dd_list # --

            for index, th in enumerate(self.th_list):
                th = th - float(self.lineEdit_instrument_offsetFull.text()) # th offset

                # read motors
                Qz = (4 * np.pi / float(self.lineEdit_instrument_wavelength.text())) * np.sin(np.radians(th))
                s1hg, s2hg, monitor = self.s1hg_list[index], self.s2hg_list[index], monitorData[index]

                if not self.checkBox_reductions_overilluminationCorr.isChecked():
                    overillCorr, FWHM_proj = 1, s2hg
                    overillCorr_plot = self.f_overilluminationCorrCoeff(s1hg, s2hg, round(th, 4))[0]
                else:
                    overillCorr, FWHM_proj = self.f_overilluminationCorrCoeff(s1hg, s2hg, round(th, 4))
                    overillCorr_plot = overillCorr

                # calculate resolution in Gunnar's Sared way or other (also using overillumination correction)
                if self.checkBox_export_resolutionLikeSared.isChecked():
                    Resolution = np.sqrt(((2 * np.pi / float(self.lineEdit_instrument_wavelength.text())) ** 2) * ((np.cos(np.radians(th))) ** 2) * (0.68 ** 2) * ((s1hg ** 2) + (s2hg ** 2)) / ((float( self.lineEdit_instrument_distanceS1ToSample.text()) - float( self.lineEdit_instrument_distanceS2ToSample.text())) ** 2) + ((float(self.lineEdit_instrument_wavelengthResolution.text()) ** 2) * (Qz ** 2)))
                else:
                    d_alpha = np.arctan((s1hg + [s2hg if FWHM_proj == s2hg else FWHM_proj][0]) / (
                            (float(self.lineEdit_instrument_distanceS1ToSample.text()) - float(self.lineEdit_instrument_distanceS2ToSample.text())) * 2))
                    if self.comboBox_export_angle.currentText() == "Qz":
                        k_0 = 2 * np.pi / float(self.lineEdit_instrument_wavelength.text())
                        Resolution = np.sqrt((k_0 ** 2) * ( (((np.cos(np.radians(th))) ** 2) * d_alpha ** 2) + ((float(self.lineEdit_instrument_wavelengthResolution.text()) ** 2) * ((np.sin(np.radians(th))) ** 2))))
                    else: Resolution = d_alpha if self.comboBox_export_angle.currentText() == "Radians" else np.degrees(d_alpha)

                # Save resolution in sigma rather than in FWHM units
                Resolution = Resolution / (2 * np.sqrt(2 * np.log(2)))

                # analyze integrated intensity for ROI
                if SFM_scanIntens is None:
                    Intens = 0
                    Intens_bkg = 0
                else:
                    Intens = sum(SFM_scanIntens[index][roi_coord_X[0]: roi_coord_X[1]])
                    Intens_bkg = sum(SFM_scanIntens[index][roi_coord_X_BKG[0] : roi_coord_X_BKG[1]])

                # minus background, divide by monitor, overillumination correct + calculate errors
                if not Intens > 0: Intens = 0
                # I want to avoid error==0 if intens==0
                if Intens == 0: IntensErr = 1
                else: IntensErr = np.sqrt(Intens)

                if self.checkBox_reductions_subtractBkg.isChecked() and Qz > bkg_skip:
                    if Intens_bkg > 0:
                        IntensErr = np.sqrt(Intens + Intens_bkg)
                        Intens = Intens - Intens_bkg

                if self.checkBox_reductions_divideByMonitorOrTime.isChecked():

                    if self.comboBox_reductions_divideByMonitorOrTime.currentText() == "monitor":
                        monitor = monitor_list[index]
                        if Intens == 0: IntensErr = IntensErr / monitor
                        else: IntensErr = (Intens / monitor) * np.sqrt((IntensErr / Intens) ** 2 + (1 / monitor))
                    elif self.comboBox_reductions_divideByMonitorOrTime.currentText() == "time":
                        monitor = time_list[index]
                        IntensErr = IntensErr / monitor

                    Intens = Intens / monitor

                if self.checkBox_reductions_overilluminationCorr.isChecked() and overillCorr > 0:
                    IntensErr = IntensErr / overillCorr
                    Intens = Intens / overillCorr

                if self.checkBox_reductions_normalizeByDB.isChecked():
                    try:
                        DB_intens = float(self.DB_INFO[self.SFM_DB_FILE + ";" + str(s1hg) + ";" + str(s2hg)].split(";")[0]) * self.DB_attenFactor
                        DB_err = overillCorr * float(self.DB_INFO[self.SFM_DB_FILE + ";" + str(s1hg) + ";" + str(s2hg)].split(";")[1]) * self.DB_attenFactor
                        IntensErr = (Intens / DB_intens) * np.sqrt((DB_err / DB_intens) ** 2 + (IntensErr / Intens) ** 2)
                        Intens = Intens / DB_intens
                        self.statusbar.clearMessage()
                    except:
                        # if we try DB file without neccesary slits combination measured - show error message + redraw reflectivity_preview
                        self.statusbar.showMessage("Error: Choose another DB file for this SFM data file.")
                        self.checkBox_reductions_normalizeByDB.setCheckState(0)

                if self.checkBox_reductions_scaleFactor.isChecked():
                    IntensErr = IntensErr / self.scaleFactor
                    Intens = Intens / self.scaleFactor

                try:
                    show_first, show_last = int(self.lineEdit_SFM_reflectivityPreview_skipPoints_left.text()), len(self.th_list)-int(self.lineEdit_SFM_reflectivityPreview_skipPoints_right.text())
                except: show_first, show_last = 0, len(self.th_list)

                if not Intens < 0 and index < show_last and index >= show_first:
                    # I need this for "Reduce SFM" option. First - store one pol.
                    SFM_export_Qz_onePol.append(Qz)
                    SFM_export_I_onePol.append(Intens)
                    SFM_export_dI_onePol.append(IntensErr)
                    SFM_export_resolution_onePol.append(Resolution)

                    if Intens > 0:
                        plot_I.append(np.log10(Intens))
                        plot_angle.append(Qz)
                        plot_dI_err_top.append(abs(np.log10(Intens + IntensErr) - np.log10(Intens)))

                        plot_overillumination.append(overillCorr_plot)

                        if Intens > IntensErr: plot_dI_err_bottom.append(np.log10(Intens) - np.log10(Intens - IntensErr))
                        else: plot_dI_err_bottom.append(0)

                    if self.comboBox_SFM_reflectivityPreview_view_reflectivity.currentText() == "Lin":
                        plot_I.pop()
                        plot_I.append(Intens)
                        plot_dI_err_top.pop()
                        plot_dI_err_top.append(IntensErr)
                        plot_dI_err_bottom.pop()
                        plot_dI_err_bottom.append(IntensErr)

                    if self.comboBox_SFM_reflectivityPreview_view_angle.currentText() == "Deg":
                        plot_angle.pop()
                        plot_angle.append(th)

            # I need this for "Reduse SFM" option. Second - combine all shown pol in one list variable.
            # polarisations are uu, dd, ud, du
            self.SFM_export_Qz.append(SFM_export_Qz_onePol)
            self.SFM_export_I.append(SFM_export_I_onePol)
            self.SFM_export_dI.append(SFM_export_dI_onePol)
            self.SFM_export_resolution.append(SFM_export_resolution_onePol)

            if self.checkBox_SFM_reflectivityPreview_includeErrorbars.isChecked():
                s1 = pg.ErrorBarItem(x=np.array(plot_angle), y=np.array(plot_I), top=np.array(plot_dI_err_top), bottom=np.array(plot_dI_err_bottom), pen=pg.mkPen(color[0], color[1], color[2]), brush=pg.mkBrush(color[0], color[1], color[2]))
                self.graphicsView_SFM_reflectivityPreview.addItem(s1)

            s2 = pg.ScatterPlotItem(x=plot_angle, y=plot_I, symbol="o", size=4, pen=pg.mkPen(color[0], color[1], color[2]), brush=pg.mkBrush(color[0], color[1], color[2]))
            self.graphicsView_SFM_reflectivityPreview.addItem(s2)

            if self.checkBox_SFM_reflectivityPreview_showOverillumination.isChecked():
                s3 = pg.PlotCurveItem(x=plot_angle, y=plot_overillumination, pen=pg.mkPen(color=(255, 0, 0), width=1), brush=pg.mkBrush(color=(255, 0, 0), width=1) )
                self.graphicsView_SFM_reflectivityPreview.addItem(s3)

            if self.checkBox_SFM_reflectivityPreview_showZeroLevel.isChecked():
                if self.comboBox_SFM_reflectivityPreview_view_reflectivity.currentText() == "Lin": level = np.array([1, 1])
                else: level = np.array([0, 0])
                s4 = pg.PlotCurveItem(x=np.array([min(plot_angle), max(plot_angle)]), y=level, pen=pg.mkPen(color=(0, 0, 255), width=1), brush=pg.mkBrush(color=(255, 0, 0), width=1) )
                self.graphicsView_SFM_reflectivityPreview.addItem(s4)

    def f_SFM_2Dmap_draw(self):

        self.SFM_intDetectorImage = []

        for item in (self.graphicsView_SFM_2Dmap_Qxz_theta, self.graphicsView_SFM_2Dmap): item.clear()

        # change interface if for different views
        ELEMENTS = [self.label_SFM_2Dmap_rescaleImage_x, self.label_SFM_2Dmap_rescaleImage_y, self.horizontalSlider_SFM_2Dmap_rescaleImage_x, self.horizontalSlider_SFM_2Dmap_rescaleImage_y, self.label_SFM_2Dmap_lowerNumberOfPointsBy, self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy, self.label_SFM_2Dmap_QxzThreshold, self.comboBox_SFM_2Dmap_QxzThreshold, self.label_SFM_2Dmap_view_scale, self.comboBox_SFM_2Dmap_view_scale, self.checkBox_SFM_2Dmap_flip]

        if self.comboBox_SFM_2Dmap_axes.currentText() == "Pixel vs. Point": visible, geometry = [True, True, True, True, False, False, False, False, True, True, False], [0, 0, 0, 0]
        elif self.comboBox_SFM_2Dmap_axes.currentText() == "Qx vs. Qz": visible, geometry = [False, False, False, False, True, True, True, True, False, False, False], [0, 30, 577, 522]
        elif self.comboBox_SFM_2Dmap_axes.currentText() == "Alpha_i vs. Alpha_f": visible, geometry = [False, False, False, False, True, True, False, False, True, True, True], [0, 0, 0, 0]

        self.graphicsView_SFM_2Dmap_Qxz_theta.setGeometry(QtCore.QRect(geometry[0], geometry[1], geometry[2], geometry[3]))
        for index, index_visible in enumerate(visible): ELEMENTS[index].setVisible(index_visible)

        if self.SFM_FILE == "": return

        # start over if we selected nes SFM scan
        if not self.SFMFile2dCalculatedParams == [] and not self.SFMFile2dCalculatedParams[0] == self.SFM_FILE:
            self.comboBox_SFM_2Dmap_axes.setCurrentIndex(0)
            self.SFMFile2dCalculatedParams, self.res_aif = [], []

        try:
            self.graphicsView_SFM_2Dmap.removeItem(self.roi_draw_2Dmap)
        except: True

        # load selected integrated detector image
        if self.comboBox_SFM_2Dmap_polarisation.count() == 1: self.SFM_intDetectorImage = self.SFM_psdUU
        else:
            if self.comboBox_SFM_2Dmap_polarisation.currentText() == "uu": self.SFM_intDetectorImage = self.SFM_psdUU
            elif self.comboBox_SFM_2Dmap_polarisation.currentText() == "du": self.SFM_intDetectorImage = self.SFM_psdDU
            elif self.comboBox_SFM_2Dmap_polarisation.currentText() == "ud": self.SFM_intDetectorImage = self.SFM_psdUD
            elif self.comboBox_SFM_2Dmap_polarisation.currentText() == "dd": self.SFM_intDetectorImage = self.SFM_psdDD

        if isinstance(self.SFM_intDetectorImage, list) and self.SFM_intDetectorImage == []: return

        # create log array for log view
        self.SFM_intDetectorImage_log = np.log10(np.where(self.SFM_intDetectorImage < 1, 0.1, self.SFM_intDetectorImage))

        # Pixel to Angle conversion for "Qx vs Qz" and "alpha_i vs alpha_f" 2d maps
        if self.comboBox_SFM_2Dmap_axes.currentText() in ["Qx vs. Qz", "Alpha_i vs. Alpha_f"]:
            # recalculate only if something was changed
            if self.res_aif == [] or not self.SFMFile2dCalculatedParams == [self.SFM_FILE, self.comboBox_SFM_2Dmap_polarisation.currentText(), self.lineEdit_SFM_detectorImage_roiX_left.text(), self.lineEdit_SFM_detectorImage_roiX_right.text(), self.lineEdit_instrument_wavelength.text(), self.lineEdit_instrument_distanceSampleToDetector.text(), self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy.currentText(), self.comboBox_SFM_2Dmap_QxzThreshold.currentText(), self.lineEdit_instrument_sampleCurvature.text(), self.checkBox_SFM_2Dmap_flip.checkState()]:
                self.spots_Qxz, self.SFM_intDetectorImage_Qxz, self.SFM_intDetectorImage_aif, self.SFM_intDetectorImage_values_array = [], [], [[],[]], []

                # flip image in Aif mode (checkbox) -- this requires another ROI
                if self.comboBox_SFM_2Dmap_axes.currentText() == "Alpha_i vs. Alpha_f":
                    # we need to flip the detector (X) for correct calculation
                    self.SFM_intDetectorImage = np.flip(self.SFM_intDetectorImage, 1)
                    roi_middle = round((self.SFM_intDetectorImage.shape[1] - float(self.lineEdit_SFM_detectorImage_roiX_left.text()) +
                                            self.SFM_intDetectorImage.shape[1] - float(self.lineEdit_SFM_detectorImage_roiX_right.text())) / 2)

                mm_per_pix = 300 / self.SFM_intDetectorImage.shape[1]

                for theta_i, tth_i, det_image_i in zip(self.th_list, self.tth_list, self.SFM_intDetectorImage):
                    for pixel_num, value in enumerate(det_image_i):
                        # Reduce number of points to draw (to save RAM)
                        if pixel_num % int(self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy.currentText()) == 0:

                            theta_f = tth_i - theta_i # theta F in deg
                            delta_theta_F_mm = (pixel_num - roi_middle) * mm_per_pix
                            delta_theta_F_deg = np.degrees(np.arctan(delta_theta_F_mm / float(self.lineEdit_instrument_distanceSampleToDetector.text()))) # calculate delta theta F in deg
                            theta_f = theta_f + delta_theta_F_deg * (-1 if self.checkBox_SFM_2Dmap_flip.isChecked() else 1) # final theta F in deg for the point

                            # convert to Q
                            Qx = (2 * np.pi / float(self.lineEdit_instrument_wavelength.text())) * (np.cos(np.radians(theta_f)) - np.cos(np.radians(theta_i)))
                            Qz = (2 * np.pi / float(self.lineEdit_instrument_wavelength.text())) * (np.sin(np.radians(theta_f)) + np.sin(np.radians(theta_i)))

                            for arr, val in zip((self.SFM_intDetectorImage_Qxz, self.SFM_intDetectorImage_aif[0], self.SFM_intDetectorImage_aif[1], self.SFM_intDetectorImage_values_array), ([Qx, Qz, value], theta_i, theta_f, value)): arr.append(val)

                            # define colors - 2 count+ -> green, [0,1] - blue
                            color = [0, 0, 255] if value < int(self.comboBox_SFM_2Dmap_QxzThreshold.currentText()) else [0, 255, 0]

                            self.spots_Qxz.append({'pos': (-Qx, Qz), 'pen': pg.mkPen(color[0], color[1], color[2])})

                if self.comboBox_SFM_2Dmap_axes.currentText() == "Alpha_i vs. Alpha_f":
                    # calculate required number of pixels in Y axis
                    self.resolution_x_pix_deg = self.SFM_intDetectorImage.shape[0] / (max(self.SFM_intDetectorImage_aif[0]) - min(self.SFM_intDetectorImage_aif[0]))
                    self.resolution_y_pix = int(round((max(self.SFM_intDetectorImage_aif[1]) - min(self.SFM_intDetectorImage_aif[1])) * self.resolution_x_pix_deg))

                    grid_x, grid_y = np.mgrid[min(self.SFM_intDetectorImage_aif[0]):max(self.SFM_intDetectorImage_aif[0]):((max(self.SFM_intDetectorImage_aif[0]) - min(self.SFM_intDetectorImage_aif[0]))/len(self.th_list)), min(self.SFM_intDetectorImage_aif[1]):max(self.SFM_intDetectorImage_aif[1]):(max(self.SFM_intDetectorImage_aif[1]) - min(self.SFM_intDetectorImage_aif[1]))/self.resolution_y_pix]

                    self.res_aif = griddata((np.array(self.SFM_intDetectorImage_aif[0]), np.array(self.SFM_intDetectorImage_aif[1])), np.array(self.SFM_intDetectorImage_values_array), (grid_x, grid_y), method="linear", fill_value=float(0))

                    # create log array for log view
                    self.res_aif_log = np.log10(np.where(self.res_aif < 1, 0.1, self.res_aif))

                # record params that we used for 2D maps calculation
                self.SFMFile2dCalculatedParams = [self.SFM_FILE, self.comboBox_SFM_2Dmap_polarisation.currentText(), self.lineEdit_SFM_detectorImage_roiX_left.text(), self.lineEdit_SFM_detectorImage_roiX_right.text(), self.lineEdit_instrument_wavelength.text(), self.lineEdit_instrument_distanceSampleToDetector.text(), self.comboBox_SFM_2Dmap_lowerNumberOfPointsBy.currentText(), self.comboBox_SFM_2Dmap_QxzThreshold.currentText(), self.lineEdit_instrument_sampleCurvature.text(),self.checkBox_SFM_2Dmap_flip.checkState()]

        # plot
        if self.comboBox_SFM_2Dmap_axes.currentText() == "Pixel vs. Point":

            image = self.SFM_intDetectorImage_log if self.comboBox_SFM_2Dmap_view_scale.currentText() == "Log" else self.SFM_intDetectorImage

            self.graphicsView_SFM_2Dmap.setImage(image, axes={'x': 1, 'y': 0}, levels=(0, np.max(image)), scale=(int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value()), int(self.horizontalSlider_SFM_2Dmap_rescaleImage_y.value())))
            # add ROI rectangular
            spots_ROI = {'x':(int(self.lineEdit_SFM_detectorImage_roiX_left.text()) * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value()), int(self.lineEdit_SFM_detectorImage_roiX_right.text()) * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value()), int(self.lineEdit_SFM_detectorImage_roiX_right.text()) * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value()), int(self.lineEdit_SFM_detectorImage_roiX_left.text()) * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value()), int(self.lineEdit_SFM_detectorImage_roiX_left.text()) * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value())), 'y':(0,0,self.SFM_intDetectorImage.shape[0] * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_y.value()),self.SFM_intDetectorImage.shape[0] * int(self.horizontalSlider_SFM_2Dmap_rescaleImage_y.value()),0)}

            self.roi_draw_2Dmap = pg.PlotDataItem(spots_ROI, pen=pg.mkPen(255, 255, 255), connect="all")
            self.graphicsView_SFM_2Dmap.addItem(self.roi_draw_2Dmap)

        elif self.comboBox_SFM_2Dmap_axes.currentText() == "Alpha_i vs. Alpha_f":

            image = self.res_aif_log if self.comboBox_SFM_2Dmap_view_scale.currentText() == "Log" else self.res_aif

            self.graphicsView_SFM_2Dmap.setImage(image, axes={'x': 0, 'y': 1}, levels=(0, np.max(image)))
            self.graphicsView_SFM_2Dmap.getImageItem().setRect(QtCore.QRectF(min(self.SFM_intDetectorImage_aif[0]), min(self.SFM_intDetectorImage_aif[1]), max(self.SFM_intDetectorImage_aif[0]) - min(self.SFM_intDetectorImage_aif[0]), max(self.SFM_intDetectorImage_aif[1]) - min(self.SFM_intDetectorImage_aif[1])))
            self.graphicsView_SFM_2Dmap.getView().enableAutoScale()

            # add line at 45 degrees at alfa_f==0
            spots_45 = {'x': (min(self.SFM_intDetectorImage_aif[0]), max(self.SFM_intDetectorImage_aif[0]) - min(self.SFM_intDetectorImage_aif[0])), 'y': (min(self.SFM_intDetectorImage_aif[0]), max(self.SFM_intDetectorImage_aif[0]) - min(self.SFM_intDetectorImage_aif[0])) }
            self.graphicsView_SFM_2Dmap.addItem(pg.PlotDataItem(spots_45, pen=pg.mkPen(255, 255, 255), connect = "all"))

        elif self.comboBox_SFM_2Dmap_axes.currentText() == "Qx vs. Qz":
            s0 = pg.ScatterPlotItem(spots=self.spots_Qxz, size=1)
            self.graphicsView_SFM_2Dmap_Qxz_theta.addItem(s0)

        # hide Y axis in 2D map if "rescale image" is used. Reason - misleading scale
        for item in (self.graphicsView_SFM_2Dmap.view.getAxis("left"), self.graphicsView_SFM_2Dmap.view.getAxis("bottom")): item.setTicks(None)
        if self.horizontalSlider_SFM_2Dmap_rescaleImage_x.value() > 1: self.graphicsView_SFM_2Dmap.view.getAxis("bottom").setTicks([])
        if self.horizontalSlider_SFM_2Dmap_rescaleImage_y.value() > 1: self.graphicsView_SFM_2Dmap.view.getAxis("left").setTicks([])

    def f_SFM_2Dmap_export(self):
        dir_saveFile = self.lineEdit_saveAt.text() if self.lineEdit_saveAt.text() else self.dir_current

        if self.comboBox_SFM_2Dmap_axes.currentText() == "Pixel vs. Point":
            with open(dir_saveFile + self.SFM_FILE[self.SFM_FILE.rfind("/") + 1 : -3] + "_" + self.comboBox_SFM_2Dmap_polarisation.currentText() + " 2Dmap(Pixel vs. Point).dat", "w") as newFile_2Dmap:
                for line in self.SFM_intDetectorImage:
                    for row in line: newFile_2Dmap.write(str(row) + " ")
                    newFile_2Dmap.write("\n")

        elif self.comboBox_SFM_2Dmap_axes.currentText() == "Alpha_i vs. Alpha_f":
            # Matrix
            with open(dir_saveFile + self.SFM_FILE[self.SFM_FILE.rfind("/") + 1 : -3] + "_" + self.comboBox_SFM_2Dmap_polarisation.currentText() + " 2Dmap_(Alpha_i vs. Alpha_f)).dat", "w") as newFile_2Dmap_aif:
                # header
                newFile_2Dmap_aif.write("Alpha_i limits: " + str(min(self.SFM_intDetectorImage_aif[0])) + " : " + str(max(self.SFM_intDetectorImage_aif[0])) +
                                        "   Alpha_f limits: " + str(min(self.SFM_intDetectorImage_aif[1])) + " : " + str(max(self.SFM_intDetectorImage_aif[1])) + " degrees\n")
                for line in np.rot90(self.res_aif):
                    for row in line: newFile_2Dmap_aif.write(str(row) + " ")
                    newFile_2Dmap_aif.write("\n")

            # Points (full)
            with open(dir_saveFile + self.SFM_FILE[self.SFM_FILE.rfind("/") + 1: -3] + "_" + self.comboBox_SFM_2Dmap_polarisation.currentText() + " 2Dmap_(Alpha_i vs. Alpha_f))_Points.dat", "w") as newFile_2Dmap_aifPoints:

                self.SFM_intDetectorImage_values_array, self.SFM_intDetectorImage_aif = [], [[], []]
                roi_middle = round((self.SFM_intDetectorImage.shape[1] - float(self.lineEdit_SFM_detectorImage_roiX_left.text()) +
                                    self.SFM_intDetectorImage.shape[1] - float(self.lineEdit_SFM_detectorImage_roiX_right.text())) / 2)

                mm_per_pix = 300 / self.SFM_intDetectorImage.shape[1]

                for theta_i, tth_i, det_image_i in zip(self.th_list, self.tth_list, self.SFM_intDetectorImage):
                    for pixel_num, value in enumerate(det_image_i):
                        theta_f = tth_i - theta_i # theta F in deg
                        delta_theta_F_mm = (pixel_num - roi_middle) * mm_per_pix
                        delta_theta_F_deg = np.degrees(np.arctan(delta_theta_F_mm / float(self.lineEdit_instrument_distanceSampleToDetector.text()))) # calculate delta theta F in deg
                        theta_f = theta_f + delta_theta_F_deg * (-1 if self.checkBox_SFM_2Dmap_flip.isChecked() else 1) # final theta F in deg for the point

                        for arr, val in zip((self.SFM_intDetectorImage_aif[0], self.SFM_intDetectorImage_aif[1], self.SFM_intDetectorImage_values_array), (theta_i, theta_f, value)): arr.append(val)

                for index in range(len(self.SFM_intDetectorImage_values_array)-1):
                    newFile_2Dmap_aifPoints.write(f"{str(self.SFM_intDetectorImage_aif[0][index])} {str(self.SFM_intDetectorImage_aif[1][index])} {str(self.SFM_intDetectorImage_values_array[index])} \n")

        elif self.comboBox_SFM_2Dmap_axes.currentText() in ["Qx vs. Qz"]:
            with open(dir_saveFile + self.SFM_FILE[self.SFM_FILE.rfind("/") + 1 : -3] + "_" + self.comboBox_SFM_2Dmap_polarisation.currentText() + " points_(Qx, Qz, intens).dat", "w") as newFile_2Dmap_Qxz:
                for line in self.SFM_intDetectorImage_Qxz: newFile_2Dmap_Qxz.write(str(line[0]) + " " + str(line[1]) + " " + str(line[2]) + "\n")

    def f_SFM_roi_update(self):

        roi_width = int(self.lineEdit_SFM_detectorImage_roiX_right.text()) - int(self.lineEdit_SFM_detectorImage_roiX_left.text())

        if not self.sender().objectName() == "lineEdit_SFM_detectorImage_roi_bkgX_right":
            self.lineEdit_SFM_detectorImage_roi_bkgX_left.setText(str(int(self.lineEdit_SFM_detectorImage_roiX_left.text()) - 2 * roi_width))
            self.lineEdit_SFM_detectorImage_roi_bkgX_right.setText(str(int(self.lineEdit_SFM_detectorImage_roiX_left.text()) - roi_width))
        else: self.lineEdit_SFM_detectorImage_roi_bkgX_left.setText(str(int(self.lineEdit_SFM_detectorImage_roi_bkgX_right.text()) - roi_width))

        # record ROI coord for "Lock ROI" checkbox
        self.roiLocked = [[self.lineEdit_SFM_detectorImage_roiY_top.text() + ". ", self.lineEdit_SFM_detectorImage_roiY_bottom.text() + ". ", self.lineEdit_SFM_detectorImage_roiX_left.text() + ". ", self.lineEdit_SFM_detectorImage_roiX_right.text() + ". "], self.lineEdit_SFM_detectorImage_roi_bkgX_right.text()]

        self.f_SFM_detectorImage_draw()
        self.f_SFM_reflectivityPreview_load()
        self.f_SFM_2Dmap_draw()

    ##<--

if __name__ == "__main__":
    QtWidgets.QApplication.setStyle("Fusion")
    app = QtWidgets.QApplication(sys.argv)
    prog = GUI()
    prog.show()
    if ui.qt_ver < 6:
        sys.exit(app.exec_())
    else:
        sys.exit(app.exec())
