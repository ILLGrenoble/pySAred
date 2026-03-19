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

    def get_mon_all(self): pass
    def get_mon(self): pass
    def get_mon_pol(self): pass

    def get_psd_all(self): pass
    def get_psd(self): pass
    def get_psd_pol(self): pass
    def get_detector_types(self): pass

    def get_ponos_all(self): pass

    def get_det_and_mon(self, which):
        dets = self.get_psd_all()
        mons = self.get_mon_all()
        #pols = self.get_ponos_all()

        det = None
        mon = None
        #pol = None

        if which in dets:
            det = dets[which]

        which_mon = which.replace("psd", "mon")
        if which_mon in mons:
            mon = mons[which_mon]

        #which_pol = which.replace("psd", "data")
        #if which_pol in pols:
        #    pol = pols[which_pol]

        return [ det, mon ] #, pol ]



class H5Loader(ILoader):
    FILE = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    intens_list = []
    time_list = []
    roi = []

    monitor_list = {}

    detector_types = []
    detector_images = {}

    ponos_images = {}

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
        PONOS        = SCAN.get("ponos")
        MOTORS       = INSTRUMENT.get('motors')
        MOTOR_DATA   = np.array(MOTORS.get('data')).T
        SCALERS      = INSTRUMENT.get('scalers')
        SCALERS_DATA = np.array(SCALERS.get('data')).T
        DETECTORS    = INSTRUMENT.get("detectors")

        for det in DETECTORS:
            self.detector_types.append(str(det))

        for index, motor in enumerate(MOTORS.get('SPEC_motor_mnemonics')):
            if "'th'" in str(motor): self.th_list = MOTOR_DATA[index]
            elif "'tth'" in str(motor): self.tth_list = MOTOR_DATA[index]
            elif "'s1hg'" in str(motor): self.s1hg_list = MOTOR_DATA[index]
            elif "'s2hg'" in str(motor): self.s2hg_list = MOTOR_DATA[index]

        for index, scaler in enumerate(SCALERS.get('SPEC_counter_mnemonics')):
            if "'mon0'" in str(scaler): self.monitor_list["mon"] = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]
            elif "'m1'" in str(scaler): self.monitor_list["mon_uu"] = SCALERS_DATA[index]
            elif "'m2'" in str(scaler): self.monitor_list["mon_dd"] = SCALERS_DATA[index]
            elif "'m3'" in str(scaler): self.monitor_list["mon_du"] = SCALERS_DATA[index]
            elif "'m4'" in str(scaler): self.monitor_list["mon_ud"] = SCALERS_DATA[index]

        self.roi = np.array(SCALERS.get('roi').get("roi"))

        self.is_polarised = "pnr" in SCAN

        for scan in PONOS.get('data'):
            scan_key = str(scan)
            psd_key = scan_key.replace("data", "psd")
            if psd_key in DETECTORS:
                self.detector_images[psd_key] = DETECTORS.get(psd_key).get('data')
            self.ponos_images[scan_key] = PONOS.get('data').get(scan_key)

        if not self.is_polarised:
            self.detector_images["psd"] = DETECTORS.get("psd").get('data')

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

    def get_mon_all(self): return self.monitor_list
    def get_mon(self):
        dat = None
        if "mon" in self.monitor_list: dat = self.monitor_list["mon"]
        return dat
    def get_mon_pol(self):
        uu, dd, du, ud = None, None, None, None
        if "mon_uu" in self.monitor_list: uu = self.monitor_list["mon_uu"]
        if "mon_dd" in self.monitor_list: dd = self.monitor_list["mon_dd"]
        if "mon_du" in self.monitor_list: du = self.monitor_list["mon_du"]
        if "mon_ud" in self.monitor_list: ud = self.monitor_list["mon_ud"]
        return [ uu, dd, du, ud ]

    def get_psd_all(self): return self.detector_images
    def get_psd(self):
        dat = None
        if "psd" in self.detector_images: dat = self.detector_images["psd"]
        return dat
    def get_psd_pol(self):
        uu, dd, du, ud = None, None, None, None
        if "psd_uu" in self.detector_images: uu = self.detector_images["psd_uu"]
        if "psd_dd" in self.detector_images: dd = self.detector_images["psd_dd"]
        if "psd_du" in self.detector_images: du = self.detector_images["psd_du"]
        if "psd_ud" in self.detector_images: ud = self.detector_images["psd_ud"]
        return [ uu, dd, du, ud ]
    def get_detector_types(self): return self.detector_types

    def get_ponos_all(self): return self.ponos_images



# test
#file = H5Loader("00593.h5")
#file = H5Loader("test_file.h5")
#print(file.get_th())
