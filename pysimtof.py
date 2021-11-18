from iqtools import * #read_samples, TIQData, get_fft
from ROOT import * # (TH1D, TH1F, TGraph, Draw, Update, Scale, cd,
                  # Tfile,Print,
                  # SetBinContent, GetNbins,
                  # SetLineStyle, SetLineColor, SetName, SetLimits,
                  # SetRangeUser, SetBottomMargin, SetTopMargin,
                  # SetLabelFont, SetLabelSize, SetTitleFont, SetTitleSize,
                  # SetTitleOffset, SetNdivisions,
                  # RemovePoint, Sort, SetOptStat,SetOptTitle,
                  # GetXaxis, GetYaxis,GetXmin, GetXmax, GetYmin, GetYmax)
import numpy as np
from amedata import *
from particle import *
from ring import Ring
from inputparams import *
from canvasformat import *
from lisereader import *

class SimTOF():
  def __init__(self):
    pass
      
  @staticmethod
  def fft_root(filename):
    LFRAMES = 2**12
    NFRAMES = 2*4
    iq = TIQData(filename)
    iq.read_samples(LFRAMES*NFRAMES)

    ff, pp, _ = iq.get_fft()  # frec and power
    pp = pp / pp.max()  # normalized
    h = TH1D('h', 'h', len(ff), iq.center + ff[0], iq.center + ff[-1])
    for i in range(len(ff)):
      h.SetBinContent(i, pp[i])

    nbins = h.GetXaxis().GetNbins()
    frequence_min = h.GetXaxis().GetXmin()/1000 + 245
    frequence_max = h.GetXaxis().GetXmax()/1000 + 245
    y_max = h.GetMaximum()
    h.GetXaxis().SetLimits(frequence_min, frequence_max)

    return nbins, frequence_min, frequence_max, y_max, h
      
  @staticmethod
  def root_histo(nbins, frequence_center, frequence_min, frequence_max, Frequence_Tl):
    hSim = TH1F('hSim', 'hSim', 200000, 400, 700)
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
    #hSRF.Draw()
    hSRRF.SetLineStyle(2)
    return h_ref, hSRF, hSRRF #no hSim?
      
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
    k=gZ.GetN()
    for i in range(0,k):
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
  def make_graphs(c_1, c_2, c_2_1, c_2_2, c_3, c_4, h, h_ref, hSRF, hSRRF, input_params,
                  frequence_center, frequence_min, frequence_max, Frequence_Tl, gGAMMAT):
    c_1.cd()
    gPad.SetBottomMargin(0.08)
    h.Draw()
    h.GetXaxis().SetRangeUser(
        input_params.dict['RefRangeMin1'], input_params.dict['RefRangeMax1'])
    hSRF.Draw('same')
    hSRF.SetLineColor(3)
    c_1.Update()
      
    c_2.cd()
    gPad.SetBottomMargin(0.01)
    for nnn in range(0,h.GetXaxis().GetNbins()):
      x_ref = (h.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
      y = h.GetBinContent(nnn)
      nx_ref = h_ref.GetXaxis().FindBin(x_ref)
      h_ref.SetBinContent(nx_ref, y)

    h_ref.Draw()
    h_ref.Scale(1e-8)
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
    hSRRF.GetXaxis().SetTitle('Relative Revolution Frequency')
    #hSRRF.GetXaxis().CenterTitle(true)
    hSRRF.GetXaxis().SetLabelFont(42)
    hSRRF.GetXaxis().SetLabelSize(0.10)
    hSRRF.GetXaxis().SetTitleSize(0.10)
    hSRRF.GetXaxis().SetTitleFont(42)
    hSRRF.GetYaxis().SetTitle('arb. units')
    #hSRRF.GetYaxis().CenterTitle(true)
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
  def print_out_or_not(params_file,input_params,c,h,h_ref,hSRRF,hSRF,Frequence_Rel,
                       Frequence_Tl,Harmonic):
    gSystem.ProcessEvents()
    gSystem.Sleep(10)
    print('Frequence_Rel = ', Frequence_Rel)
    print('Harmonic = ',Harmonic)
    print('Frequence_Rel*(Harmonic) = ',Frequence_Rel*(Harmonic))
    print('Frequence_Tl  = ',Frequence_Tl)
    print('exit or not? introduce exit')
    Flag=input('Enter exit to finish Brho manual adjustment:')
    if Flag=='exit':
      fout_root = TFile.Open('simtof_'+str(int(Harmonic))+'.tof','recreate')
      h.Write()
      h_ref.Write()
      hSRRF.Write()
      hSRF.Write()
      fout_root.Close()
      c.Print('result.pdf')
    else: input_params=InputParams(params_file) #reads input again after modification
    
# ================== execution =====================
def main():
  filename='data/410-j'
  frequence_center=0
  Frequence_Tl=243.2712156
  ring=Ring('ESR', 108.5)
  
  # 1. Import ame 
  ame = AMEData()
  ame.init_ame_db
  ame_data = ame.ame_table
  # 2. Importing in put params
  params_file = 'data/InputParameters.txt' #initial seeds; although can be changed to just declaring variables here
  input_params=InputParams(params_file)
  # 3. Load LISE file
  lise_file = LISEreader(input_params.lisefile)
  lise_data = lise_file.get_info_all()
  
  with open(filename) as f:
    files = f.readlines()
    for file in files:      
      # canvas:
      mycanvas=CanvasFormat()
      tex=mycanvas.set_latex_format()
      #tex.Draw()
      tex200Au79, tex200Hg79 = mycanvas.set_latex_labels()
      #draw these guys tex200Au79, tex200Hg7
      
      # gstyle:
      gStyle.SetOptStat(0)
      gStyle.SetOptTitle(0)
      gGAMMAT = mycanvas.gammat_calculator()
      #gGAMMAT.Draw()    

      r3, c0, c, c_1, c_2, c_2_1, c_2_2, c_3, c_4 = mycanvas.setup_tpad()
      nbins, frequence_min, frequence_max, y_max, h = SimTOF.fft_root(file[:-1])
      h_ref, hSRF, hSRRF=SimTOF.root_histo(nbins, frequence_center,frequence_min,
              frequence_max, Frequence_Tl)
      #print(h_ref,  hSRF, hSRRF)
      #h_ref.Draw('axis')
      #h.Draw()
      #input('stop')
      gCharge, gZ, gA, gmoq, gi, gSim=SimTOF.root_graph()
      
      Flag = ''
      while Flag != 'exit':
        m,moq,SRRF,SRF,Nx_SRF,Nx_SRRF=([] for i in range(6))      
        SimTOF.remove_point(gZ, gA, gCharge, gmoq, gi)
        
        # opening file to append:
        fout = open('output_'+str(input_params.dict['Harmonic'])+'.tof', 'a')
    
        for i, lise in enumerate(lise_data):
          for ame in ame_data:
            if lise[0]==ame[6] and lise[1]==ame[5]:
              particle_name = Particle(lise[2],lise[3],AMEData(),ring)
              
              m.append(AMEData.to_mev(particle_name.get_ionic_mass_in_u()))
              moq.append(particle_name.get_ionic_moq_in_u())
              # print('m y moq',m,'  ',moq)
              
<<<<<<< HEAD
              #gZ   .SetPoint(k, moq[k], lise[2])
              #gA   .SetPoint(k, moq[k], lise[1])
              #gCharge.SetPoint(k, moq[k], lise[4])
              #gmoq .SetPoint(k, moq[k], moq[k])
              #gi   .SetPoint(k, moq[k], lise[5])
              # print('gi=',gi,'gZ=',gZ)
              # gZ.Draw()
              
              print(i)
=======
              gZ   .SetPoint(k, moq[k], lise[2])
              gA   .SetPoint(k, moq[k], lise[1])
              gCharge.SetPoint(k, moq[k], lise[4])
              gmoq .SetPoint(k, moq[k], moq[k])
              gi   .SetPoint(k, moq[k], lise[5])

              #print(i)
>>>>>>> 249936a06a2f27da5d7755c78acd52d224c284a1
              if (str(lise[1])+lise[0] == input_params.dict['ReferenceIsotope']
                  and lise[4] == input_params.dict['ReferenceIsotopeCharge']):
                moq_Rel = moq[i]
                gamma = sqrt(pow(input_params.dict['Brho']*lise[4]*AMEData.CC/m[i], 2)+1)
                beta = sqrt(gamma * gamma - 1)/gamma
                velocity = AMEData.CC * beta
                #print(velocity,beta,gamma,moq_Rel)
                Frequence_Rel = velocity/ ring.circumference
                
        for k in range(0,len(moq)):
          # 1. simulated relative revolution frequency
          SRRF.append(1-1/input_params.dict['GAMMAT'] /
                          input_params.dict['GAMMAT']*(moq[k]-moq_Rel)/moq_Rel)
         
          # 2. simulated revolution frequency
          SRF.append(SRRF[k]*Frequence_Rel *
                         (input_params.dict['Harmonic']))
          Nx_SRF.append(hSRF.GetXaxis().FindBin(SRF[k]))
          hSRF.SetBinContent(Nx_SRF[k], lise[5]*y_max*0.01)
          # 3.hSRRF
          #print(SRF)
          SRRF.append(SRF[k]/(Frequence_Rel*(input_params.dict['Harmonic'])))
                
          Nx_SRRF.append(hSRRF.GetXaxis().FindBin(SRRF[k]))
          hSRRF.SetBinContent(Nx_SRRF[k], 1)
          #fout                                                                         
          fout.write(str(lise[0])+'\t'+str(lise[2])+'\t'+str(lise[1])+'\t'
                         +str(lise[4])+'\t'+str(input_params.dict['Harmonic'])
                         +'\t'+str(moq[k])+' u/e,\t f/f0 = '+str(SRRF[k])+'\t'
                         +str(SRF[k])+ 'MHz \t'+str(lise[5]))
        fout.close()
        
        gZ, gA, gCharge, gmoq, gi=SimTOF.root_sort(gZ, gA, gCharge, gmoq, gi)
        
        # SimTOF.make_graphs(c_1,c_2,c_2_1,c_2_2,c_3,c_4,h,h_ref,hSRF,hSRRF,input_params,
        #                    frequence_center,frequence_min,frequence_max,Frequence_Tl,gGAMMAT)
        #making graphs:
        c_1.cd()
        gPad.SetBottomMargin(0.08)
        h.Draw()
        #gPad.Modified()
        #gPad.Update()
        h.GetXaxis().SetRangeUser(
            input_params.dict['RefRangeMin1'], input_params.dict['RefRangeMax1'])
        hSRF.Draw()
        input('stop')
        gPad.Modified()
        gPad.Update()
        hSRF.SetLineColor(3)
        c_1.Update()
        c_1.cd(0)
        #c_1.SaveAs('worksornot.png')
         
        c_2.cd()
        #gPad.SetBottomMargin(0.01)
        for nnn in range(0,h.GetXaxis().GetNbins()):
          x_ref = (h.GetXaxis().GetBinCenter(nnn)+frequence_center)/Frequence_Tl
          y = h.GetBinContent(nnn)
          nx_ref = h_ref.GetXaxis().FindBin(x_ref)
          h_ref.SetBinContent(nx_ref, y)

        h_ref.Draw('same')
        #gPad.Modified()
        #gPad.Update()
        h_ref.Scale(1e-8)
        h_ref.GetYaxis().SetRangeUser(1, 1e3)
        h_ref.GetXaxis().SetRangeUser(
            input_params.dict['RefRangeMin2'], input_params.dict['RefRangeMax2'])
        hSRRF.Draw('same')
        #gPad.Modified()
        #gPad.Update()

        #c_2_1.cd()
        h_ref_small1 = h_ref.Clone('h_ref_small1')
        h_ref_small1.Draw()
        #gPad.Modified()
        #gPad.Update()
        h_ref_small1.GetXaxis().SetRangeUser(1.0010, 1.0032)
        hSRRF.Draw('same')
        #gPad.Modified()
        #gPad.Update()
        
        #c_2_2.cd()
        h_ref_small2 = h_ref.Clone('h_ref_small2')
        h_ref_small2.Draw()
        #gPad.Modified()
        #gPad.Update()
        h_ref_small2.GetXaxis().SetRangeUser(0.99994, 1.00004)
        hSRRF.Draw('same')
        #gPad.Modified()
        #gPad.Update()
      
        #c_3.cd()
        gPad.SetTopMargin(0.01)
        gPad.SetTickx(1)
        hSRRF.Draw('')
        #gPad.Modified()
        #gPad.Update()
        hSRRF.SetLineColor(2)
        hSRRF.GetXaxis().SetTitle('Relative Revolution Frequency')
        #hSRRF.GetXaxis().CenterTitle(true)
        hSRRF.GetXaxis().SetLabelFont(42)
        hSRRF.GetXaxis().SetLabelSize(0.10)
        hSRRF.GetXaxis().SetTitleSize(0.10)
        hSRRF.GetXaxis().SetTitleFont(42)
        hSRRF.GetYaxis().SetTitle('arb. units')
        #hSRRF.GetYaxis().CenterTitle(true)
        hSRRF.GetYaxis().SetLabelFont(42)
        hSRRF.GetYaxis().SetLabelSize(0.10)
        hSRRF.GetYaxis().SetTitleSize(0.10)
        hSRRF.GetYaxis().SetTitleFont(42)
        hSRRF.GetYaxis().SetTitleOffset(0.5)
        hSRRF.GetYaxis().SetNdivisions(505)
        hSRRF.GetXaxis().SetRangeUser(
            input_params.dict['RefRangeMin2'], input_params.dict['RefRangeMax2'])
        hSRRF.Scale(100)
        #c_3.Update()
          
        #c_4.cd()
        gGAMMAT.Draw('al')
        #gPad.Modified()
        #gPad.Update()
        gGAMMAT.GetXaxis().SetLimits((frequence_center+frequence_min)/Frequence_Tl,
                                    (frequence_center+frequence_max)/Frequence_Tl)
        gGAMMAT.GetYaxis().SetRangeUser(2.412, 2.432)
        #c_4.Update()
          
        hSRF.Draw('same')
        #gPad.Modified()
        #gPad.Update()
        #      
        # SimTOF.print_out_or_not(params_file,input_params,c,h,h_ref,hSRRF,hSRF,Frequence_Rel,
        #                         Frequence_Tl,input_params.dict['Harmonic'])
        gSystem.ProcessEvents()
        gSystem.Sleep(10)
        print('Frequence_Rel = ', Frequence_Rel)
        print('Harmonic = ',input_params.dict['Harmonic'])
        print('Frequence_Rel*(Harmonic) = ',Frequence_Rel*(input_params.dict['Harmonic']))
        print('Frequence_Tl  = ',Frequence_Tl)
        print('exit or not? introduce exit')
        Flag=input('Enter exit to finish Brho manual adjustment:')
        if Flag=='exit':
          fout_root = TFile.Open(f'simtof_{input_params.dict["Harmonic"]}.tof','recreate')
          h.Write()
          h_ref.Write()
          hSRRF.Write()
          hSRF.Write()
          fout_root.Close()
          c.Print('result.pdf')
        else: input_params=InputParams(params_file) #reads input again after modification
      
#this tests when program is run  
if __name__ == '__main__':
  try:
    main()
  except:
    raise
