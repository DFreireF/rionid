from ROOT import *
import numpy as np
from scipy.constants import physical_constants

import Barion as bar

#importing constants
amu    = physical_constants['atomic mass constant energy equivalent in MeV'][0]
Clight = physical_constants['speed of light in vacuum'][0]
me     = physical_constants['electron mass energy equivalent in MeV'][0]

#############################################################
######################### SIMTOF.PY #########################
#############################################################
# --------------------------------------------------------- #
#     Originally written in C++ by Dr. Rui Jiu Chen         #
#                           ---                             #
#         Adapted to Python by George Hudson-Chang          #
# --------------------------------------------------------- #

class simtof():###
    
    def SetPadFormat (self):
      self.c_1 = SetPadFormat(TPad)
      self.c_1.SetLeftMargin(0.10)
      self.c_1.SetRightMargin(0.05)
      self. c_1.SetTopMargin(0.12)
      self. c_1.SetBottomMargin(0.25)
      self. c_1.SetFrameBorderMode(0)
      self.c_1.SetLogy(1)
      self. c_1.Draw()
    def SetCanvasFormat (self):
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
      gGAMMAT.SetName("gGAMMAT")
      gGAMMAT.SetPoint(0,0.998,2.4234 + (0.98 - 1)*k)
      gGAMMAT.SetPoint(1,1.000,2.4234 + (1.000 - 1)*k)
      gGAMMAT.SetPoint(2,1.002,2.4234 + (1.02 - 1)*k)
      return gGAMMAT
    
    gStyle.SetOptStat(0)
    gStyle.SetOptTitle(0)
    gGAMMAT = GAMMATCalculator()
    gGAMMAT.Print()
    
    # hFFT_px
    ###Insert routine that reads and transform every file in a loop
    def read(self,)
    fdata = TFile("0000017.iq.tdms.root")
    TH1D = hFFT_px #please check this against original line! TH1D *hFFT_px

    fdata.GetObject("FFT_Average",hFFT_px)
    nbins         = hFFT_px.GetXaxis().GetNbins()
    frequence_min = hFFT_px.GetXaxis().GetXmin()
    frequence_max = hFFT_px.GetXaxis().GetXmax()
    y_max         = hFFT_px.GetMaximum()

    # User output
    print(f"nbins = {nbins}")
    print(f"frequence_min = {frequence_min}")
    print(f"frequence_max = {frequence_max}")

    #setting new min/max
    frequence_min = 245 + frequence_min/1000
    frequence_max = 245 + frequence_max/1000
    #setting limits
    hFFT_px.GetXaxis().SetLimits(frequence_min, frequence_max)

    # ============ declaring variables ================
    Frequence_Tl     = 243.2712156
    frequence_center = 0
    OrbitalLength    = 108430

    NA       = 0
    lines    = 0
    FlagRead = False

    # ========= declaring even more variables ==========
    # These were initialised as strings:
    # NUCNAM[6000], ET[6000], PPSString1[6000]
    # PRONAM[6000],PPSString[6000],ChargeString[6000]

    # LISEFileName, T1, lineBuffer, Flag
    # P[30001],ReferenceIsotopeCharge
    # m,me,amu,BindingEnergy
    # Clight,E,U,GAMMAT,CSREL,EMASS,UK,ACCP,Brho,gamma,beta,velocity,
    # RevolutionTime_Rel,Frequence_Rel, m_Rel,moq,moq_Rel,Z_Rel,dpop,
    # dToTSystem,RefRangeMin1,RefRangeMax1,RefRangeMin2,RefRangeMax2,
    # RefRangeMin3,RefRangeMax3,ScaleFactor
    # StartLine,StopLine,NProductions,Harmonic
    # char PPStmp[20]
    # string ReferenceIsotope
    # ifstream fAME03,fLISE,fBindingEnergy

    # ============= 1. Importing ame data ==================
    # filename: 
    datafile_name = "data/mass.rd"
    print(f"reading ame data from {datafile_name}")

    # importing mass names from first column
    mass_name=np.loadtxt(datafile_name,usecols=0,dtype=str)

    # importing mass data into array for floats
    numcols  = np.arange(0,4,1) #for extracting the 5 float columns
    numrows  = 3250 #3250 rows of data
    mass_dat = np.zeros((len(numcols),numrows)) #initialise empty array

    for i in range(len(numcols)):
      mass_dat[i,:] = np.loadtxt(datafile_name, usecols=(numcols[i]+1), \
        dtype=float)

    # mass_dat=np.genfromtxt(datafile_name)

    print("Read ame ok.")

    #  ========= 2. Load binding energy file ===========
    print("Read from ElBiEn_2007.dat")
    fBindingEnergy = np.loadtxt("ElBiEn_2007.dat")
    print("Read ok.")

    # ============== 3. Load LISE file =================
    LISEFileName = "simtof/E143_TEline-ESR-72Ge.lpp"
    print(f"reading from {LISEFileName}")
    # (reading from calculations part: isotope name and 6th charge state.)
    # np.genfromtxt(LISEFileName,dtype=str)
    print("Read ok.")

    hSim = TH1F("hSim","hSim",200e3,400,700)
    gZ   = TGraph()
    gA   = TGraph()
    gCharge = TGraph()
    gmoq = TGraph()
    gi   = TGraph()
    gSim = TGraph()
    gSim.SetLineColor(2)
    gSim.SetName("gSim")

    # FFT px ref
    hFFT_px_ref = TH1F("hFFT_px_ref","hFFT_px_ref", \
       nbins,(frequence_center+frequence_min)/Frequence_Tl, \
         (frequence_center+frequence_max)/Frequence_Tl)
    # SRF
    hSRF  = TH1F("hSRF", "simulated revolution frequence", \
      nbins,(frequence_center+frequence_min), \
        (frequence_center+frequence_max))
    # SRRF
    hSRRF = TH1F("hSRRF","simulated relative revolution frequence", \
      nbins,(frequence_center+frequence_min)/Frequence_Tl, \
        (frequence_center+frequence_max)/Frequence_Tl)

    hSRF.SetLineStyle(2)
    hSRRF.SetLineStyle(2)

    # ================= 4. Tpad Setup =================
    #Tpad r3
    r3 = TRandom3()

    #Tpad c0
    c0 = TCanvas("c0", "c0",0,0,1000,300)
    SetCanvasFormat(c0)

    #Tpad c
    c = TCanvas("c", "c",0,0,1000,880)
    SetCanvasFormat(c)
    c.cd()

    #Tpad c_1
    c_1 = TPad("c_1", "c_1",0.00,0.75,0.99,0.99)
    SetPadFormat(c_1)
    c.cd()

    #Tpad c_2
    c_2 = TPad("c_2", "c_2",0.0,0.50,0.99,0.75)
    SetPadFormat(c_2)
    c.cd()

    #Tpad c_2_1
    c_2_1 = TPad("c_2_1", "c_2_1",0.70,0.6,0.86,0.7189711)
    SetPadFormat(c_2_1)
    c_2_1.SetLeftMargin(0.02857143)
    c_2_1.SetRightMargin(0.02857143)
    c_2_1.SetTopMargin(0.01851852)
    c_2_1.SetBottomMargin(0.01851852)

    #Tpad c_2_2
    c_2_2 = TPad("c_2_2", "c_2_2",0.45,0.6,0.61,0.7189711)
    SetPadFormat(c_2_2)
    c_2_2.SetLeftMargin(0.02857143)
    c_2_2.SetRightMargin(0.02857143)
    c_2_2.SetTopMargin(0.01851852)
    c_2_2.SetBottomMargin(0.01851852)
    c.cd()

    #Tpad c_3
    c_3 = TPad("c_3", "c_3",0.0,0.25,0.99,0.50)
    SetPadFormat(c_3)
    c.cd()

    #Tpad c_4
    c_4 = TPad("c_4", "c_4",0.0,0.0,0.99,0.25)
    SetPadFormat(c_4)
    c_4.SetLogy(0)

    # ============= 5. Importing Input params ===============
    # Imported as strings 
    params_file = "simtof/InputParameters.txt"
    print(f"reading input parameters from {params_file}")
    with open(params_file) as f:
      inputparams = dict([line.split() for line in f])
    print(f"read ok.")

    gZ.RemovePoint(0)
    gA.RemovePoint(0)
    gCharge.RemovePoint(0)
    gmoq.RemovePoint(0)
    gi.RemovePoint(0)


              for(int j=0,j<NProductions,j++)
                {
                  if(NUCNAM[i] == PRONAM[j])
                    {
                      m                 = A[i]*amu + MassExcess[i]/1e3 - Z[i]*me + BindingEnergyDB[Z[i]  ][ChargeDB[j]-1]/1e6   // MeV 
                      moq               = m/ChargeDB[j]/amu
                      gZ   .SetPoint(k,moq,Z[i])
                      gA   .SetPoint(k,moq,A[i])
                      gCharge   .SetPoint(k,moq,ChargeDB[j])
                      gmoq .SetPoint(k,moq,moq)
                      gi   .SetPoint(k,moq,j)
                      if(NUCNAM[i] == ReferenceIsotope&&ChargeDB[j]==ReferenceIsotopeCharge)
                        {
                          moq_Rel           = moq
                          gamma             = sqrt(pow(Brho*ChargeDB[j]*Clight/m,2)+1)
                          beta              = sqrt(gamma*gamma -1)/gamma
                          velocity          = Clight * beta
                          Frequence_Rel     = 1000/(OrbitalLength/velocity)
                        }
                      k++
                    }
                }	
            }
          gZ.Sort()
          gA.Sort()
          gCharge.Sort()
          gmoq.Sort()
          gi.Sort()
          char tmp[100]
          sprintf(tmp,"output_%d.tof",Harmonic)
          ofstream fout(tmp)
          std::cout.precision(10)

          double index,ZZZ,AAA,Charge,moq,SRRF,SRF
          int kkk=0
          for(int i=0i<gZ.GetN()i++)
            {
              gZ     .GetPoint(i,moqDB[i],ZZZ)	
              gA     .GetPoint(i,moqDB[i],AAA)	
              gCharge.GetPoint(i,moqDB[i],Charge)	
              gmoq   .GetPoint(i,moqDB[i],moq)	
              gi     .GetPoint(i,moqDB[i],index)

              # ====== 1. simulated relative revolution frequence ======
              SRRF   = 1-1/GAMMAT/GAMMAT*(moqDB[i]-moq_Rel)/moq_Rel

              # ====== 2. simulated revolution frequence ===============
              SRF= SRRF*Frequence_Rel*(Harmonic)
              Nx_SRF = hSRF.GetXaxis().FindBin(SRF)
              hSRF.SetBinContent(Nx_SRF,PPS[(index)]*y_max*0.01)

              # ====== 3. ===============================================
              SRRF = SRF/(Frequence_Rel*(Harmonic))
              Nx_SRRF = hSRRF.GetXaxis().FindBin(SRRF)
              hSRRF.SetBinContent(Nx_SRRF,1)

              fout<<std::fixed<<PRONAM[int(index)]<<"\t"<<int(ZZZ)<<"\t"<<int(AAA)<<"\t"<<int(Charge)<<"\t"<<setw(2)<<int(Harmonic)<<"\t"<<setw(2)<<setw(5)<<moqDB[i]<<" ue,\t f/f0 = "<<setw(5)<<SRRF<<" \t"<<setw(5)<<SRF<<" MHz,\t"<<setw(10)<<PPS[int(index)]<<endl
              cout<<std::fixed<<PRONAM[int(index)]<<"\t"<<int(ZZZ)<<"\t"<<int(AAA)<<"\t"<<int(Charge)<<"\t"<<setw(2)<<int(Harmonic)<<"\t"<<setw(2)<<setw(5)<<moqDB[i]<<" ue,\t f/f0 = "<<setw(5)<<SRRF<<" \t"<<setw(5)<<SRF<<" MHz,\t"<<setw(10)<<PPS[int(index)]<<endl
            }
          fout.close()

          c_1.cd()
          gPad.SetBottomMargin(0.08)
          hFFT_px.Draw()
          hFFT_px.GetXaxis().SetRangeUser(RefRangeMin1,RefRangeMax1)
          hSRF.Draw("same")
          hSRF.SetLineColor(3)
          c_1.Update()

          c_2.cd()
          gPad.SetBottomMargin(0.01)
          for(int nnn=0nnn<hFFT_px.GetXaxis().GetNbins()nnn++)
            {
              double x_ref = (hFFT_px.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
              double y     = hFFT_px.GetBinContent(nnn)
              Int_t nx_ref = hFFT_px_ref. GetXaxis().FindBin(x_ref)
              hFFT_px_ref.SetBinContent(nx_ref,y)
            }
          hFFT_px_ref.Draw()
          hFFT_px_ref.Scale(0.00000001)
          hFFT_px_ref.GetYaxis().SetRangeUser(1,1e3)
          hFFT_px_ref.GetXaxis().SetRangeUser(RefRangeMin2,RefRangeMax2)
          hSRRF.Draw("same")

          c_2_1.cd()
          TH1F *hFFT_px_ref_small1  = (TH1F *)hFFT_px_ref.Clone("hFFT_px_ref_small1")
          hFFT_px_ref_small1.Draw()
          hFFT_px_ref_small1.GetXaxis().SetRangeUser(1.0010,1.0032)
          hSRRF.Draw("same")

          c_2_2.cd()      
          TH1F *hFFT_px_ref_small2  = (TH1F *)hFFT_px_ref.Clone("hFFT_px_ref_small2")
          hFFT_px_ref_small2.Draw()
          hFFT_px_ref_small2.GetXaxis().SetRangeUser(0.99994,1.00004)
          hSRRF.Draw("same")

          TLatex *   tex200Au79 = new TLatex(0.9999552,2.176887e+14,"^{200}Au^{79+}")
          tex200Au79.SetTextColor(2)
          tex200Au79.SetTextSize(0.08)
          tex200Au79.SetTextAngle(88.21009)
          tex200Au79.SetLineWidth(2)
          tex200Au79.Draw()

          TLatex *   tex200Hg79 = new TLatex(0.999965,2.176887e+13,"^{200}Au^{79+}")
          tex200Hg79.SetTextColor(2)
          tex200Hg79.SetTextSize(0.08)
          tex200Hg79.SetTextAngle(88.21009)
          tex200Hg79.SetLineWidth(2)
          tex200Hg79.Draw()

          c_3.cd()
          gPad.SetTopMargin(0.01)
          gPad.SetTickx(1)
          hSRRF.Draw("")
          hSRRF.SetLineColor(2)
          hSRRF.GetXaxis().SetTitle("relative revolution frequence")
          hSRRF.GetXaxis().CenterTitle(true)
          hSRRF.GetXaxis().SetLabelFont(42)
          hSRRF.GetXaxis().SetLabelSize(0.10)
          hSRRF.GetXaxis().SetTitleSize(0.10)
          hSRRF.GetXaxis().SetTitleFont(42)
          hSRRF.GetYaxis().SetTitle("arb. units")
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
          gGAMMAT.Draw("al")
          gGAMMAT.GetXaxis().SetLimits((frequence_center+frequence_min)/Frequence_Tl,(frequence_center+frequence_max)/Frequence_Tl)
          gGAMMAT.GetYaxis().SetRangeUser(2.412,2.432)
          c_4.Update()
          //c.Update()

          gSystem.ProcessEvents()
          gSystem.Sleep(10)
          cout<<"exit or not? [Exit,exit]"<<endl
          cout<<"Frequence_Rel = "<<Frequence_Rel<<endl
          cout<<"Harmonic = "<<Harmonic<<endl
          cout<<"Frequence_Rel*(Harmonic) = "<<Frequence_Rel*(Harmonic)<<endl
          cout<<"Frequence_Tl  = "<<Frequence_Tl<<endl
          cin>>Flag
          cout<<Flag<<endl

        }
      char tmp[100]
      sprintf(tmp,"simtof_%d.root",Harmonic)
      TFile *fout_root = new TFile(tmp,"recreate")
      hFFT_px.Write()
      hFFT_px_ref.Write()
      hSRRF.Write()
      hSRF.Write()
      fout_root.Close()
      c.Print("result.pdf")
    }
