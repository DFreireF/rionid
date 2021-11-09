from ROOT import *
import numpy as np
import lisereader as lread
import iqtools as iqt
from amedata import *
#from particle import *
from ring import Ring
import inputparams
import canvasformat as cvfmt

class SimTOF():
  def __init__(self, filename):
    self.filename = filename
    
    # canvas:
    mycanvas=cvfmt.CanvasFormat()
    mycanvas.set_latex_format()
    mycanvas.set_latex_labels()
    r3, c0, c, c_1, c_2_1, c_2_2, c_3, c_4 = mycanvas.setup_tpad()
    
    # gstyle:
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gGAMMAT = mycanvas.gammat_calculator()
    gGAMMAT.Print()    
  
    # fft:
    # SimTOF.fft_root(needs_filename)

    # 1. Import ame 
    ame = amedata.AMEData()
    ame.init_ame_db
    ame_data = ame.ame_table
    # 2. Importing in put params
    params_file = 'data/InputParameters.txt' #initial seeds; although can be changed to just declaring variables here
    input_params=InputParameters(params_file)
    # 3. Load LISE file
    lise_file = lread.LISEreader(input_params.lisefile)
    lise_data = lise_file.get_info_all()
    
    gCharge, gZ, gA, gmoq, gi, gSim = SimTOF.root_graph()
    
    SimTOF.make_graphs()
    
    #then big while loop must go here, so it should be a function
  
  @staticmethod
  def fft_root(filename):
    LFRAMES = 2**18
    NFRAMES = 2*8
    iq = iqt.get_iq_object(filename)
    iq.iqt.read_samples(LFRAMES*NFRAMES)

    ff, pp, _ = iq.get_fft()  # frec and power
    pp = pp / pp.max()  # normalized

    h = TH1F('h', 'h', len(ff), iq.center + ff[0], iq.center + ff[-1])
    for i in range(len(ff)):
      h.SetBinContent(i, pp[i])
    f = TFile(filename + '.root', 'RECREATE')
    h.Write()
    f.GetObject('FFT-', h)
    f.close()

    nbins = h.GetXaxis().GetNbins()
    frequence_min = h.GetXaxis().GetXmin()/1000 + 245
    frequence_max = h.GetXaxis().GetXmax()/1000 + 245
    y_max = h.GetMaximum()
    h.GetXaxis().SetLimits(frequence_min, frequence_max)

    return nbins, frequence_min, frequence_max, y_max

  @staticmethod #for future code
  def read_to_root(filename):
    with open(filename) as f:
      files = f.readlines()
    for file in files:
      self.FFT_root(file)
      #find brho
      
  @staticmethod
  def root_histo(nbins, frequence_center, frequence_min, frequence_max, Frequence_Tl):
    hSim = TH1F('hSim', 'hSim', 200e3, 400, 700)
    # FFT px ref
    h_ref = TH1F('h_ref', 'h_ref',
                 nbins, (frequence_center+frequence_min)/Frequence_Tl,
                 (frequence_center+frequence_max)/Frequence_Tl)
    # SRF
    hSRF = TH1F('hSRF', 'simulated revolution frequence',
                nbins, (frequence_center+frequence_min),
                (frequence_center+frequence_max))
    # SRRF
    hSRRF = TH1F('hSRRF', 'simulated relative revolution frequence',
                 nbins, (frequence_center+frequence_min)/Frequence_Tl,
                 (frequence_center+frequence_max)/Frequence_Tl)
    hSRF.SetLineStyle(2)
    hSRRF.SetLineStyle(2)
    return h_ref, hSRF, hSRRF
      
  @staticmethod
  def root_graph():
    gCharge = TGraph()
    gZ   = TGraph()
    gA   = TGraph()
    gmoq = TGraph()
    gi   = TGraph()
    gSim = TGraph()
    gSim.SetLineColor(2)
    gSim.SetName('gSim')
    return gCharge, gZ, gA, gmoq, gi, gSim
  
  @staticmethod #this doesnt need method, can just go in loop directly.
  def remove_point(gZ,gA,gCharge,gmoq, gi):
    gZ.RemovePoint(0)
    gA.RemovePoint(0)
    gCharge.RemovePoint(0)
    gmoq.RemovePoint(0)
    gi.RemovePoint(0)
      
  @staticmethod
  def root_sort(gZ, gA, gCharge, gmoq, gi):  # sort in decreasing order
    gZ.Sort()
    gA.Sort()
    gCharge.Sort()
    gmoq.Sort()
    gi.Sort()
    return gZ, gA, gCharge, gmoq, gi
        
  @staticmethod
  def make_graphs():
    c_1.cd()
    gPad.SetBottomMargin(0.08)
    h.Draw()
    h.GetXaxis().SetRangeUser(input_params.dict['RefRangeMin1'],input_params.dict['RefRangeMax1'])
    hSRF.Draw('same')
    hSRF.SetLineColor(3)
    c_1.Update()
      
    c_2.cd()
    gPad.SetBottomMargin(0.01)
    for nnn in h.GetXaxis().GetNbins():
      x_ref = (h.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
      y = h.GetBinContent(nnn)
      nx_ref = h_ref.GetXaxis().FindBin(x_ref)
      h_ref.SetBinContent(nx_ref, y_max)

    h_ref.Draw()
    h_ref.Scale(0.00000001)
    h_ref.GetYaxis().SetRangeUser(1, 1e3)
    h_ref.GetXaxis().SetRangeUser(
        input_params.dict['RefRangeMin2'], input_params.dict['RefRangeMax2'])
    hSRRF.Draw('same')

    c_2_1.cd()
    h_ref_small1 = h_ref.Clone('h_ref_small1')
    h_ref_small1.Draw()
    h_ref_small1.GetXaxis().SetRangeUser(1.0010, 1.0032)
    hSRRF.Draw('same')
    
    c_2_2.cd()
    h_ref_small2 = h_ref.Clone('h_ref_small2')
    h_ref_small2.Draw()
    h_ref_small2.GetXaxis().SetRangeUser(0.99994, 1.00004)
    hSRRF.Draw('same')
  
    c_3.cd()
    gPad.SetTopMargin(0.01)
    gPad.SetTickx(1)
    hSRRF.Draw('')
    hSRRF.SetLineColor(2)
    hSRRF.GetXaxis().SetTitle('relative revolution frequence')
    hSRRF.GetXaxis().CenterTitle(true)
    hSRRF.GetXaxis().SetLabelFont(42)
    hSRRF.GetXaxis().SetLabelSize(0.10)
    hSRRF.GetXaxis().SetTitleSize(0.10)
    hSRRF.GetXaxis().SetTitleFont(42)
    hSRRF.GetYaxis().SetTitle('arb. units')
    hSRRF.GetYaxis().CenterTitle(true)
    hSRRF.GetYaxis().SetLabelFont(42)
    hSRRF.GetYaxis().SetLabelSize(0.10)
    hSRRF.GetYaxis().SetTitleSize(0.10)
    hSRRF.GetYaxis().SetTitleFont(42)
    hSRRF.GetYaxis().SetTitleOffset(0.5)
    hSRRF.GetYaxis().SetNdivisions(505)
    hSRRF.GetXaxis().SetRangeUser(
        input_params.dict['RefRangeMin2'], input_params.dict['RefRangeMax2'])
    hSRRF.Scale(100)
    c_3.Update()
      
    c_4.cd()
    gGAMMAT.Draw('al')
    gGAMMAT.GetXaxis().SetLimits((frequence_center+frequence_min)/Frequence_Tl,
                                 (frequence_center+frequence_max)/Frequence_Tl)
    gGAMMAT.GetYaxis().SetRangeUser(2.412, 2.432)
    c_4.Update()
      
  @staticmethod
  def print_out_or_not(self):  
    gSystem.ProcessEvents()
    gSystem.Sleep(10)
    print('Frequence_Rel = ', Frequence_Rel)
    print('Harmonic = ',Harmonic)
    print('Frequence_Rel*(Harmonic) = ',Frequence_Rel*(Harmonic))
    print('Frequence_Tl  = ',Frequence_Tl)
    print('exit or not? introduce exit')
    Flag=input('Enter exit to finish Brho manual adjustment:')
    if Flag=='exit':
      fout_root = TFile.Open(('simtof_%d.tof',input_params.dict['Harmonic']),'recreate')
      h.Write()
      h_ref.Write()
      hSRRF.Write()
      hSRF.Write()
      fout_root.Close()
      c.Print('result.pdf')
          
  #=================== execution ====================          
  
  #this should go under __init__ once it is a function
  Flag = ''
  while Flag != 'exit':
    self.root_histo()
    self.root_graph()
    self.setup_tpad()
    self.remove_points()
    k = 0
    Frequence_Tl     = 243.2712156 #MHz
    frequence_center = 0
    OrbitalLength    = 108430 #mm
    fout = open(('output_%d.tof', input_params.dict['Harmonic']), 'a')
    for i, lise in enumerate(lise_data):
      for ame in ame_data:
        if lise[0]==ame[6] and lise[1]==ame[5]:
            particle_name = Particle(lise[2],lise[3],ame_data,Ring('ESR', 108.5))
            m[k] = amedata.to_mev(particle_name.get_ionic_mass_in_u())
            moq[k] = particle_name.get_ionic_moq_in_u()
            gZ   .SetPoint(k, moq[k], lise[2])
            gA   .SetPoint(k, moq[k], lise[1])
            gCharge.SetPoint(k, moq[k], lise[4])
            gmoq .SetPoint(k, moq[k], moq[k])
            gi   .SetPoint(k, moq[k], lise[5])
            if (lise[0]==input_params.dict['ReferenceIsotope'] and lise[4]==input_params.dict['ReferenceIsotopeCharge']):
                moq_Rel = moq[k]
                gamma         = sqrt(pow(input_params.dict['Brho']*lise[4]/AMEData.CC/m,2)+1) # c was wrong (relations + unit analysis)
                beta          = sqrt(gamma * gamma - 1)/gamma
                velocity      = AMEData.CC * beta
                Frequence_Rel = 1000/(OrbitalLength / velocity)
                
            # 1. simulated relative revolution frequency
            SRRF[k] = 1-1/input_params.dict['GAMMAT'] / \
                input_params.dict['GAMMAT']*(moq[k]-moq_Rel)/moq_Rel
            # 2. simulated revolution frequency
            SRF[k] = SRRF[k]*Frequence_Rel*(input_params.dict['Harmonic'])
            Nx_SRF[k] = hSRF.GetXaxis().FindBin(SRF[k])
            hSRF.SetBinContent(Nx_SRF[k], lise[5]*y_max*0.01)
            # 3.
            SRRF[k] = SRF[k]/(Frequence_Rel*(input_params.dict['Harmonic']))
            Nx_SRRF[k] = hSRRF.GetXaxis().FindBin(SRRF[k])
            hSRRF.SetBinContent(Nx_SRRF[k], 1)
            #fout
            fout.write(lise[0], '\t', lise[2], '\t', lise[1], '\t', lise[4], '\t', int(
                input_params.dict['Harmonic']), '\t', moq[k], ' ue,\t f/f0 = ', SRRF, ' \t', SRF, ' MHz,\t', lise[5])
            k += 1
    fout.close()
    self.root_sort()
    self.make_graphs()
    self.latex_labels()
    self.print_out_or_not()
  ##while ends

# ================== testing =====================
def test():
  print('here is where you can check that routines work')
  
#this tests when program is run  
if __name__ == '__main__':
  #here you can put the filenames of files you want to test
  #introduce 245-j.txt file
  try:
      test()
  except:
      raise
