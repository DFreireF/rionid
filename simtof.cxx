#include <iostream>
#include <sstream>
#include <stdlib.h>
#include <TImage.h>
using namespace std;
void SetPadFormat(TPad *c_1)
{
  c_1->SetLeftMargin(0.10);
  c_1->SetRightMargin(0.05);
  c_1->SetTopMargin(0.12);
  c_1->SetBottomMargin(0.25);
  c_1->SetFrameBorderMode(0);
  c_1->SetLogy(1);
  c_1->Draw();
}
void SetCanvasFormat(TCanvas *c)
{
  c->SetFillColor(0);
  c->SetBorderMode(0);
  c->SetBorderSize(2);
  c->SetFrameBorderMode(0);
}
void SetLatexFormat(TLatex *tex)
{
  tex->SetTextColor(2);
  tex->SetTextAngle(90);
  tex->SetLineWidth(2);
  tex->Draw();
}
TGraph *GAMMATCalculator()
{
  TGraph *gGAMMAT = new  TGraph();
  double k = -0.5;
  gGAMMAT->SetName("gGAMMAT");
  gGAMMAT->SetPoint(0,0.998,2.4234 + (0.98 - 1)*k);
  gGAMMAT->SetPoint(1,1.000,2.4234 + (1.000 - 1)*k);
  gGAMMAT->SetPoint(2,1.002,2.4234 + (1.02 - 1)*k);
  return gGAMMAT;
}
void simtof()
{
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  TGraph *gGAMMAT = GAMMATCalculator();
  gGAMMAT -> Print();
  TFile *fdata = new TFile("0000013.iq.tdms.root");
  TH1D *hFFT_px;
  fdata->GetObject("FFT_Average",hFFT_px);
  Int_t nbins  = hFFT_px->GetXaxis()->GetNbins();
  double frequence_min    = hFFT_px->GetXaxis()->GetXmin();
  double frequence_max    = hFFT_px->GetXaxis()->GetXmax();
  double y_max = hFFT_px->GetMaximum();
  cout <<"nbins = "<<nbins<<endl;
  cout <<"frequence_min = "<<frequence_min<<endl;
  cout <<"frequence_max = "<<frequence_max<<endl;
  frequence_min = 245 + frequence_min/1000;
  frequence_max = 245 + frequence_max/1000;
  hFFT_px->GetXaxis()->SetLimits(frequence_min ,  frequence_max);
  double Frequence_Tl     = 243.2712156;
  double frequence_center = 0;
  double OrbitalLength    = 108430;
  string NUCNAM[6000], ET[6000],LISEFileName,PRONAM[6000],T1,lineBuffer,PPSString[6000],ChargeString[6000],PPSString1[6000],Flag;
  int  Z[6000],  A[6000];
  double MassExcess[6000],ERR[6000],moqDB[6000];
  int ChargeDB[6000];
  double PPS[6000], P[30001],ReferenceIsotopeCharge;
  double m,me,amu,BindingEnergy;
  double Clight,E,U,GAMMAT,CSREL,EMASS,UK,ACCP,Brho,gamma,beta,velocity,RevolutionTime_Rel,Frequence_Rel, m_Rel,moq,moq_Rel,Z_Rel,dpop,dToTSystem,RefRangeMin1,RefRangeMax1,RefRangeMin2,RefRangeMax2,RefRangeMin3,RefRangeMax3,ScaleFactor;
  int NA = 0,lines= 0,StartLine,StopLine,NProductions,Harmonic;
  bool FlagRead = false;
  char PPStmp[20];
  string ReferenceIsotope;
  ifstream fAME03,fLISE,fBindingEnergy;
  LISEFileName = "E143_TEline-ESR-72Ge.lpp";
  fAME03.open("mass.rd");
  Clight= 299.7924580;
  me    = 0.5109989;
  amu   = 931.494061;
  //1. Load AME data base.
  for(int i=0;i<3537;i++)
    {
      fAME03>>NUCNAM[i]>>Z[i]>>A[i]>>MassExcess[i]>>ERR[i]>>ET[i];
      NA++;
    }
  fAME03.close();
  // 2. Load binding energy file.
  fBindingEnergy.open("ElBiEn_2007.dat");
  double BindingEnergyDB[101][100];
  lines = 0;
  if (!fBindingEnergy) 
    {
      cout << "Input Path file : ElBiEn_2007.dat not found " << endl;
      return;
    }
  else
    {
      cout << "Reading from : ElBiEn_2007.dat" << endl;
      while (!fBindingEnergy.eof())
        {
	  getline(fBindingEnergy, lineBuffer);
        	
	  if(lineBuffer.find("# Z  TotBEn 1e-ion")!=string::npos)
	    {
	      FlagRead = true;
	      StartLine = lines+1;
	    }
	  lines++;
        }
    }		
  StopLine = StartLine+100;
  fBindingEnergy.clear();
  fBindingEnergy.close();
  fBindingEnergy.open("ElBiEn_2007.dat");
  lines = 0;
  for(int i=0;i<StopLine;i++)
    {
      getline(fBindingEnergy, lineBuffer);
      if(i<StartLine)
	{
	  continue;
	}
      else
	{
	  istringstream lineBufferStream;
	  lineBufferStream.str(lineBuffer);
	  double zzz, aaa[102];
	  for(int j=0;j<102;j++)
	    lineBufferStream>>aaa[j];
	  zzz = aaa[0];
	  for(int j=0;j<100;j++)
	    {
	      BindingEnergyDB[int(zzz)][j] = aaa[2+j];
	    }
	  lines++; 
	}
    }
  // 3. Load LISE file
  lines = 0;
  fLISE.open(LISEFileName.c_str());
  char lineBufferchar[1000];
  if (!fLISE) 
    {
      cout << "Input Path file :" << LISEFileName << " not found " << endl;
      return;
    }
  else
    {
      cout << "Reading from :" <<LISEFileName << endl;
      while (!fLISE.eof())
        {
	  getline(fLISE, lineBuffer);
	  if(lineBuffer.find("[Calculations]")!=string::npos)
	    {
	      FlagRead = true;
	      StartLine = lines+1;
	    }
	  lines++;
        }
    }	
  StopLine = lines-2;
  fLISE.clear();
  fLISE.close();
  fLISE.open(LISEFileName.c_str());
  lines = 0;
  string NUCNAM_output[6000];
  cout<<"reading LISE file:"<<endl;
  for(int i=0;i<StopLine;i++)
    {
      getline(fLISE, lineBuffer);
      cout<<lineBuffer<<endl;
      if(i<StartLine)
	{
	  continue;
	}
      else
	{
	  istringstream lineBufferStream;
	  lineBufferStream.str(lineBuffer);
	  lineBufferStream>>PRONAM[lines]>>T1>>T1>>T1>>T1>>T1>>ChargeString[lines]>>PPSString[lines];
		  			
	  PPSString[lines].erase(0,1);
	  PPSString[lines].erase(10,PPSString[lines].length());
	  PPS[lines] = atof(PPSString[lines].c_str());
		  			
	  ChargeString[lines].erase(ChargeString[lines].length()-1,1);
	  ChargeDB[lines] = atoi(ChargeString[lines].c_str());
	  lines++;
	}
    }
  NProductions = lines;
  cout<<"Read LISE ok."<<endl;
  fLISE.close();
  TH1F *hSim   = new TH1F("hSim","hSim",200e3,400,700);
  TGraph *gZ   = new TGraph();
  TGraph *gA   = new TGraph();
  TGraph *gCharge= new TGraph();
  TGraph *gmoq = new TGraph();
  TGraph *gi   = new TGraph();
  TGraph *gSim = new TGraph();
  gSim->SetLineColor(2);
  gSim->SetName("gSim");

  TH1F *hFFT_px_ref = new TH1F("hFFT_px_ref","hFFT_px_ref",                nbins,(frequence_center+frequence_min)/Frequence_Tl,(frequence_center+frequence_max)/Frequence_Tl);
  TH1F *hSRF  = new TH1F("hSRF", "simulated revolution frequence",         nbins,(frequence_center+frequence_min),             (frequence_center+frequence_max));
  TH1F *hSRRF = new TH1F("hSRRF","simulated relative revolution frequence",nbins,(frequence_center+frequence_min)/Frequence_Tl,(frequence_center+frequence_max)/Frequence_Tl);
  hSRF->SetLineStyle(2);
  hSRRF->SetLineStyle(2);

  TRandom3 *r3 = new TRandom3();
  TCanvas *c0 = new TCanvas("c0", "c0",0,0,1000,300);
  SetCanvasFormat(c0);
  TCanvas *c = new TCanvas("c", "c",0,0,1000,880);
  SetCanvasFormat(c);
  c->cd();
  TPad *c_1 = new TPad("c_1", "c_1",0.00,0.75,0.99,0.99);
  SetPadFormat(c_1);
  c->cd();
  TPad *c_2 = new TPad("c_2", "c_2",0.0,0.50,0.99,0.75);
  SetPadFormat(c_2);
  c->cd();
  TPad *c_2_1 = new TPad("c_2_1", "c_2_1",0.70,0.6,0.86,0.7189711);
  SetPadFormat(c_2_1);
  c_2_1->SetLeftMargin(0.02857143);
  c_2_1->SetRightMargin(0.02857143);
  c_2_1->SetTopMargin(0.01851852);
  c_2_1->SetBottomMargin(0.01851852);
  TPad *c_2_2 = new TPad("c_2_2", "c_2_2",0.45,0.6,0.61,0.7189711);
  SetPadFormat(c_2_2);  c_2_2->SetLeftMargin(0.02857143);
  c_2_2->SetRightMargin(0.02857143);
  c_2_2->SetTopMargin(0.01851852);
  c_2_2->SetBottomMargin(0.01851852);
  c->cd();
  TPad *c_3 = new TPad("c_3", "c_3",0.0,0.25,0.99,0.50);
  SetPadFormat(c_3);
  c->cd();
  TPad *c_4 = new TPad("c_4", "c_4",0.0,0.0,0.99,0.25);
  SetPadFormat(c_4);
  c_4->SetLogy(0);
  while(Flag!="exit")
    { 
      hSim->Reset();
      hSRF->Reset();
      hSRRF->Reset();
      ifstream fInputParameters;
      fInputParameters.open("InputParameters");
      fInputParameters>>lineBuffer>>Brho;
      fInputParameters>>lineBuffer>>GAMMAT;
      fInputParameters>>lineBuffer>>dpop;
      fInputParameters>>lineBuffer>>dToTSystem;
      fInputParameters>>lineBuffer>>RefRangeMin1;
      fInputParameters>>lineBuffer>>RefRangeMax1;
      fInputParameters>>lineBuffer>>RefRangeMin2;
      fInputParameters>>lineBuffer>>RefRangeMax2;
      fInputParameters>>lineBuffer>>RefRangeMin3;
      fInputParameters>>lineBuffer>>RefRangeMax3;
      fInputParameters>>lineBuffer>>ScaleFactor;
      fInputParameters>>lineBuffer>>ReferenceIsotope;
      fInputParameters>>lineBuffer>>ReferenceIsotopeCharge;
      fInputParameters>>lineBuffer>>Harmonic;		
      fInputParameters.close();
      cout<<"Brho = "<<Brho<<" ; GAMMAT = "<<GAMMAT<<" ;dpop = "<<dpop<<" ;dToTSystem= "<<dToTSystem<<" ;ReferenceIsotope= "<<ReferenceIsotope<<" ;Harmonic= "<<Harmonic<<endl;
      int k = gZ->GetN();
      for(int i=0;i<k;i++)
	{
	  gZ->RemovePoint(0);
	  gA->RemovePoint(0);
	  gCharge->RemovePoint(0);
	  gmoq->RemovePoint(0);
	  gi->RemovePoint(0);
	}
      k=0;
      for(int i=0;i<NA;i++)
	{
	  for(int j=0;j<NProductions;j++)
	    {
	      if(NUCNAM[i] == PRONAM[j])
		{
		  m                 = A[i]*amu + MassExcess[i]/1e3 - Z[i]*me + BindingEnergyDB[Z[i]  ][ChargeDB[j]-1]/1e6;   // MeV 
		  moq               = m/ChargeDB[j]/amu;
		  gZ   ->SetPoint(k,moq,Z[i]);
		  gA   ->SetPoint(k,moq,A[i]);
		  gCharge   ->SetPoint(k,moq,ChargeDB[j]);
		  gmoq ->SetPoint(k,moq,moq);
		  gi   ->SetPoint(k,moq,j);
		  if(NUCNAM[i] == ReferenceIsotope&&ChargeDB[j]==ReferenceIsotopeCharge)
		    {
		      moq_Rel           = moq;
		      gamma             = sqrt(pow(Brho*ChargeDB[j]*Clight/m,2)+1);
		      beta              = sqrt(gamma*gamma -1)/gamma;
		      velocity          = Clight * beta;
		      Frequence_Rel     = 1000/(OrbitalLength/velocity);
		    }
		  k++;
		}
	    }	
	}
      gZ->Sort();
      gA->Sort();
      gCharge->Sort();
      gmoq->Sort();
      gi->Sort();
      char tmp[100];
      sprintf(tmp,"output_%d.tof",Harmonic);
      ofstream fout(tmp);
      std::cout.precision(10);
      
      double index,ZZZ,AAA,Charge,moq,SRRF,SRF;
      int kkk=0;
      for(int i=0;i<gZ->GetN();i++)
	{
	  gZ     ->GetPoint(i,moqDB[i],ZZZ);	
	  gA     ->GetPoint(i,moqDB[i],AAA);	
	  gCharge->GetPoint(i,moqDB[i],Charge);	
	  gmoq   ->GetPoint(i,moqDB[i],moq);	
	  gi     ->GetPoint(i,moqDB[i],index);
	  // 1. simulated relative revolution frequence
	  SRRF   = 1-1/GAMMAT/GAMMAT*(moqDB[i]-moq_Rel)/moq_Rel;
	  //GAMMAT = gGAMMAT->Eval(SRRF);
	  //SRRF   = 1-1/GAMMAT/GAMMAT*(moqDB[i]-moq_Rel)/moq_Rel;
	  // 2. simulated revolution frequence
	  SRF= SRRF*Frequence_Rel*(Harmonic);
	  int Nx_SRF = hSRF->GetXaxis()->FindBin(SRF);
	  //hSRF->SetBinContent(Nx_SRF,1e13);
	  hSRF->SetBinContent(Nx_SRF,PPS[int(index)]*y_max*0.01);
	  // 3.
	  SRRF = SRF/(Frequence_Rel*(Harmonic));
	  int Nx_SRRF = hSRRF->GetXaxis()->FindBin(SRRF);
	  hSRRF->SetBinContent(Nx_SRRF,1);
		
	  fout<<std::fixed<<PRONAM[int(index)]<<"\t"<<int(ZZZ)<<"\t"<<int(AAA)<<"\t"<<int(Charge)<<"\t"<<setw(2)<<int(Harmonic)<<"\t"<<setw(2)<<setw(5)<<moqDB[i]<<" ue,\t f/f0 = "<<setw(5)<<SRRF<<" \t"<<setw(5)<<SRF<<" MHz,\t"<<setw(10)<<PPS[int(index)]<<endl;
	  cout<<std::fixed<<PRONAM[int(index)]<<"\t"<<int(ZZZ)<<"\t"<<int(AAA)<<"\t"<<int(Charge)<<"\t"<<setw(2)<<int(Harmonic)<<"\t"<<setw(2)<<setw(5)<<moqDB[i]<<" ue,\t f/f0 = "<<setw(5)<<SRRF<<" \t"<<setw(5)<<SRF<<" MHz,\t"<<setw(10)<<PPS[int(index)]<<endl;
	}
      fout.close();
     
      c_1->cd();
      gPad->SetBottomMargin(0.08);
      hFFT_px->Draw();
      hFFT_px->GetXaxis()->SetRangeUser(RefRangeMin1,RefRangeMax1);
      hSRF->Draw("same");
      hSRF->SetLineColor(3);
      c_1->Update();
			
      c_2->cd();
      gPad->SetBottomMargin(0.01);
      for(int nnn=0;nnn<hFFT_px->GetXaxis()->GetNbins();nnn++)
	{
	  double x_ref = (hFFT_px->GetXaxis()->GetBinCenter(nnn)+frequence_center)/Frequence_Tl;
	  double y     = hFFT_px->GetBinContent(nnn);
	  Int_t nx_ref = hFFT_px_ref-> GetXaxis()->FindBin(x_ref);
	  hFFT_px_ref->SetBinContent(nx_ref,y);
	}
      hFFT_px_ref->Draw();
      hFFT_px_ref->Scale(0.00000001);
      hFFT_px_ref->GetYaxis()->SetRangeUser(1,1e3);
      hFFT_px_ref->GetXaxis()->SetRangeUser(RefRangeMin2,RefRangeMax2);
      hSRRF->Draw("same");

      c_2_1->cd();
      TH1F *hFFT_px_ref_small1  = (TH1F *)hFFT_px_ref->Clone("hFFT_px_ref_small1");
      hFFT_px_ref_small1->Draw();
      hFFT_px_ref_small1->GetXaxis()->SetRangeUser(1.0010,1.0032);
      hSRRF->Draw("same");
      
      c_2_2->cd();      
      TH1F *hFFT_px_ref_small2  = (TH1F *)hFFT_px_ref->Clone("hFFT_px_ref_small2");
      hFFT_px_ref_small2->Draw();
      hFFT_px_ref_small2->GetXaxis()->SetRangeUser(0.99994,1.00004);
      hSRRF->Draw("same");
      
      TLatex *   tex200Au79 = new TLatex(0.9999552,2.176887e+14,"^{200}Au^{79+}");
      tex200Au79->SetTextColor(2);
      tex200Au79->SetTextSize(0.08);
      tex200Au79->SetTextAngle(88.21009);
      tex200Au79->SetLineWidth(2);
      tex200Au79->Draw();
      
      TLatex *   tex200Hg79 = new TLatex(0.999965,2.176887e+13,"^{200}Au^{79+}");
      tex200Hg79->SetTextColor(2);
      tex200Hg79->SetTextSize(0.08);
      tex200Hg79->SetTextAngle(88.21009);
      tex200Hg79->SetLineWidth(2);
      tex200Hg79->Draw();

      c_3->cd();
      gPad->SetTopMargin(0.01);
      gPad->SetTickx(1);
      hSRRF->Draw("");
      hSRRF->SetLineColor(2);
      hSRRF->GetXaxis()->SetTitle("relative revolution frequence");
      hSRRF->GetXaxis()->CenterTitle(true);
      hSRRF->GetXaxis()->SetLabelFont(42);
      hSRRF->GetXaxis()->SetLabelSize(0.10);
      hSRRF->GetXaxis()->SetTitleSize(0.10);
      hSRRF->GetXaxis()->SetTitleFont(42);
      hSRRF->GetYaxis()->SetTitle("arb. units");
      hSRRF->GetYaxis()->CenterTitle(true);
      hSRRF->GetYaxis()->SetLabelFont(42);
      hSRRF->GetYaxis()->SetLabelSize(0.10);
      hSRRF->GetYaxis()->SetTitleSize(0.10);
      hSRRF->GetYaxis()->SetTitleFont(42);
      hSRRF->GetYaxis()->SetTitleOffset(0.5);	  	
      hSRRF->GetYaxis()->SetNdivisions(505);  
      hSRRF->GetXaxis()->SetRangeUser(RefRangeMin2,RefRangeMax2);
      hSRRF->Scale(100);
      c_3->Update();
			
      c_4->cd();
      gGAMMAT->Draw("al");
      gGAMMAT->GetXaxis()->SetLimits((frequence_center+frequence_min)/Frequence_Tl,(frequence_center+frequence_max)/Frequence_Tl);
      gGAMMAT->GetYaxis()->SetRangeUser(2.412,2.432);
      c_4->Update();
      //c->Update();
      
      gSystem->ProcessEvents();
      gSystem->Sleep(10);
      cout<<"Frequence_Rel = "<<Frequence_Rel<<endl;
      cout<<"Harmonic = "<<Harmonic<<endl;
      cout<<"Frequence_Rel*(Harmonic) = "<<Frequence_Rel*(Harmonic)<<endl;
      cout<<"Frequence_Tl  = "<<Frequence_Tl<<endl;
      cout<<"Nx_SRF = "<<Nx_SRF<<endl;
      cout<<"exit or not? [Exit,exit]"<<endl;
      cin>>Flag;
      cout<<Flag<<endl;

    }
  char tmp[100];
  sprintf(tmp,"simtof_%d.root",Harmonic);
  TFile *fout_root = new TFile(tmp,"recreate");
  hFFT_px->Write();
  hFFT_px_ref->Write();
  hSRRF->Write();
  hSRF->Write();
  fout_root->Close();
  c->Print("result.pdf");
}
