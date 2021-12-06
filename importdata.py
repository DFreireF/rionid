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
        self.filename_NTCAP = self.file_list_NTCAP[53]

    def _import(self):
        # import ame from barion:
        self.ame = AMEData()
        # self.ame.init_ame_db #is this necessary? Should also eliminate the message of AME Database files are available.
        self.ame_data = self.ame.ame_table

        # import input params
        params_file = 'data/InputParameters.txt'
        input_params = InputParams(params_file)
        self.pdict = input_params.dict

        # Load LISE file
        lise_file = lread.LISEreader(input_params.lisefile)
        self.lise_data = lise_file.get_info_all()

    def _analyzer_data(self):
        LFRAMES = 2**15
        NFRAMES = 2*7
        iq_tiq = TIQData(self.filename_tiq)
        iq_tiq.read_samples(LFRAMES*NFRAMES)

        # center frequency
        #self.fcenter=iq_tiq.center
        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq_tiq.get_spectrogram(lframes=LFRAMES, nframes=NFRAMES)
        ff = (xx[0]+iq_tiq.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]/np.max(zz[0])).reshape(len(zz[0]),1) #normalized power
        # setting variables from tiq data
        self.analyzer_data=(np.stack((ff, pp), axis=1)).reshape((len(ff),2))
        #print(self.analyzer_data[:,0])
        #input()
    def _NTCAP_data(self):
        LFRAMES = 2**15
        NFRAMES = 2*7
        iq_tdms = TDMSData(self.filename_NTCAP)
        iq_tdms.read_samples(LFRAMES*NFRAMES)

        # center frequency
        #self.fcenter=iq_tdms.center
        # import xx:frequency, yy:time, zz:power
        xx, _, zz = iq_tdms.get_spectrogram(lframes=LFRAMES, nframes=NFRAMES)
        ff = (xx[0]+iq_tdms.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
        pp = (zz[0]/np.max(zz[0])).reshape(len(zz[0]),1) #normalized power
        # setting variables from NTCAP data
        self.NTCAP_data = (np.stack((ff, pp), axis=1)).reshape((len(ff), 2))

    def _calculate(self):
        # return mass and moq from barion of the particles present in LISE file
        self.mass = np.array([AMEData.to_mev(Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u())
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        self.moq = np.array([Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_moq_in_u()
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        # aux is the index of the reference particle
        self.aux = [i for i, lise in enumerate(self.lise_data) for ame in self.ame_data if (lise[0] ==
                    ame[6] and lise[1] == ame[5] and str(lise[1])+lise[0] == self.pdict['ReferenceIsotope'])]
        self.moq_Rel = self.moq[self.aux]
        # calculates gamma, beta, velocity and frequency (v/d) of our reference particle
        self.calculate_ion_parameters(self.pdict['Brho'])
        # simulated relative and non-rel revolution frequencies
        self.SRRF = np.array([1-1/self.pdict['GAMMAT']/self.pdict['GAMMAT']*(self.moq[k]-self.moq_Rel)/self.moq_Rel
                              for k in range(len(self.mass))])
        self.SRF = [self.SRRF[k]*self.Frequence_Rel*self.pdict['Harmonic']
                    for k in range(len(self.mass))]

    def _simulated_data(self):
        self.simulated_data = np.array([])
        # get power data from lise
        yield_data = [element[5] for element in self.lise_data]
        self.yield_data_normalised = np.array(
            [[element/max(yield_data) for element in yield_data]]).T
        # harmonics:
        self.harmonics = np.array([124, 125, 126])
        for i, harmonic in enumerate(self.harmonics):  # will start here
            # create harmonic index:
            harmonic_index = (np.ones(len(self.SRF))*self.harmonics[i]).reshape(len(self.SRF),1)
            # get srf data
            harmonic_frequency = self.SRRF*self.Frequence_Rel*self.harmonics[i]
            #harmonic_frequency=self.set_range_SRF_to_analyzer(harmonic_frequency)
            # attach harmonic, frequency and yield data together:
            array_stack = np.stack((harmonic_index, harmonic_frequency, self.yield_data_normalised),
                                   axis=1)  # axis=1 stacks vertically
            self.simulated_data = np.append(self.simulated_data, array_stack)

        self.simulated_data = self.simulated_data.reshape(
            len(self.harmonics)*len(array_stack), 3)
        print(self.simulated_data)

    def calculate_ion_parameters(self, x):
        self.gamma = self.gamma(self.pdict['Brho'])
        self.beta = self.beta(self.gamma)
        self.velocity = self.velocity(self.beta)
        self.Frequence_Rel = self.calc_freq_rel(self.velocity)

    def set_range_SRF_to_analyzer(self,SRF):
        # find range
        srf_range = max(SRF) - min(SRF)
        data_range = max(self.analyzer_data[:,0]) - min(self.analyzer_data[:,0])
        # normalise srf data:
        normalised_srf = [x*(data_range/srf_range)for x in SRF]
        # find center of normalised data:
        normalised_center = min(normalised_srf) + \
            (max(normalised_srf)-min(normalised_srf))/2
        # move new srf data to center of tiqdata
        return  [x*(data_range/srf_range) -
                    normalised_center + self.fcenter for x in SRF]

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
