from ROOT import *
import numpy as np
import lisereader as lread
import Barion as bar
import iqtools as iqt
import amedata
import particle

class simtof():
  def __init__(self):
    #here enter commands to execute on initialisation
    pass
  
  def SetPadFormat(self):
    self.c_1 = SetPadFormat(TPad)
    self.c_1.SetLeftMargin(0.10)
    self.c_1.SetRightMargin(0.05)
    self.c_1.SetTopMargin(0.12)
    self.c_1.SetBottomMargin(0.25)
    self.c_1.SetFrameBorderMode(0)
    self.c_1.SetLogy(1)
    self.c_1.Draw()

  def SetCanvasFormat(self):
    self.c = SetCanvasFormat(TCanvas)
    self.c.SetFillColor(0)
    self.c.SetBorderMode(0)
    self.c.SetBorderSize(2)
    self.c.SetFrameBorderMode(0)

  def SetLatexFormat(self):
    self.tex = SetLatexFormat(TLatex)
    self.tex.SetTextColor(2)
    self.tex.SetTextAngle(90)
    self.tex.SetLineWidth(2)
    self.tex.Draw()

  def GAMMATCalculator(self):
    gGAMMAT = TGraph()
    k = -0.5
    gGAMMAT.SetName('gGAMMAT')
    gGAMMAT.SetPoint(0, 0.998, 2.4234 + (0.98 - 1)*k)
    gGAMMAT.SetPoint(1, 1.000, 2.4234 + (1.000 - 1)*k)
    gGAMMAT.SetPoint(2, 1.002, 2.4234 + (1.02 - 1)*k)
    return gGAMMAT
    
  gStyle.SetOptStat(0)
  gStyle.SetOptTitle(0)
  gGAMMAT = GAMMATCalculator()
  gGAMMAT.Print()

  def FFT_root(self, filename):
    LFRAMES = 2**18
    NFRAMES = 2*8
    iq = iqt.get_iq_object(filename)
    iq.iqt.read_samples(LFRAMES*NFRAMES)
    iq.iqt.get_spectrogramme()
    ff, pp, _ = iq.get_fft()
    pp = pp / pp.max()
    h = TH1D('h', 'h', len(ff), iq.center + ff[0], iq.center + ff[-1])
    for i in range(len(ff)):
        h.SetBinContent(i, pp[i])
    f = TFile(filename + '.root', 'RECREATE')
    h.Write()
    f.GetObject('FFT_Average', h)
    f.close()
    nbins         = h.GetXaxis().GetNbins()
    frequence_min = h.GetXaxis().GetXmin()/1000 +245
    frequence_max = h.GetXaxis().GetXmax()/1000 +245
    y_max         = h.GetMaximum()
    h.GetXaxis().SetLimits(frequence_min, frequence_max)
    Frequence_Tl     = 243.2712156 #MHz
    frequence_center = 0
    OrbitalLength    = 108430 #mm
    
  filename = '245-j.txt'  # this needs to go in test section; File containing all the data files taken in June with the 245MHz

  def read_to_root(self, filename):
    with open(filename) as f:
        files = f.readlines()
    for file in files:
        self.FFT_root(file)
        #find brho

  # ===================================================
  # 1. Importing ame data
  # datafile_name = 'data/mass.rd' #this also needs to go test section
  # print(f'reading ame data from {datafile_name}')
  # mass_dat = np.genfromtxt(datafile_name, usecols=range(0, 4), dtype=str)
  # print('Read ame ok.')
  
  # 1.1 Import ame instead using barion:
  ame = amedata.AMEData()
  ame.init_ame_db
  ame_data = ame.ame_table
  # needs: NUCNAM (column 5+6), Z(4), A(5), MassExcess (8), ERR (9)

  # 2. Load binding energy file; Not necessay I think
  #fBindingEnergy = np.genfromtxt('data/ElBiEn_2007.dat', skip_header=11)

  # 3. Load LISE file
  LISEFileName = 'data/E143_TEline-ESR-72Ge.lpp'
  lise_file = lread.LISEreader(LISEFileName)
  lise_data = lise_file.get_info_all()
  
  # 4. Importing Input params
  params_file = 'data/InputParameters.txt' #initial seeds; although can be changed to just declaring variables here
  inputparams={k:(float(v) if v.replace('.','').isdigit() else v) 
               for k,v in [line.split() for line in open(params_file)]}
  
  def root_histo(self):
    hSim = TH1D('hSim','hSim',200e3,400,700)
    # FFT px ref
    h_ref = TH1D('h_ref', 'h_ref',
                      nbins, (frequence_center+frequence_min)/Frequence_Tl,
                      (frequence_center+frequence_max)/Frequence_Tl)
    # SRF
    hSRF = TH1D('hSRF', 'simulated revolution frequence',
              nbins, (frequence_center+frequence_min),
              (frequence_center+frequence_max))
    # SRRF
    hSRRF = TH1D('hSRRF', 'simulated relative revolution frequence',
                nbins, (frequence_center+frequence_min)/Frequence_Tl,
                (frequence_center+frequence_max)/Frequence_Tl)
    hSRF.SetLineStyle(2)
    hSRRF.SetLineStyle(2)
    
  self.root_histo()
  # new tgraphs
  def root_graph(self):
    gCharge = TGraph()
    gZ   = TGraph()
    gA   = TGraph()
    gmoq = TGraph()
    gi   = TGraph()
    gSim = TGraph()
    gSim.SetLineColor(2)
    gSim.SetName('gSim')
    
  self.root_graph()

  # ================= 4. Tpad Setup =================
  def setup_tpad(self):
    #Tpad r3
    r3 = TRandom3()
    #Tpad c0
    c0 = TCanvas('c0', 'c0', 0, 0, 1000, 300)
    SetCanvasFormat(c0)
    #Tpad c
    c = TCanvas('c', 'c', 0, 0, 1000, 880)
    SetCanvasFormat(c)
    c.cd()
    #Tpad c_1
    c_1 = TPad('c_1', 'c_1', 0.00, 0.75, 0.99, 0.99)
    SetPadFormat(c_1)
    c.cd()
    #Tpad c_2
    c_2 = TPad('c_2', 'c_2', 0.0, 0.50, 0.99, 0.75)
    SetPadFormat(c_2)
    c.cd()
    #Tpad c_2_1
    c_2_1 = TPad('c_2_1', 'c_2_1', 0.70, 0.6, 0.86, 0.7189711)
    SetPadFormat(c_2_1)
    c_2_1.SetLeftMargin(0.02857143)
    c_2_1.SetRightMargin(0.02857143)
    c_2_1.SetTopMargin(0.01851852)
    c_2_1.SetBottomMargin(0.01851852)
    #Tpad c_2_2
    c_2_2 = TPad('c_2_2', 'c_2_2', 0.45, 0.6, 0.61, 0.7189711)
    SetPadFormat(c_2_2)
    c_2_2.SetLeftMargin(0.02857143)
    c_2_2.SetRightMargin(0.02857143)
    c_2_2.SetTopMargin(0.01851852)
    c_2_2.SetBottomMargin(0.01851852)
    c.cd()
    #Tpad c_3
    c_3 = TPad('c_3', 'c_3', 0.0, 0.25, 0.99, 0.50)
    SetPadFormat(c_3)
    c.cd()
    #Tpad c_4
    c_4 = TPad('c_4', 'c_4', 0.0, 0.0, 0.99, 0.25)
    SetPadFormat(c_4)
    c_4.SetLogy(0)
   
  self.setup_tpad()
  def remove_points(self):
    k=int(gZ.GetN())
    for i in range(0,k):
        gZ.RemovePoint(0)
        gA.RemovePoint(0)
        gCharge.RemovePoint(0)
        gmoq.RemovePoint(0)
        gi.RemovePoint(0)
  
  self.remove_points()

  k=0
  ofstream fout('output_%d.tof',inputparams['Harmonic'])
  # below: if name string and A number match:
  for i,lise in enumerate(lise_data): #i gives line index
    for ame in ame_data:
      if lise[0]==ame[6] and lise[1]==ame[5]:
        particle_name = Particle(zz,nn,ame_data,ring)
        m[k] = amedata.to_mev(particle_name.get_ionic_mass_in_u())
        moq[k] = particle_name.get_ionic_moq_in_u()
        
        gZ   .SetPoint(k, moq[k], lise[2])
        gA   .SetPoint(k, moq[k], lise[1])
        gCharge.SetPoint(k, moq[k], lise[4])
        gmoq .SetPoint(k, moq[k], moq[k])
        gi   .SetPoint(k, moq[k], lise[5])
        if(lise[0] == inputparams['ReferenceIsotope'] and lise[4] == inputparams['ReferenceIsotopeCharge'])
            moq_Rel = moq[k]
            gamma         = sqrt(pow(inputparams['Brho']*lise[4]/bar.AMEData.CC/m,2)+1) #this is wrong (relations + unit analysis) ; c must be dividing (now corrected) --> implications of this? probably it cancels out somehow in the relations of interest calculated
            beta          = sqrt(gamma*gamma -1)/gamma
            velocity      = bar.AMEData.CC * beta
            Frequence_Rel = 1000/(OrbitalLength/velocity)
            
        # 1. simulated relative revolution frequency
        SRRF[k]   = 1-1/inputparams['GAMMAT']/inputparams['GAMMAT']*(moqDB[k]-moq_Rel)/moq_Rel
        # 2. simulated revolution frequency
        SRF[k]= SRRF[k]*Frequence_Rel*(inputparams['Harmonic'])
        Nx_SRF[k] = hSRF.GetXaxis().FindBin(SRF[k])
        hSRF.SetBinContent(Nx_SRF[k],PPS[(index)]*y_max*0.01)
        # 3. 
        SRRF[k] = SRF[k]/(Frequence_Rel*(inputparams['Harmonic']))
        Nx_SRRF[k] = hSRRF.GetXaxis().FindBin(SRRF[k])
        hSRRF.SetBinContent(Nx_SRRF[k],1)
        #fout
        fout<<std::fixed<<PRONAM[int(index)]<<'\t'<<int(ZZZ)<<'\t'<<int(AAA)<<'\t'<<int(Charge)<<'\t'<<setw(2)<<int(inputparams['Harmonic'])<<'\t'<<setw(2)<<setw(5)<<moqDB[i]<<' ue,\t f/f0 = '<<setw(5)<<SRRF<<' \t'<<setw(5)<<SRF<<' MHz,\t'<<setw(10)<<PPS[int(index)]<<endl
        cout<<std::fixed<<PRONAM[int(index)]<<'\t'<<int(ZZZ)<<'\t'<<int(AAA)<<'\t'<<int(Charge)<<'\t'<<setw(2)<<int(inputparams['Harmonic'])<<'\t'<<setw(2)<<setw(5)<<moqDB[i]<<' ue,\t f/f0 = '<<setw(5)<<SRRF<<' \t'<<setw(5)<<SRF<<' MHz,\t'<<setw(10)<<PPS[int(index)]<<endl
        k+=1
        
  fout.close()

  def root_sort(self):#sort in decreasing order
    gZ.Sort()
    gA.Sort()
    gCharge.Sort()
    gmoq.Sort()
    gi.Sort()
    
  self.root_sort()
  
  c_1.cd()
  gPad.SetBottomMargin(0.08)
  h.Draw()
  h.GetXaxis().SetRangeUser(inputparams['RefRangeMin1'],inputparams['RefRangeMax1'])
  hSRF.Draw('same')
  hSRF.SetLineColor(3)
  c_1.Update()

  c_2.cd()
  gPad.SetBottomMargin(0.01)
  for(int nnn=0nnn<h.GetXaxis().GetNbins()nnn++)
            
  double x_ref = (h.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
  double y     = h.GetBinContent(nnn)
  Int_t nx_ref = h_ref. GetXaxis().FindBin(x_ref)
  h_ref.SetBinContent(nx_ref,y)

  h_ref.Draw()
  h_ref.Scale(0.00000001)
  h_ref.GetYaxis().SetRangeUser(1,1e3)
  h_ref.GetXaxis().SetRangeUser(inputparams['RefRangeMin2'],inputparams['RefRangeMax2'])
  hSRRF.Draw('same')

  c_2_1.cd()
  h_ref_small1  = h_ref.Clone('h_ref_small1')
  h_ref_small1.Draw()
  h_ref_small1.GetXaxis().SetRangeUser(1.0010,1.0032)
  hSRRF.Draw('same')

  c_2_2.cd()      
  h_ref_small2  = h_ref.Clone('h_ref_small2')
  h_ref_small2.Draw()
  h_ref_small2.GetXaxis().SetRangeUser(0.99994,1.00004)
  hSRRF.Draw('same')

  #============= latex text: ==============
  tex200Au79 =TLatex(0.9999552,2.176887e+14,'^{200}Au^{79+}')
  tex200Au79.SetTextColor(2)
  tex200Au79.SetTextSize(0.08)
  tex200Au79.SetTextAngle(88.21009)
  tex200Au79.SetLineWidth(2)
  tex200Au79.Draw()

  tex200Hg79 = TLatex(0.999965,2.176887e+13,'^{200}Au^{79+}')
  tex200Hg79.SetTextColor(2)
  tex200Hg79.SetTextSize(0.08)
  tex200Hg79.SetTextAngle(88.21009)
  tex200Hg79.SetLineWidth(2)
  tex200Hg79.Draw()

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
  hSRRF.GetXaxis().SetRangeUser(inputparams['RefRangeMin2'],inputparams['RefRangeMax2'])
  hSRRF.Scale(100)
  c_3.Update()

  c_4.cd()
  gGAMMAT.Draw('al')
  gGAMMAT.GetXaxis().SetLimits((frequence_center+frequence_min)/Frequence_Tl,
                               (frequence_center+frequence_max)/Frequence_Tl)
  gGAMMAT.GetYaxis().SetRangeUser(2.412,2.432)
  c_4.Update()

  gSystem.ProcessEvents()
  gSystem.Sleep(10)
  cout<<'exit or not? [Exit,exit]'<<endl
  cout<<'Frequence_Rel = '<<Frequence_Rel<<endl
  cout<<'Harmonic = '<<inputparams['Harmonic']<<endl
  cout<<'Frequence_Rel*(Harmonic) = '<<Frequence_Rel*(inputparams['Harmonic'])
  cout<<'Frequence_Tl  = '<<Frequence_Tl<<endl
  cin>>Flag
  cout<<Flag<<endl

    
  fout_root = TFile(('simtof_%d.tof',inputparams['Harmonic']),'recreate')
  h.Write()
  h_ref.Write()
  hSRRF.Write()
  hSRF.Write()
  fout_root.Close()
  c.Print('result.pdf')
    
# ================== testing =====================
#here you can put the filenames of files you want to test

def test():
  print('here is where you can check that routines work')
  
#this tests when program is run  
if __name__ == '__main__':
  try:
      test()
  except:
      raise
