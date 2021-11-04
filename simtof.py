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
    Frequence_Tl     = 243.2712156
    frequence_center = 0
    OrbitalLength    = 108430
    
  filename = '245-j.txt'  # this needs to go in test section

  def read_to_root(self, filename):
    with open(filename) as f:
        files = f.readlines()
    for file in files:
        self.FFT_root(file)
        #implement ruiju brho-root ploting and find brho

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

  # 2. Load binding energy file
  fBindingEnergy = np.genfromtxt('data/ElBiEn_2007.dat', skip_header=11)

  # 3. Load LISE file
  LISEFileName = 'data/E143_TEline-ESR-72Ge.lpp'
  lise_file = lread.LISEreader(LISEFileName)
  lise_data = lise_file.get_info_all()
  
  # 4. Importing Input params
  params_file = 'data/InputParameters.txt'
  inputparams={k:(float(v) if v.replace('.','').isdigit() else v) 
               for k,v in [line.split() for line in open(params_file)]}
  
  # new tgraphs
  hSim = TH1F('hSim','hSim',200e3,400,700)
  gCharge = TGraph()
  gZ   = TGraph()
  gA   = TGraph()
  gmoq = TGraph()
  gi   = TGraph()
  gSim = TGraph()
  gSim.SetLineColor(2)
  gSim.SetName('gSim')

  # FFT px ref
  hFFT_px_ref = TH1F('hFFT_px_ref', 'hFFT_px_ref',
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

  gZ.RemovePoint(0)
  gA.RemovePoint(0)
  gCharge.RemovePoint(0)
  gmoq.RemovePoint(0)
  gi.RemovePoint(0)

# next section can replace with barion function 
  # for(int j=0,j<NProductions,j++)
  # need new for loop
  # e.g. for i,element in lise_data:
  
    #  NUCNAM from ame, PRONAM from lise
    # if(NUCNAM[i] == PRONAM[j])
    
    # below: if name string and A number match:
  for lise in lise_data:
    for ame in ame_data:
      if lise[0]==ame[6] and lise[1]==ame[5]:
        particle_name = Particle(zz,nn,ame_data,ring)
        m = amedata.to_mev(particle_name.get_ionic_mass_in_u())
        moq = particle_name.get_ionic_moq_in_u()
      
      m = A[i]*bar.AMEData.UU + MassExcess[i]/1e3 - Z[i]*bar.AMEData.ME + BindingEnergyDB[Z[i]][ChargeDB[j]-1]/1e6 #in MeV
      moq = m/ChargeDB[j]/bar.AMEData.UU
      gZ   .SetPoint(k, moq, Z[i])
      gA   .SetPoint(k, moq, A[i])
      gCharge.SetPoint(k, moq, ChargeDB[j])
      gmoq .SetPoint(k, moq, moq)
      gi   .SetPoint(k, moq, j)
      if(NUCNAM[i] == ReferenceIsotope and ChargeDB[j] == ReferenceIsotopeCharge)
      moq_Rel = moq
        gamma         = sqrt(pow(Brho*ChargeDB[j]*bar.AMEData.CC/m,2)+1)
        beta          = sqrt(gamma*gamma -1)/gamma
        velocity      = bar.AMEData.CC * beta
        Frequence_Rel = 1000/(OrbitalLength/velocity)

  gZ.Sort()
  gA.Sort()
  gCharge.Sort()
  gmoq.Sort()
  gi.Sort()
  char tmp[100]
  sprintf(tmp,'output_%d.tof',Harmonic)
  ofstream fout(tmp)
  std::cout.precision(10)

  double index,ZZZ,AAA,Charge,moq,SRRF,SRF
  int kkk=0
  for(int i=0i<gZ.GetN()i++)
    gZ     .GetPoint(i,moqDB[i],ZZZ)	
    gA     .GetPoint(i,moqDB[i],AAA)	
    gCharge.GetPoint(i,moqDB[i],Charge)	
    gmoq   .GetPoint(i,moqDB[i],moq)	
    gi     .GetPoint(i,moqDB[i],index)

    # 1. simulated relative revolution frequency
    SRRF   = 1-1/GAMMAT/GAMMAT*(moqDB[i]-moq_Rel)/moq_Rel

    # 2. simulated revolution frequency
    SRF= SRRF*Frequence_Rel*(Harmonic)
    Nx_SRF = hSRF.GetXaxis().FindBin(SRF)
    hSRF.SetBinContent(Nx_SRF,PPS[(index)]*y_max*0.01)

    # 3. 
    SRRF = SRF/(Frequence_Rel*(Harmonic))
    Nx_SRRF = hSRRF.GetXaxis().FindBin(SRRF)
    hSRRF.SetBinContent(Nx_SRRF,1)

    fout<<std::fixed<<PRONAM[int(index)]<<'\t'<<int(ZZZ)<<'\t'<<int(AAA)<<'\t'<<int(Charge)<<'\t'<<setw(2)<<int(Harmonic)<<'\t'<<setw(2)<<setw(5)<<moqDB[i]<<' ue,\t f/f0 = '<<setw(5)<<SRRF<<' \t'<<setw(5)<<SRF<<' MHz,\t'<<setw(10)<<PPS[int(index)]<<endl
    cout<<std::fixed<<PRONAM[int(index)]<<'\t'<<int(ZZZ)<<'\t'<<int(AAA)<<'\t'<<int(Charge)<<'\t'<<setw(2)<<int(Harmonic)<<'\t'<<setw(2)<<setw(5)<<moqDB[i]<<' ue,\t f/f0 = '<<setw(5)<<SRRF<<' \t'<<setw(5)<<SRF<<' MHz,\t'<<setw(10)<<PPS[int(index)]<<endl
  }
      fout.close()

  c_1.cd()
  gPad.SetBottomMargin(0.08)
  hFFT_px.Draw()
  hFFT_px.GetXaxis().SetRangeUser(RefRangeMin1,RefRangeMax1)
  hSRF.Draw('same')
  hSRF.SetLineColor(3)
  c_1.Update()

  c_2.cd()
  gPad.SetBottomMargin(0.01)
  for(int nnn=0nnn<hFFT_px.GetXaxis().GetNbins()nnn++)
            
  double x_ref = (hFFT_px.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
  double y     = hFFT_px.GetBinContent(nnn)
  Int_t nx_ref = hFFT_px_ref. GetXaxis().FindBin(x_ref)
  hFFT_px_ref.SetBinContent(nx_ref,y)

  hFFT_px_ref.Draw()
  hFFT_px_ref.Scale(0.00000001)
  hFFT_px_ref.GetYaxis().SetRangeUser(1,1e3)
  hFFT_px_ref.GetXaxis().SetRangeUser(RefRangeMin2,RefRangeMax2)
  hSRRF.Draw('same')

  c_2_1.cd()
  hFFT_px_ref_small1  = hFFT_px_ref.Clone('hFFT_px_ref_small1')
  hFFT_px_ref_small1.Draw()
  hFFT_px_ref_small1.GetXaxis().SetRangeUser(1.0010,1.0032)
  hSRRF.Draw('same')

  c_2_2.cd()      
  hFFT_px_ref_small2  = hFFT_px_ref.Clone('hFFT_px_ref_small2')
  hFFT_px_ref_small2.Draw()
  hFFT_px_ref_small2.GetXaxis().SetRangeUser(0.99994,1.00004)
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
  hSRRF.GetXaxis().SetRangeUser(RefRangeMin2,RefRangeMax2)
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
  cout<<'Harmonic = '<<Harmonic<<endl
  cout<<'Frequence_Rel*(Harmonic) = '<<Frequence_Rel*(Harmonic)<<endl
  cout<<'Frequence_Tl  = '<<Frequence_Tl<<endl
  cin>>Flag
  cout<<Flag<<endl

    
  char tmp[100]
  sprintf(tmp,'simtof_%d.root',Harmonic)
  TFile = TFile(tmp,'recreate')
  hFFT_px.Write()
  hFFT_px_ref.Write()
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
