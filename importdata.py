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
        self._read_data()
        self._calculate()

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

        self.BRho = input_params.dict['Brho']
        self.GammaT = input_params.dict['GAMMAT']
        self.RefIso = input_params.dict['ReferenceIsotope']
        self.RefQ = input_params.dict['ReferenceIsotopeCharge']
        self.Harmonic = input_params.dict['Harmonic']

        # Load LISE file
        lise_file = lread.LISEreader(input_params.lisefile)
        self.lise_data = lise_file.get_info_all()

    def _read_data(self):
        LFRAMES=2**15
        NFRAMES=2*4
        iq=TIQData(self.filename)
        iq.read_samples(LFRAMES*NFRAMES)
        
        # center frequency
        self.fcenter=iq.center
        # import xx:frequency , yy:time, zz:power
        xx, yy, zz = iq.get_spectrogram(lframes=LFRAMES, nframes=NFRAMES)
        self.ff=xx[0] #frequency
        self.pp = zz[0]/zz[0].max()  #normalized power
        self.h = TH1D('h', 'h', len(self.ff),
                      iq.center +self.ff[0],iq.center + self.ff[-1])

        # setting variables from data
        for i in range(len(self.ff)):
            self.h.SetBinContent(i, self.pp[i])
        self.nbins = self.h.GetXaxis().GetNbins()
        self.frequence_min = self.h.GetXaxis().GetXmin()/1000+245
        self.frequence_max = self.h.GetXaxis().GetXmax()/1000+245
        self.y_max = self.h.GetMaximum()
        self.h.GetXaxis().SetLimits(self.frequence_min, self.frequence_max)

    def _calculate(self):
        
        # return mass and moq from barion
        self.m = [AMEData.to_mev(Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u())
                  for ame in self.ame_data for lise in self.lise_data if lise[0] == ame[6] and lise[1] == ame[5]]
        self.moq = [Particle(lise[2], lise[3], self.ame, self.ring).get_ionic_mass_in_u()
                    for ame in self.ame_data for lise in self.lise_data if lise[0] == ame[6] and lise[1] == ame[5]]

        # if reference particle, calculate variables with lise data
        for i, lise in enumerate(self.lise_data):
            if (str(lise[1])+lise[0] == self.RefIso and lise[4] == self.RefQ):
                self.aux = i
                self.moq_Rel = self.moq[i]
                self.gamma = np.sqrt(pow(self.BRho*self.RefQ*AMEData.CC/self.m[i], 2)+1)
                self.beta = np.sqrt(self.gamma*self.gamma-1)/self.gamma
                self.velocity = AMEData.CC*self.beta
                self.Frequence_Rel = self.velocity/self.ring.circumference

        # simulated relative and non-rel revolution frequencies
        self.SRRF = [1-1/self.GammaT/self.GammaT*(self.moq[k]-self.moq_Rel)/self.moq_Rel
                     for k, element in enumerate(self.m)]
        self.SRF = [self.SRRF[k]*self.Frequence_Rel*self.Harmonic
                    for k, element in enumerate(self.m)]
        
        print('self.pp.argmax()',self.pp.argmax(),'self.ff[self.pp.argmax()]',self.ff[self.pp.argmax()]+self.fcenter,'SRF[aux]',self.SRF[self.aux])
        print(f'Brho initial: {self.BRho}')
        self.BRhoCorrection()
        print(f'Brho final: {self.BRho}')

        # Calculate new simulated frecuency sample spectrum
        self.SRF = [element*self.Frequence_Rel*self.Harmonic for element in self.SRRF]
        
    def tominimize(self,x): # function to minimize (x=Brho); yup, it's big
        a=sqrt(pow(x*self.RefQ*AMEData.CC/self.m[self.aux],2)+1)
        b=sqrt(a*a-1)/a
        c=AMEData.CC*b
        d=c/self.ring.circumference
        e=d*self.Harmonic*self.SRRF[self.aux]
        tominimize=abs((self.ff[self.pp.argmax()]+self.fcenter)-e)
        return tominimize
   
    def BRhoCorrection(self): # Performs minimization of f_data[IsochroIon]-f_sample[RefIon(Brho)]
        print('function to minimize before minimizing: ',self.tominimize(self.BRho))
        self.BRho=minimize(self.tominimize,[self.BRho],method='CG').x[0]
        print('function to minimized: ',self.tominimize(self.BRho))
        self.gamma=np.sqrt(pow(self.BRho*self.RefQ*AMEData.CC/self.m[self.aux],2)+1)
        self.beta=np.sqrt(self.gamma*self.gamma-1)/self.gamma
        self.velocity=AMEData.CC*self.beta
        self.Frequence_Rel=self.velocity/self.ring.circumference
        
    def _output(self):
        pass
        # for example: 
        # self.myhistogramdata = 
        # self.myvariabledata = 

# eventually should be in __init__ with filename
# specified inside InputParameters.txt
# main could be console user interface until gui is made
def main():
    # specified file is list of filenames
    # filename='data/245-m'
    filename = 'data/410-j'
    
    # opens list of filenames and extracts data from each file
    with open(filename) as f:
        files = f.readlines()
        for file in files:
            #[:-1] to remove eol sequence
            test = ImportData(file[:-1])


if __name__ == '__main__':
    main()
