from barion.ring import Ring
from barion.amedata import *
from barion.particle import *
from lisereader.reader import *
from ROOT import *
from iqtools import *
import sys


class ImportData():
    '''
    Model (MVC)
    '''
    def __init__(self, ref_nuclei, ref_charge, brho, gammat):
        
        self.ring = Ring('ESR', 108.43)
        self.ref_nuclei = ref_nuclei
        self.ref_charge = ref_charge
        self.ref_ion = f'{ref_nuclei}+{ref_charge}'
        self.brho = brho
        self.gammat = gammat

    def _set_secondary_args(self, lise_filename, harmonics):

        self.lise = lise_filename
        self.harmonics = harmonics

    def _set_tertiary_args(self, filename, data_time, skip_time, binning):
        
        self.filename = filename    
        self.data_time = data_time
        self.skip_time = skip_time
        self.lframes = binning
        
    def _import(self):
        # import ame from barion:
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table
        
        # Load LISE file
        lise_file = LISEreader(self.lise)
        self.lise_data = lise_file.get_info_all()

    def exp_data_root(self):
        
        ##This part may need to be changed to have the same frecuency "units"
        fdata = TFile(self.filename)
        histogram = fdata.Get('FFT_Total_px')# change this to, fdata.ls() and choose one
        ff = np.array([[histogram.GetXaxis().GetBinCenter(i)*1e6] for i in range(1, histogram.GetNbinsX())])#*1000+245*10**6
        pp = np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbinsX())])          
        return (np.stack((ff, pp), axis=1)).reshape((len(ff),2))

    def exp_data_analyser(self):

        iq = get_iq_object(self.filename)
        nframes = int(self.data_time * iq.fs / self.lframes)
        sframes = int(self.skip_time * iq.fs / self.lframes)
        iq.read(nframes = nframes, lframes = self.lframes, sframes = sframes)
        xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.lframes)
        axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:,0]))
        ff = (axx[0, :] + iq.center).reshape(len(axx[0, :]),1) #frequency, index 0 as xx is 2d array
        pp = (azz[0, :]).reshape(len(azz[0, :]),1) #power
        pp = pp / pp.max()
        return (np.stack((ff, pp), axis = 1)).reshape((len(ff), 2))
    
    def exp_data_ntcap(self):
        
        '''
        Needs to be modified
        '''
        nframes = 4096
        lframes = 2e18
        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq.get_spectrogram(nframes, lframes)
        ff = (xx[0] + iq.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]).reshape(len(zz[0]),1) #power
        pp = pp / pp.max()
        return (np.stack((ff, pp), axis = 1)).reshape((len(ff), 2))
        
    def _exp_data(self):
        
        if 'root' in self.filename: self.exp_data = self.exp_data_root()
        elif 'tiq' in self.filename: self.exp_data = self.exp_data_analyser()
        elif 'tdms' in self.filename: self.exp_data = self.exp_data_ntcap()
        else: sys.exit()

    def calculate_moqs(self, particles = None):
        
        # return moq from barion of the particles present in LISE file, or of the particles introduced
        self.moq = dict()
        if particles:
            for particle in particles:
                nuclei_name = f'{particle.tbl_aa}{particle.tbl_name}+{particle.qq}'
                self.moq[nuclei_name] = particle.get_ionic_moq_in_u()
        else:
            self._import()
            for lise in self.lise_data:
                nuclei_name = f'{lise[1]}{lise[0]}+{lise[4][0]}'
                self.moq[nuclei_name] = [Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_moq_in_u()
                                                   for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]]

    def _calculate_srrf(self, moqs = None):
        
        if moqs:
            self.moq = moqs
            self.moq[self.ref_ion] = Particle(32, 40, AMEData(), self.ring).get_ionic_moq_in_u()
            
        self.mass_ref = AMEData.to_mev(self.moq[self.ref_ion] * self.ref_charge)
        self.frequence_rel = ImportData.calculate_ion_parameters(self.brho, self.ref_charge, self.mass_ref, self.ring.circumference)
        # simulated relative revolution frequencies
        self.srrf = np.array([1 - 1 / self.gammat**2 * (self.moq[name] - self.moq[self.ref_ion]) / self.moq[self.ref_ion]
                              for name in self.moq])
        
    def _simulated_data(self, particles = False):
        self.simulated_data_dict = dict()
        if particles: yield_data = [1 for i in range(len(self.moq))]
        else: yield_data = np.array([[lise[5] for lise in self.lise_data]]).T
        #get nuclei name for labels
        self.nuclei_names = [nuclei_name for nuclei_name in self.moq]
        # harmonics:
        for harmonic in self.harmonics:
            simulated_data = np.array([])
            array_stack = np.array([])
            # get srf data
            harmonic_frequency = self.srrf * self.frequence_rel * harmonic
            # attach harmonic, frequency, yield data and ion properties together:
            print(harmonic_frequency, yield_data)
            array_stack = np.stack((harmonic_frequency, yield_data),
                                   axis=1)  # axis=1 stacks vertically
            simulated_data = np.append(simulated_data, array_stack)
            simulated_data = simulated_data.reshape(len(array_stack), 2)
            name = f'{harmonic}'            
            self.simulated_data_dict[name] = simulated_data
#            self.simulated_data_dict[name] = simulated_data[simulated_data[:, 0].argsort()]
            
    @staticmethod
    def calculate_ion_parameters(brho, ref_charge, ref_mass, ring_circumference):
        gamma = ImportData.gamma(brho, ref_charge, ref_mass)
        beta = ImportData.beta(gamma)
        velocity = ImportData.velocity(beta)
        frequence_rel = ImportData.calc_freq_rel(velocity, ring_circumference)
        return frequence_rel
        
    @staticmethod
    def gamma(brho, ref_charge, ref_mass):
        # /1e6 necessary for mass from mev to ev.
        return np.sqrt(pow(brho*ref_charge*(AMEData.CC/1e6)/ref_mass, 2)+1)        
    
    @staticmethod
    def beta(gamma):
        return np.sqrt(gamma**2 - 1) / gamma

    @staticmethod
    def velocity(beta):
        return AMEData.CC * beta
    
    @staticmethod
    def calc_freq_rel(velocity, ring_circumference):
        return velocity / ring_circumference
