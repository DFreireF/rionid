from iqtools import * 
from ROOT import * 
import numpy as np
from amedata import *
from particle import *
from ring import Ring
from lisereader import *
from inputparams import*

class e143_tiq_data():
  def __init__(self,filename):
    self.filename=filename
    self.ring=Ring('ESR', 108.5) #have to add more functionalities here
    ame = AMEData()
    ame.init_ame_db
    self.ame_data = ame.ame_table
    #Importing input params
    self.params_file = 'data/InputParameters.txt'
    self.input_params=InputParams(self.params_file)
    #Load LISE file
    lise_file = LISEreader(self.input_params.lisefile)
    self.lise_data = lise_file.get_info_all()     
    self.m,self.moq,self.SRRF,self.SRF,self.Nx_SRF,self.Nx_SRRF=([] for i in range(6))
  
  def fft_root(self,filename):   
    LFRAMES = 2**10
    NFRAMES = 2*4
    iq = TIQData(filename)
    iq.read_samples(LFRAMES*NFRAMES)
    self.ff, self.pp, _ = iq.get_fft()  #1D frec and power
    self.pp = self.pp / self.pp.max()  # normalized
    self.h = TH1D('h', 'h', len(self.ff), iq.center + self.ff[0], iq.center + self.ff[-1])
    for i in range(len(self.ff)):
      self.h.SetBinContent(i, self.pp[i])
    self.nbins = self.h.GetXaxis().GetNbins()
    self.frequence_min = self.h.GetXaxis().GetXmin()/1000 + 245
    self.frequence_max = self.h.GetXaxis().GetXmax()/1000 + 245
    self.y_max = self.h.GetMaximum()
    self.h.GetXaxis().SetLimits(self.frequence_min, self.frequence_max)
  
  def calculate(self,filename):     
    Flag = ''
    while Flag != 'exit':                     
      for i, lise in enumerate(self.lise_data):
        for ame in self.ame_data:
          if lise[0]==ame[6] and lise[1]==ame[5]:
            particle_name = Particle(lise[2],lise[3],AMEData(),self.ring)
            self.m.append(AMEData.to_mev(particle_name.get_ionic_mass_in_u()))
            self.moq.append(particle_name.get_ionic_moq_in_u())
                
            if (str(lise[1])+lise[0] == self.input_params.dict['ReferenceIsotope']
                and lise[4] == self.input_params.dict['ReferenceIsotopeCharge']):
              moq_Rel = self.moq[i]
              self.gamma = sqrt(pow(self.input_params.dict['Brho']*lise[4]*AMEData.CC/self.m[i], 2)+1)
              self.beta = sqrt(self.gamma * self.gamma - 1)/self.gamma
              self.velocity = AMEData.CC * self.beta
              Frequence_Rel = self.velocity/self.ring.circumference
                  
      for k in range(0,len(self.m)):
        # 1. simulated relative revolution frequency
        self.SRRF.append(1-1/self.input_params.dict['GAMMAT'] /
                  self.input_params.dict['GAMMAT']*(self.moq[k]-moq_Rel)/moq_Rel)
        # 2. simulated revolution frequency
        self.SRF.append(self.SRRF[k]*Frequence_Rel *
                           (self.input_params.dict['Harmonic']))
            
          
      print('Brho = ',self.input_params.dict['Brho'],'mass',self.m)
      print('exit or not? introduce exit')
      Flag=input('Enter exit to finish Brho manual adjustment:')
      if Flag=='exit':
        break
      else:
        self.input_params=InputParams(self.params_file) #reads input again after modification
# ================== execution =====================
def main():
  filename='data/245-j'
  with open(filename) as f:
    files = f.readlines()
    for file in files:
      test=e143_tiq_data(file[:-1]) #initialization   
      test.fft_root(file[:-1])
      test.calculate(file[:-1]) # initialization
        
#this tests when program is run  
if __name__ == '__main__':
  try:
    main()
  except:
    raise
