import h5py
import numpy as np



class ILoader:
    def is_ok(self): pass
    def is_pol(self): pass

    def get_h5(self): pass

    def get_th(self): pass
    def get_tth(self): pass
    def get_s1hg(self): pass
    def get_s2hg(self): pass

    def get_intens(self): pass
    def get_time(self): pass
    def get_roi(self): pass

    def get_mon(self): pass
    def get_mon_pol(self): pass

    def get_psd(self): pass
    def get_psd_pol(self): pass
    def get_detector_types(self): pass

    def get_ponos_pol(self): pass
    def get_ponos_types(self): pass



class H5Loader(ILoader):
    FILE = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    intens_list = []
    time_list = []
    roi = []

    monitor_list = []
    monitor_uu_list = []
    monitor_dd_list = []
    monitor_du_list = []
    monitor_ud_list = []

    detector_types = []
    detector_images = None
    detector_images_uu = None
    detector_images_dd = None
    detector_images_du = None
    detector_images_ud = None

    ponos_types = []
    ponos_images_uu = None
    ponos_images_dd = None
    ponos_images_du = None
    ponos_images_ud = None

    file_ok = False
    is_polarised = False


    def __init__(self, filename):
        self.file_ok = False
        try:
            self.FILE = h5py.File(filename, 'r')
        except FileNotFoundError:
            return

        SCAN         = self.FILE[list(self.FILE.keys())[0]]
        INSTRUMENT   = SCAN.get("instrument")
        MOTORS       = INSTRUMENT.get('motors')
        MOTOR_DATA   = np.array(MOTORS.get('data')).T
        SCALERS      = INSTRUMENT.get('scalers')
        SCALERS_DATA = np.array(SCALERS.get('data')).T
        PONOS        = SCAN.get("ponos")
        DETECTORS    = INSTRUMENT.get("detectors")

        for det in DETECTORS:
            self.detector_types.append(str(det))

        for index, motor in enumerate(MOTORS.get('SPEC_motor_mnemonics')):
            if "'th'" in str(motor): self.th_list = MOTOR_DATA[index]
            elif "'tth'" in str(motor): self.tth_list = MOTOR_DATA[index]
            elif "'s1hg'" in str(motor): self.s1hg_list = MOTOR_DATA[index]
            elif "'s2hg'" in str(motor): self.s2hg_list = MOTOR_DATA[index]

        for index, scaler in enumerate(SCALERS.get('SPEC_counter_mnemonics')):
            if "'mon0'" in str(scaler): self.monitor_list = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]
            elif "'m1'" in str(scaler): self.monitor_uu_list = SCALERS_DATA[index]
            elif "'m2'" in str(scaler): self.monitor_dd_list = SCALERS_DATA[index]
            elif "'m3'" in str(scaler): self.monitor_du_list = SCALERS_DATA[index]
            elif "'m4'" in str(scaler): self.monitor_ud_list = SCALERS_DATA[index]

        self.roi = np.array(SCALERS.get('roi').get("roi"))

        self.is_polarised = "pnr" in SCAN
        for scan in PONOS.get('data'):
            if str(scan) == "data_uu":
                if self.is_polarised:
                    self.detector_images_uu = DETECTORS.get("psd_uu").get('data')
                self.ponos_images_uu = PONOS.get('data').get("data_uu")
                self.ponos_types.append("data_uu")
            elif str(scan) == "data_ud":
                if self.is_polarised:
                    self.detector_images_ud = DETECTORS.get("psd_ud").get('data')
                self.ponos_images_ud = PONOS.get('data').get("data_ud")
                self.ponos_types.append("data_ud")
            elif str(scan) == "data_du":
                if self.is_polarised:
                    self.detector_images_du = DETECTORS.get("psd_du").get('data')
                self.ponos_images_du = PONOS.get('data').get("data_du")
                self.ponos_types.append("data_du")
            elif str(scan) == "data_dd":
                if self.is_polarised:
                    self.detector_images_dd = DETECTORS.get("psd_dd").get('data')
                self.ponos_images_dd = PONOS.get('data').get("data_dd")
                self.ponos_types.append("data_dd")

        if not self.is_polarised:
            self.detector_images = DETECTORS.get("psd").get('data')

        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def is_pol(self): return self.is_polarised

    def get_h5(self): return self.FILE

    def get_th(self): return self.th_list
    def get_tth(self): return self.tth_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list

    def get_intens(self): return self.intens_list
    def get_time(self): return self.time_list
    def get_roi(self): return self.roi

    def get_mon(self): return self.monitor_list
    def get_mon_pol(self): return [ self.monitor_uu_list, self.monitor_dd_list, self.monitor_du_list, self.monitor_ud_list ]

    def get_psd(self): return self.detector_images
    def get_psd_pol(self): return [ self.detector_images_uu, self.detector_images_dd, self.detector_images_du, self.detector_images_ud ]
    def get_detector_types(self): return self.detector_types

    def get_ponos_pol(self): return [ self.ponos_images_uu, self.ponos_images_dd, self.ponos_images_du, self.ponos_images_ud ]
    def get_ponos_types(self): return self.ponos_types



# test
#file = H5Loader("/users/tw/tmp/data/00593.h5")
#print(file.get_th())
