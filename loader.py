import h5py
import numpy as np


class H5Loader:
    FILE = None
    SCAN = None

    th_list = []
    s1hg_list = []
    s2hg_list = []

    monitor_list = []
    intens_list = []
    time_list = []

    detector_images = None
    file_ok = False


    def __init__(self, filename):
        self.file_ok = False
        try:
            self.FILE = h5py.File(filename, 'r')
        except FileNotFoundError:
            return

        INSTRUMENT = self.FILE[list(self.FILE.keys())[0]].get("instrument")
        MOTOR_DATA = np.array(INSTRUMENT.get('motors').get('data')).T
        SCALERS_DATA = np.array(INSTRUMENT.get('scalers').get('data')).T
        self.SCAN = self.FILE[list(self.FILE.keys())[0]]

        self.th_list = self.s1hg_list = self.s2hg_list = []
        self.monitor_list = self.intens_list = self.time_list = []

        for index, motor in enumerate(INSTRUMENT.get('motors').get('SPEC_motor_mnemonics')):
            if "'th'" in str(motor): self.th_list = MOTOR_DATA[index]
            elif "'s1hg'" in str(motor): self.s1hg_list = MOTOR_DATA[index]
            elif "'s2hg'" in str(motor): self.s2hg_list = MOTOR_DATA[index]

        for index, scaler in enumerate(INSTRUMENT.get('scalers').get('SPEC_counter_mnemonics')):
            if "'mon0'" in str(scaler): self.monitor_list = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]

        original_roi_coord = np.array(self.SCAN.get("instrument").get('scalers').get('roi').get("roi"))

        self.detector_images = INSTRUMENT.get('detectors').get("psd").get('data')
        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def get_h5(self): return self.FILE
    def get_scan(self): return self.SCAN
    def get_th(self): return self.th_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list



# test
#file = H5Loader("/users/tw/tmp/data/00593.h5")
