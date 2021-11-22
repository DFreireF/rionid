from iqtools import *
from ROOT import *
import numpy as np
from amedata import *
from particle import *
from ring import Ring
import lisereader as lread
from inputparams import*
from scipy.optimize import minimize


class ImportData():
    def __init__(self, filename):
        self.filename = filename
        self.ring = Ring('ESR', 108.5)  # have to add more functionalities here
        self._import()

    def _import(self):
        # import ame from barion:
        self.ame = AMEData()
        self.ame.init_ame_db
        self.ame_data = self.ame.ame_table
        
        # import input params
        params_file = 'data/InputParameters.txt'
        input_params = InputParams(params_file)
        # after tominimize equation fixed, change to:
        # pdict = input_params.dict
        # or pdict = InputParams(params_file).dict
        #but then will have to alter lisereader line.
        
        self.BRho = input_params.dict['Brho']
        self.GammaT = input_params.dict['GAMMAT']
        self.RefIso = input_params.dict['ReferenceIsotope']
        self.RefQ = input_params.dict['ReferenceIsotopeCharge']
        self.Harmonic = input_params.dict['Harmonic']
        
        # Load LISE file
        lise_file = lread.LISEreader(input_params.lisefile)
        self.lise_data = lise_file.get_info_all()
        self.Nx_SRF, self.Nx_SRRF = ([] for i in range(2))

    def data(self):
        LFRAMES = 2**10
        NFRAMES = 2*4
        iq = TIQData(self.filename)
        iq.read_samples(LFRAMES*NFRAMES)

        self.ff, self.pp, _ = iq.get_fft()  # 1D frec and power
        self.pp = self.pp / self.pp.max()  # normalized
        self.h = TH1D('h', 'h', len(self.ff), iq.center +
                      self.ff[0], iq.center + self.ff[-1])

        for i in range(len(self.ff)):
            self.h.SetBinContent(i, self.pp[i])
        self.nbins = self.h.GetXaxis().GetNbins()
        self.frequence_min = self.h.GetXaxis().GetXmin()/1000+245
        self.frequence_max = self.h.GetXaxis().GetXmax()/1000+245
        self.y_max = self.h.GetMaximum()
        self.h.GetXaxis().SetLimits(self.frequence_min, self.frequence_max)

    def samples(self):
        for i, lise in enumerate(self.lise_data):
            #calculating mass and moq using ame and lise data together
            m = [AMEData.to_mev(Particle(lise[2],lise[3],ame,self.ring).get_ionic_moq_in_u)
                 for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]]
            moq = [Particle(lise[2],lise[3],ame,self.ring).get_ionic_moq_in_u
                   for ame in self.ame_data if lise[0] == ame[6] and lise[1] == ame[5]]
            
            # for ame in self.ame_data:
            #     if lise[0] == ame[6] and lise[1] == ame[5]:
            #         particle_name = Particle(
            #             lise[2], lise[3], AMEData(), self.ring)
            #         self.m.append(AMEData.to_mev(
            #             particle_name.get_ionic_mass_in_u()))
            #         self.moq.append(particle_name.get_ionic_moq_in_u())
                    
            # if reference particle, calculate variables
            if (str(lise[1])+lise[0] == self.RefIso and lise[4] == self.RefQ):
                self.aux = i
                self.moq_Rel = self.moq[i]
                self.gamma = sqrt(
                    pow(self.BRho*self.RefQ*AMEData.CC/self.m[i], 2)+1)
                self.beta = sqrt(self.gamma*self.gamma-1)/self.gamma
                self.velocity = AMEData.CC*self.beta
                self.Frequence_Rel = self.velocity/self.ring.circumference

        # for k in range(0, len(self.m)):
        #     # 1. simulated relative revolution frequency
        #     self.SRRF.append(1-1/self.GammaT/self.GammaT *
        #                      (self.moq[k]-self.moq_Rel)/self.moq_Rel)
        #     # 2. simulated revolution frequency
        #     self.SRF.append(self.SRRF[k]*self.Frequence_Rel*self.Harmonic)
        
        # simulated relative and non-rel revolution frequencies    
        self.SRRF = [1-1/self.GammaT/self.GammaT*(self.moq[k]-self.moq_Rel)/self.moq_Rel
                        for k, element in enumerate(m)]
        self.SRF = [self.SRRF[k]*self.Frequence_Rel*self.Harmonic
                    for k, element in enumerate(m)]
        

        print(f'Brho initial: {self.BRho}')
        self.BRhoCorrection()
        print(f'Brho final: {self.BRho}')

        #why do you need this one?
        for k in range(0, len(self.m)):  # Calculate new simulated frecuency sample spectrum
            self.SRF[k] = self.SRRF[k]*self.Frequence_Rel*self.Harmonic

    def tominimize(self, x):  # function to minimize (x=Brho); yup, it's big
        tominimize = abs(self.ff[self.pp.argmax()]-((1-1/self.GammaT/self.GammaT*(self.moq[self.aux]-self.moq_Rel)/self.moq_Rel)*((AMEData.CC*(sqrt((sqrt(pow(x*self.RefQ*AMEData.CC/self.m[self.aux], 2))*(sqrt(pow(x*self.RefQ*AMEData.CC/self.m[self.aux], 2))-1)/(sqrt(pow(x*self.RefQ*AMEData.CC/self.m[self.aux], 2))))/self.ring.circumference)*self.Harmonic))
        return tominimize

    # Performs minimization of f_data[IsochroIon]-f_sample[RefIon(Brho)]
    def BRhoCorrection(self):
        self.BRho=minimize(tominimize, [self.BRho])
        self.gamma=sqrt(
            pow(self.BRho*self.RefQ*AMEData.CC/self.m[self.aux], 2)+1)
        self.beta=sqrt(self.gamma*self.gamma-1)/self.gamma
        self.velocity=AMEData.CC*self.beta
        self.Frequence_Rel=self.velocity/self.ring.circumference
# ================== execution =====================
def main():
    filename='data/245-m'
    with open(filename) as f:
        files=f.readlines()
        for file in files:
            test=ImportData(file[:-1])  # initialization
            test.data()
            test.samples()

if __name__ == '__main__':
    main()