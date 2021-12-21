from iqtools import *
from ROOT import *
import numpy as np
from amedata import *
from particle import *
from ring import Ring
import lisereader as lread
from inputparams import*


class ImportData():
    def __init__(self, filename_tiq, filename_NTCAP):#, filename_NTCAP
        self.master_filename_tiq = filename_tiq
        self.master_filename_NTCAP = filename_NTCAP
        self.ring = Ring('ESR', 108.5)  # have to add more functionalities here

        self._read_masterfile()
        self._import()
        self._analyzer_data()
        self._NTCAP_data()
        self._calculate()
        self._simulated_data()

    def _read_masterfile(self):
        # reads list filenames with experiment data. [:-1] to remove eol sequence.
        self.file_list_tiq = [file[:-1]
                          for file in open(self.master_filename_tiq).readlines()]
        self.file_list_NTCAP = [file[:-1]
                          for file in open(self.master_filename_NTCAP).readlines()]
        # and for now:
        self.filename_tiq = self.file_list_tiq[0]
        self.filename_NTCAP = self.file_list_NTCAP[1]

    def _import(self):
        # import ame from barion:
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table

        # import input params
        params_file = 'data/InputParameters.txt'
        input_params = InputParams(params_file)
        self.pdict = input_params.dict

        # Load LISE file
        lise_file = lread.LISEreader(input_params.lisefile)
        self.lise_data = lise_file.get_info_all()

    def _analyzer_data(self):
        iq_tiq = TIQData(self.filename_tiq)        
        #iq_tiq.read_samples(1)
        lframes = 2**15
        nframes = 2*7
        iq_tiq.read_samples(nframes*lframes)

        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq_tiq.get_spectrogram(lframes=lframes, nframes=nframes)
        ff = (xx[0]+iq_tiq.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]/np.max(zz[0])).reshape(len(zz[0]),1) #normalized power
        self.analyzer_data=(np.stack((ff, pp), axis=1)).reshape((len(ff),2))

    def _NTCAP_data(self):
        iq_tdms = TDMSData(self.filename_NTCAP)
        lframes = 2**15
        nframes = 2*7
        iq_tdms.read_samples(nframes*lframes)
        
        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq_tdms.get_spectrogram(lframes=lframes, nframes=nframes)
        ff = (xx[0]+iq_tdms.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]/np.max(zz[0])).reshape(len(zz[0]),1) #normalized power
        self.NTCAP_data = (np.stack((ff, pp), axis=1)).reshape((len(ff), 2))

    def _calculate(self):
        # return mass and moq from barion of the particles present in LISE file
        self.mass = np.array([AMEData.to_mev(Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u())
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        moq = np.array([Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_moq_in_u()
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        # aux is the index of the reference particle
        self.aux = [i for i, lise in enumerate(self.lise_data) for ame in self.ame_data if (lise[0] ==
                                                                                            ame[6] and lise[1] == ame[5] and str(lise[1])+lise[0] == self.pdict['ReferenceIsotope'])]
        moq_Rel = moq[self.aux]
        # calculates gamma, beta, velocity and frequency (v/d) of our reference particle
        self.calculate_ion_parameters(self.pdict['Brho'])
        # simulated relative revolution frequencies
        self.SRRF = np.array([1-1/self.pdict['GAMMAT']/self.pdict['GAMMAT']*(moq[k]-moq_Rel)/moq_Rel
                              for k in range(len(self.mass))])

    def _simulated_data(self):
        self.simulated_data_dict=dict()
        # get power data from lise
        yield_data = [lise[5] for lise in self.lise_data]
        yield_data_normalised = np.array(
            [[element/max(yield_data) for element in yield_data]]).T
        #get lise name for labels
        ion_A=np.array([[int(lise[1]) for lise in self.lise_data]]).T
        ion_Z=np.array([[int(lise[2]) for lise in self.lise_data]]).T
        ion_Q=np.array([[int(lise[4]) for lise in self.lise_data]]).T
        # harmonics:
        self.harmonics = np.array([int(harmonic) for harmonic in input(f'introduce the harmonics to simulate separated by space; e.g.: 124 125:').split()]).T
        for harmonic in self.harmonics:
            print(harmonic)
            simulated_data = np.array([])
            array_stack=np.array([])
            # create harmonic index:
            name=f'{harmonic}'
            # get srf data
            harmonic_frequency = self.SRRF*self.Frequence_Rel*harmonic
            # attach harmonic, frequency, yield data and ion properties together:
            array_stack = np.stack((harmonic_frequency, yield_data_normalised, ion_A, ion_Z, ion_Q),
                                   axis=1)  # axis=1 stacks vertically
            simulated_data = np.append(simulated_data, array_stack)
            simulated_data = simulated_data.reshape(len(array_stack), 5)
            self.simulated_data_dict[name]=simulated_data
        
    def calculate_ion_parameters(self, x):
        gamma = self.gamma(self.pdict['Brho'])
        beta = self.beta(gamma)
        velocity = self.velocity(beta)
        self.Frequence_Rel = self.calc_freq_rel(velocity)

    def gamma(self, x):
        # /1e6 necessary for mass from MeV to eV.
        return np.sqrt(pow(x*self.pdict['ReferenceIsotopeCharge']*(AMEData.CC/1e6)/self.mass[self.aux], 2)+1)

    def beta(self, gamma):
        return np.sqrt(gamma*gamma-1)/gamma

    def velocity(self, beta):
        return AMEData.CC*beta

    def calc_freq_rel(self, velocity):
        return velocity/self.ring.circumference
    
def main():
    # specified file is list of filenames
    filename_tiq = 'data/410-j'
    filename_NTCAP = 'data/tdms-example'
    test = ImportData(filename_tiq, filename_NTCAP)


if __name__ == '__main__':
    main()
