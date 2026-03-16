import h5py
import numpy as np


class H5Loader:
    FILE = None
    SCAN = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    monitor_list = []
    monitor_uu_list = []
    monitor_dd_list = []
    monitor_du_list = []
    monitor_ud_list = []
    intens_list = []
    time_list = []

    det_types = []
    detector_images = None
    detector_images_uu = None
    detector_images_dd = None
    detector_images_du = None
    detector_images_ud = None
    roi = []

    file_ok = False
    is_polarised = False


    def __init__(self, filename):
        self.file_ok = False
        try:
            self.FILE = h5py.File(filename, 'r')
        except FileNotFoundError:
            return

        INSTRUMENT = self.FILE[list(self.FILE.keys())[0]].get("instrument")
        MOTOR_DATA = np.array(INSTRUMENT.get('motors').get('data')).T
        SCALERS_DATA = np.array(INSTRUMENT.get('scalers').get('data')).T
        PONOS = self.FILE[list(self.FILE.keys())[0]].get("ponos")
        self.SCAN = self.FILE[list(self.FILE.keys())[0]]

        for index, motor in enumerate(INSTRUMENT.get('motors').get('SPEC_motor_mnemonics')):
            if "'th'" in str(motor): self.th_list = MOTOR_DATA[index]
            elif "'tth'" in str(motor): self.tth_list = MOTOR_DATA[index]
            elif "'s1hg'" in str(motor): self.s1hg_list = MOTOR_DATA[index]
            elif "'s2hg'" in str(motor): self.s2hg_list = MOTOR_DATA[index]

        for index, scaler in enumerate(INSTRUMENT.get('scalers').get('SPEC_counter_mnemonics')):
            if "'mon0'" in str(scaler): self.monitor_list = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]
            elif "'m1'" in str(scaler): self.monitor_uu_list = SCALERS_DATA[index]
            elif "'m2'" in str(scaler): self.monitor_dd_list = SCALERS_DATA[index]
            elif "'m3'" in str(scaler): self.monitor_du_list = SCALERS_DATA[index]
            elif "'m4'" in str(scaler): self.monitor_ud_list = SCALERS_DATA[index]

        self.roi = np.array(self.SCAN.get("instrument").get('scalers').get('roi').get("roi"))

        self.is_polarised = "pnr" in list(self.FILE[list(self.FILE.keys())[0]])
        if self.is_polarised:
            for scan in PONOS.get('data'):
                if str(scan) == "data_uu":
                    self.detector_images_uu = INSTRUMENT.get("detectors").get("psd_uu").get('data')
                elif str(scan) == "data_ud":
                    self.detector_images_ud = INSTRUMENT.get("detectors").get("psd_ud").get('data')
                elif str(scan) == "data_du":
                    self.detector_images_du = INSTRUMENT.get("detectors").get("psd_du").get('data')
                elif str(scan) == "data_dd":
                    self.detector_images_dd = INSTRUMENT.get("detectors").get("psd_dd").get('data')
        else:
            self.detector_images = INSTRUMENT.get("detectors").get("psd").get('data')

        for det in INSTRUMENT.get('detectors'):
            self.det_types.append(str(det))

        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def is_pol(self): return self.is_polarised
    def get_h5(self): return self.FILE
    def get_scan(self): return self.SCAN
    def get_th(self): return self.th_list
    def get_tth(self): return self.tth_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list
    def get_intens(self): return self.intens_list
    def get_time(self): return self.time_list
    def get_mon(self): return self.monitor_list
    def get_mon_pol(self): return [ self.monitor_uu_list, self.monitor_dd_list, self.monitor_du_list, self.monitor_ud_list ]
    def get_psd(self): return self.detector_images
    def get_psd_pol(self): return [ self.detector_images_uu, self.detector_images_dd, self.detector_images_du, self.detector_images_ud ]
    def get_det_types(self): return self.det_types
    def get_roi(self): return self.roi


# test
#file = H5Loader("/users/tw/tmp/data/00593.h5")
