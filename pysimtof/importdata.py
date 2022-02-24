from barion.ring import Ring
from barion.amedata import *
from barion.particle import *
from lisereader.reader import *
from ROOT import *
from iqtools import *
import sys

class ImportData():
    def __init__(self):
        self.ring = Ring('ESR', 108.43)

    def _set_args(self, filename, lise_filename, harmonics, brho, gammat, ref_iso, ref_charge, time, skip):
        self._import(lise_filename)
        self._exp_data(filename, time, skip)
        self._calculate(brho, gammat, ref_iso, ref_charge)
        self._simulated_data(harmonics)

    def _import(self, lisefile):
        # import ame from barion:
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table
        # Load LISE file
        lise_file = LISEreader(lisefile)
        self.lise_data = lise_file.get_info_all()
        
    @staticmethod    
    def exp_data_root(filename):
        ##This part may need to be changed to have the same frecuency "units"
        fdata = TFile(filename)
        histogram=fdata.Get('FFT_Total_px')# change this to, fdata.ls() and choose one
        ff= np.array([[histogram.GetXaxis().GetBinCenter(i)*1e6] for i in range(1,histogram.GetNbinsX())])#*1000+245*10**6
        pp= np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbinsX())])          
        return (np.stack((ff, pp), axis=1)).reshape((len(ff),2))

    @staticmethod
    def exp_data_analyser(filename, time, skip):
        iq = get_iq_object(filename)
        iq.read_samples(1)
        skip_time=time+skip
        lframes=2**9
        nframes=int(time*iq.fs/lframes)
        sframes=int(skip_time*iq.fs/lframes)
        iq.read(nframes=nframes, lframes=lframes, sframes=sframes)
        ff, pp, _=iq.get_fft()
        ff = (ff+iq.center).reshape(len(ff),1) #frequency, index 0 as xx is 2d array
        pp=pp/pp.max()
        pp = (pp).reshape(len(pp),1) #power
        return (np.stack((ff, pp), axis=1)).reshape((len(ff),2))
    
    @staticmethod
    def exp_data_ntcap(filename):
        lframes = 2**15
        nframes = 50
        iq.read_samples(nframes*lframes)
        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq.get_spectrogram(nframes,lframes)
        ff = (xx[0]+iq.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]).reshape(len(zz[0]),1) #power
        pp=pp/pp.max()
        return (np.stack((ff, pp), axis=1)).reshape((len(ff),2))
        
    def _exp_data(self, filename, time, skip):
        if 'root' in filename: self.exp_data=ImportData.exp_data_root(filename)
        elif 'tiq' in filename: self.exp_data=ImportData.exp_data_analyser(filename,time,skip)
        elif 'tdms' in filename: self.exp_data=ImportData.exp_data_ntcap(filename)
        else: sys.exit()

    def _calculate(self, brho, gammat, ref_isotope, ref_charge):
        # return mass and moq from barion of the particles present in LISE file
        self.mass = np.array([AMEData.to_mev(Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u())
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        moq = np.array([Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_moq_in_u()
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        self.ref_index = [i for i, lise in enumerate(self.lise_data) for ame in self.ame_data if (lise[0] ==
                                                                                            ame[6] and lise[1] == ame[5] and str(lise[1])+lise[0] == ref_isotope)]
        moq_rel = moq[self.ref_index]
        # calculates gamma, beta, velocity and frequency (v/d) of our reference particle
        self.frequence_rel=ImportData.calculate_ion_parameters(brho, ref_charge, self.mass[self.ref_index], self.ring.circumference)
        # simulated relative revolution frequencies
        self.srrf = np.array([1-1/gammat/gammat*(moq[k]-moq_rel)/moq_rel
                              for k in range(len(self.mass))])
        
    def _simulated_data(self, harmonics):
        self.simulated_data_dict=dict()
        yield_data = np.array([[lise[5] for lise in self.lise_data]]).T
        #get nuclei name for labels
        self.nuclei_names=[f'{lise[1]}'+Particle(lise[2], lise[3], self.ame, self.ring).tbl_name+f'+{lise[4][0]}' for lise in self.lise_data]
        # harmonics:
        for harmonic in harmonics:
            simulated_data = np.array([])
            array_stack=np.array([])
            # get srf data
            harmonic_frequency = self.srrf*self.frequence_rel*harmonic
            # attach harmonic, frequency, yield data and ion properties together:
            array_stack = np.stack((harmonic_frequency, yield_data),
                                   axis=1)  # axis=1 stacks vertically
            simulated_data = np.append(simulated_data, array_stack)
            simulated_data = simulated_data.reshape(len(array_stack), 2)
            name=f'{harmonic}'            
            self.simulated_data_dict[name]=simulated_data
            
    @staticmethod
    def calculate_ion_parameters(brho, ref_charge, ref_mass, ring_circumference):
        gamma = ImportData.gamma(brho, ref_charge, ref_mass)
        beta = ImportData.beta(gamma)
        velocity = ImportData.velocity(beta)
        frequence_rel = ImportData.calc_freq_rel(velocity, ring_circumference)
        return frequence_rel
        
    @staticmethod
    def gamma(brho, ref_charge, ref_mass):
        # /1e6 necessary for mass from MeV to eV.
        return np.sqrt(pow(brho*ref_charge*(AMEData.CC/1e6)/ref_mass, 2)+1)        
    
    @staticmethod
    def beta(gamma):
        return np.sqrt(gamma*gamma-1)/gamma
    
    @staticmethod
    def velocity(beta):
        return AMEData.CC*beta
    
    @staticmethod
    def calc_freq_rel(velocity, ring_circumference):
        return velocity/ring_circumference
