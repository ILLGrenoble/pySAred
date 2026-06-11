import h5py
import numpy as np



class ILoader:
    def is_ok(self): pass
    def is_pol(self): pass

    def get_th(self): pass
    def get_tth(self): pass
    def get_s1hg(self): pass
    def get_s2hg(self): pass

    def get_time(self): pass
    def get_intens(self): pass
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
        try:
            FILE = h5py.File(filename, 'r')
        except FileNotFoundError:
            return None

        # choose between loaders
        if "entry0" in list(FILE.keys()):
            return NXSLoader(FILE)
        else:
            return H5Loader(FILE)



class H5Loader(ILoader):
    FILE = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    time_list = []
    intens_list = []
    roi = []   # [ top, bottom, left, right ]

    detector_types = []
    detector_images = {}

    file_ok = False
    is_polarised = False


    def __init__(self, FILE):
        self.file_ok = False
        self.FILE = FILE

        SCAN         = self.FILE[list(self.FILE.keys())[0]]
        INSTRUMENT   = SCAN.get("instrument")
        PONOS        = SCAN.get("ponos")
        MOTORS       = INSTRUMENT.get("motors")
        MOTOR_DATA   = np.array(MOTORS.get("data")).T
        SCALERS      = INSTRUMENT.get("scalers")
        SCALERS_DATA = np.array(SCALERS.get("data")).T
        DETECTORS    = INSTRUMENT.get("detectors")

        for det in DETECTORS:
            if not det in self.detector_types:
                self.detector_types.append(str(det))

        for index, motor in enumerate(MOTORS.get("SPEC_motor_mnemonics")):
            if "'th'" in str(motor): self.th_list = MOTOR_DATA[index]
            elif "'tth'" in str(motor): self.tth_list = MOTOR_DATA[index]
            elif "'s1hg'" in str(motor): self.s1hg_list = MOTOR_DATA[index]
            elif "'s2hg'" in str(motor): self.s2hg_list = MOTOR_DATA[index]

        for index, scaler in enumerate(SCALERS.get("SPEC_counter_mnemonics")):
            if "'mon0'" in str(scaler): self.detector_images["mon"] = SCALERS_DATA[index]
            elif "'roi'" in str(scaler): self.intens_list = SCALERS_DATA[index]
            elif "'sec'" in str(scaler): self.time_list = SCALERS_DATA[index]
            elif "'m1'" in str(scaler): self.detector_images["mon_uu"] = SCALERS_DATA[index]
            elif "'m2'" in str(scaler): self.detector_images["mon_dd"] = SCALERS_DATA[index]
            elif "'m3'" in str(scaler): self.detector_images["mon_du"] = SCALERS_DATA[index]
            elif "'m4'" in str(scaler): self.detector_images["mon_ud"] = SCALERS_DATA[index]

        self.roi = np.array(SCALERS.get("roi").get("roi"))

        self.is_polarised = "pnr" in SCAN
        if not self.is_polarised:
            self.detector_images["psd"] = DETECTORS.get("psd").get("data")

        for scan in PONOS.get("data"):
            scan_key = str(scan)
            psd_key = scan_key.replace("data", "psd")
            if psd_key in DETECTORS:
                self.detector_images[psd_key] = DETECTORS.get(psd_key).get("data")
            self.detector_images[scan_key] = PONOS.get("data").get(scan_key)

        if len(self.roi) == 0 and len(self.detector_types) > 0:
            # select everything if no roi is given
            self.roi = np.array([ 0., float(self.detector_images[self.detector_types[0]].shape[1]),
                0., float(self.detector_images[self.detector_types[0]].shape[2]) ])

        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def is_pol(self): return self.is_polarised

    def get_th(self): return self.th_list
    def get_tth(self): return self.tth_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list

    def get_time(self): return self.time_list
    def get_intens(self): return self.intens_list
    def get_roi(self): return self.roi

    def get_det(self): return self.detector_images
    def get_det_types(self): return self.detector_types



class NXSLoader(ILoader):
    FILE = None

    th_list = []
    tth_list = []
    s1hg_list = []
    s2hg_list = []

    time_list = []
    intens_list = []
    roi = []  # [ top, bottom, left, right ]

    detector_types = []
    detector_images = {}

    file_ok = False
    is_polarised = False


    def __init__(self, FILE):
        self.file_ok = False
        self.FILE = FILE

        SCAN       = self.FILE[list(self.FILE.keys())[0]]
        DATA_SCAN  = SCAN["data_scan"]
        VARS       = DATA_SCAN["scanned_variables"]
        INSTRUMENT = None

        # find instrument
        for item in SCAN.values():
            try:
                if item.attrs.get("NX_class").decode() == "NXinstrument":
                    INSTRUMENT = item
                    break
            except AttributeError:
                pass

        # no instrument found
        if INSTRUMENT == None:
            return

        # get instrument angles
        try:
            self.th_list = np.array(INSTRUMENT["th"]["value"])
        except KeyError:
            pass
        try:
            self.tth_list = np.array(INSTRUMENT["tth"]["value"])
        except KeyError:
            pass
        try:
            self.s1hg_list = np.array(INSTRUMENT["s1hg"]["value"])
        except KeyError:
            pass
        try:
            self.s2hg_list = np.array(INSTRUMENT["s2hg"]["value"])
        except KeyError:
            pass

        # detector images
        data_len = DATA_SCAN["total_steps"][0]
        all_psd = DATA_SCAN.get("detector_data").get("data")
        data_full_len = all_psd.shape[0]
        num_pol = int(data_full_len / data_len)
        self.is_polarised = (num_pol > 1)
        if self.is_polarised:
            self.detector_types = [ "psd_uu", "psd_dd" ]
            self.detector_images["psd_uu"] = all_psd[::num_pol]
            self.detector_images["psd_dd"] = all_psd[1::num_pol]
            # TODO
            self.detector_images["mon_uu"] = [ 1. ] * data_len
            self.detector_images["mon_dd"] = [ 1. ] * data_len
        else:
            self.detector_types = [ "psd" ]
            self.detector_images["psd"] = all_psd
            # TODO
            self.detector_images["mon"] = [ 1. ] * data_len


        if len(self.roi) == 0 and len(self.detector_types) > 0:
            # select everything if no roi is given
            self.roi = np.array([ 0., float(self.detector_images[self.detector_types[0]].shape[1] - 1.),
                0., float(self.detector_images[self.detector_types[0]].shape[2]) - 1. ])

        # get the scanned variables
        try:
            vars = VARS["variables_names/label"][:]
        except KeyError:
            axes = VARS["variables_names/axis"][:]
            names = VARS["variables_names/name"][:]
            props = VARS["variables_names/property"][:]
            vars = [ names[i] if axes[i] != 0 else props[i] for i in range(axes.size) ]
        vars = [ str.decode() for str in vars ]
        try:
            # get scanned vars
            scanned_cols = VARS["variables_names/scanned"][:]
            scanned_vars = [ vars[idx] for idx in range(scanned_cols.size) if scanned_cols[idx] != 0 ]
        except KeyError:
            # use all vars
            scanned_vars = vars

        # get the scanned variable values
        self.time_list = [ 1. ] * data_len
        self.intens_list = [ 1. ] * data_len
        self.th_list = self.tth_list = [ 0. ] * data_len
        self.s1hg_list = self.s2hg_list = [ 1. ] * data_len
        for idx in range(scanned_cols.size):
            if int(scanned_cols[idx]) == 0:
                continue
            if scanned_vars[idx] == "th":
                self.th_list = VARS["data"][idx, ::num_pol]
            elif scanned_vars[idx] == "tth":
                self.tth_list = VARS["data"][idx, ::num_pol]
            elif scanned_vars[idx] == "s1hg":
                self.s1hg_list = VARS["data"][idx, ::num_pol]
            elif scanned_vars[idx] == "s2hg":
                self.s2hg_list = VARS["data"][idx, ::num_pol]

        self.file_ok = True


    # getters
    def is_ok(self): return self.file_ok
    def is_pol(self): return self.is_polarised

    def get_th(self): return self.th_list
    def get_tth(self): return self.tth_list
    def get_s1hg(self): return self.s1hg_list
    def get_s2hg(self): return self.s2hg_list

    def get_time(self): return self.time_list
    def get_intens(self): return self.intens_list
    def get_roi(self): return self.roi

    def get_det(self): return self.detector_images
    def get_det_types(self): return self.detector_types




# test
#ILoader.load("00593.h5")
#ILoader.load("001034.nxs")
