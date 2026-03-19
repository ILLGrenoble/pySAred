import h5py
import numpy as np



class ILoader:
    def is_ok(self): pass
    def is_pol(self): pass

    def get_th(self): pass
    def get_tth(self): pass
    def get_s1hg(self): pass
    def get_s2hg(self): pass

    def get_intens(self): pass
    def get_time(self): pass
    def get_roi(self): pass

    def get_det(self): pass
    def get_det_types(self): pass

    def get_det_and_mon(self, which):
        dets = self.get_det()

        det = None
        mon = None
        #pol = None

        if which in dets:
            det = dets[which]

        which_mon = which.replace("psd", "mon")
        if which_mon in dets:
            mon = dets[which_mon]

        #which_pol = which.replace("psd", "data")
        #if which_pol in dets:
        #    pol = dets[which_pol]

        return [ det, mon ] #, pol ]

    def get_psds(self):
        unpol, uu, dd, du, ud = None, None, None, None, None
        if "psd" in self.detector_images: unpol = self.detector_images["psd"]
        if "psd_uu" in self.detector_images: uu = self.detector_images["psd_uu"]
        if "psd_dd" in self.detector_images: dd = self.detector_images["psd_dd"]
        if "psd_du" in self.detector_images: du = self.detector_images["psd_du"]
        if "psd_ud" in self.detector_images: ud = self.detector_images["psd_ud"]
        return [ unpol, uu, dd, du, ud ]

    def get_mons(self):
        unpol, uu, dd, du, ud = None, None, None, None, None
        if "mon" in self.detector_images: unpol = self.detector_images["mon"]
        if "mon_uu" in self.detector_images: uu = self.detector_images["mon_uu"]
        if "mon_dd" in self.detector_images: dd = self.detector_images["mon_dd"]
        if "mon_du" in self.detector_images: du = self.detector_images["mon_du"]
        if "mon_ud" in self.detector_images: ud = self.detector_images["mon_ud"]
        return [ unpol, uu, dd, du, ud ]


    @staticmethod
    def load(filename):
        # TODO; choose between loaders here
        return H5Loader(filename)



class H5Loader(ILoader):
    FILE = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    intens_list = []
    time_list = []
    roi = []

    detector_types = []
    detector_images = {}

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
            if "'mon0'" in str(scaler): self.detector_images["mon"] = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]
            elif "'m1'" in str(scaler): self.detector_images["mon_uu"] = SCALERS_DATA[index]
            elif "'m2'" in str(scaler): self.detector_images["mon_dd"] = SCALERS_DATA[index]
            elif "'m3'" in str(scaler): self.detector_images["mon_du"] = SCALERS_DATA[index]
            elif "'m4'" in str(scaler): self.detector_images["mon_ud"] = SCALERS_DATA[index]

        self.roi = np.array(SCALERS.get('roi').get("roi"))

        self.is_polarised = "pnr" in SCAN
        if not self.is_polarised:
            self.detector_images["psd"] = DETECTORS.get("psd").get('data')

        for scan in PONOS.get('data'):
            scan_key = str(scan)
            psd_key = scan_key.replace("data", "psd")
            if psd_key in DETECTORS:
                self.detector_images[psd_key] = DETECTORS.get(psd_key).get('data')
            self.detector_images[scan_key] = PONOS.get('data').get(scan_key)

        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def is_pol(self): return self.is_polarised

    def get_th(self): return self.th_list
    def get_tth(self): return self.tth_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list

    def get_intens(self): return self.intens_list
    def get_time(self): return self.time_list
    def get_roi(self): return self.roi

    def get_det(self): return self.detector_images
    def get_det_types(self): return self.detector_types




# test
#file = ILoader.load("00593.h5")
#file = ILoader.load("test_file.h5")
#print(file.get_th())
