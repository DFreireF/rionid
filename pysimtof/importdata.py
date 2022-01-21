from iqtools import *
from ROOT import *
import numpy as np
from amedata import *
from particle import *
from ring import Ring
import lisereader as lread


class ImportData():
    def __init__(self, filename, LISE_filename, harmonics, Brho, Gammat, ref_iso, ref_charge):
        self.ring = Ring('ESR', 108.4)
        self._import(LISE_filename)
        self._exp_data(filename)
        self._calculate(Brho, Gammat, ref_iso, ref_charge)
        self._simulated_data(harmonics)

    def _import(self, lisefile):
        # import ame from barion:
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table
        # Load LISE file
        lise_file = lread.LISEreader(lisefile)
        self.lise_data = lise_file.get_info_all()
        
    def _exp_data(self, filename):
        if 'root' in filename:
            fdata = TFile(filename)
            h=TH1F()
            h=fdata.Get('FFT_Average')
            ff= np.array([[h.GetXaxis().GetBinCenter(i)*1000+245*10**6] for i in range(1,h.GetNbinsX())])
            pp= np.array([[h.GetBinContent(i)] for i in range(1,h.GetNbinsX())])          
            self.exp_data=(np.stack((ff, pp), axis=1)).reshape((len(ff),2))
        else:
            iq = get_iq_object(filename)        
            lframes = 2**16
            nframes = 2*7
            iq.read_samples(nframes*lframes)
            # import xx:frequency, yy:time, zz:power
            xx, _, zz = iq.get_spectrogram(lframes=lframes, nframes=nframes)
            ff = (xx[0]+iq.center).reshape(len(xx[0]),1) #frequency, index 0 as xx is 2d array
            pp = (zz[0]).reshape(len(zz[0]),1) #power
            self.exp_data=(np.stack((ff, pp), axis=1)).reshape((len(ff),2))

    def _calculate(self, Brho, Gammat, ref_isotope, ref_charge):
        # return mass and moq from barion of the particles present in LISE file
        self.mass = np.array([AMEData.to_mev(Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u())
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        moq = np.array([Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_moq_in_u()
                             for lise in self.lise_data for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]])
        # aux is the index of the reference particle
        self.aux = [i for i, lise in enumerate(self.lise_data) for ame in self.ame_data if (lise[0] ==
                                                                                            ame[6] and lise[1] == ame[5] and str(lise[1])+lise[0] == ref_isotope)]
        moq_Rel = moq[self.aux]
        # calculates gamma, beta, velocity and frequency (v/d) of our reference particle
        self.calculate_ion_parameters(Brho, ref_charge)
        # simulated relative revolution frequencies
        self.SRRF = np.array([1-1/Gammat/Gammat*(moq[k]-moq_Rel)/moq_Rel
                              for k in range(len(self.mass))])
        
    def _simulated_data(self, harmonics):
        self.simulated_data_dict=dict()
        yield_data = np.array([[lise[5] for lise in self.lise_data]]).T
        #get nuclei name for labels
        self.nuclei_names=[f'{lise[1]}'+Particle(lise[2], lise[3], self.ame, self.ring).tbl_name+f'+{lise[4]}' for lise in self.lise_data]
        # harmonics:
        for harmonic in harmonics:
            simulated_data = np.array([])
            array_stack=np.array([])
            # create harmonic index:
            name=f'{harmonic}'
            # get srf data
            harmonic_frequency = self.SRRF*self.Frequence_Rel*harmonic
            # attach harmonic, frequency, yield data and ion properties together:
            array_stack = np.stack((harmonic_frequency, yield_data),
                                   axis=1)  # axis=1 stacks vertically
            simulated_data = np.append(simulated_data, array_stack)
            simulated_data = simulated_data.reshape(len(array_stack), 2)
            self.simulated_data_dict[name]=simulated_data
            #self.simulated_data_dict[name]=simulated_data[simulated_data[:, 0].argsort()] #sorting by frec

    def calculate_ion_parameters(self, Brho, ref_charge):
        gamma = self.gamma(Brho, ref_charge)
        beta = self.beta(gamma)
        velocity = self.velocity(beta)
        self.Frequence_Rel = self.calc_freq_rel(velocity)

    def gamma(self, Brho, ref_charge):
        # /1e6 necessary for mass from MeV to eV.
        return np.sqrt(pow(Brho*ref_charge*(AMEData.CC/1e6)/self.mass[self.aux], 2)+1)

    def beta(self, gamma):
        return np.sqrt(gamma*gamma-1)/gamma

    def velocity(self, beta):
        return AMEData.CC*beta

    def calc_freq_rel(self, velocity):
        return velocity/self.ring.circumference
    
def main():
    filename = 'data/245test.tiq'
    LISE_filename='data/E143_TEline-ESR-72Ge.lpp'
    harmonics=[125]
    Brho=6.90922    
    Gammat=1.395
    ref_iso='72Ge'
    ref_charge=32
    ImportData(filename, LISE_filename, harmonics, Brho, Gammat, ref_iso, ref_charge)


if __name__ == '__main__':
    main()
