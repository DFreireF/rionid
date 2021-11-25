from ROOT import TCanvas,TMath,TH1,TH1F,TF1,TRandom,TSpectrum,TVirtualFitter 
#fitting function compose by various Gaussians; change by Voigt function maybe
from array import array
from time import time
import numpy as np

def fpeaks(x,par):
    result = par[0] + par[1]*x[0] #line
    npeakstofit=(np.len(par))
    print(npeakstofit,'?')
    for p in range(0,npeakstofit):#for each peak 3 parameters
        norm  = par[3*p+2] 
        mean  = par[3*p+3]
        sigma = par[3*p+4]
        norm /= sigma*(TMath.Sqrt(TMath.TwoPi()))
        result += norm*TMath.Gaus(x[0],mean,sigma)
        #print(sigma)
    return result

class FitPeaks():

    def __init__(self,npeaks,histogram):
        self.par = array('d',[])
        self.npeaks=npeaks
        self.histogram=histogram
        self.h2=histogram
        self.peaks()
    #def __call__(self):
        #self.peaks()
        #self.fitting()
        #self.c1.Update()
        
    def canvas(self):#Generates canvas, 1 with found peaks, 1 with fitting
        self.c1 = TCanvas('c1','c1',10,10,1000,900)
        self.c1.Divide(1,2)
        
    def generate_random_peaks(self):#Generate n peaks at random
        self.par.append(0.8)
        self.par.append(-0.6/1000)
        gRandom=TRandom()
        for p in range(0,self.npeaks):
           self.par.append(1) # "height"
           self.par.append(10+gRandom.Rndm()*980)#[3*p+3] // "mean"
           self.par.append(3+2*gRandom.Rndm()) #[3*p+4] // "sigma"
           
    def peaks(self):
        #self.generate_random_peaks()
        self.canvas()
        self.c1.cd(1)
        self.histogram.Draw()
        h2=self.histogram
        # Use TSpectrum to find the peak candidates
        self.s = TSpectrum(self.npeaks) #(maximum number of peaks)
        self.nfound = self.s.Search(self.histogram,2,"",0.10)
        print(f'Found {self.nfound} candidate peaks to fit\n')
        
        if self.npeaks<0: #if you dont want any fitting, just the peaks found
            return None
        
        # Estimate background using TSpectrum::Background
        hb = self.s.Background(self.histogram,20,"same") #This function calculates the background spectrum in the input histogram, returned as a histogram.
        if hb: #is there any other option than this? I mean, is it satisfied always?
            self.c1.Update()  
        # estimate linear background using a fitting method
        self.c1.cd(2)
        self.set_ranges()
        #print(self.range_min)
        self.fline = TF1('fline','pol1',self.range_min,self.range_max) #we will need to change the range 
        self.histogram.Fit('fline','qn')
        self.c1.Update()
        #self.par[0]=self.fline.GetParameter(0)
        #self.par[1]=self.fline.GetParameter(1)
        self.par.append(self.fline.GetParameter(0)) #par[0] 
        self.par.append(self.fline.GetParameter(1)) #par[1]
        self.n_peakstofit()
        start_time = time()
        print(f'Now fitting: it takes some time \n')
        #self.par=getpar.GetParameters()
        npars=int(len(self.par))
        #print(npars)
        for i in range (0,10):
            fit=TF1('fit',fpeaks,self.range_min,self.range_max,npars)
            TVirtualFitter.Fitter(h2,10+npars-2)#*int(self.par[-1])
            fit.SetParameters(self.par)
            fit.SetNpx(1000)
            h2.Fit(fit)
            self.c1.Update()
            getpar = self.h2.GetFunction('fit')
            for j in range(getpar.GetNumberFreeParameters()):
                self.par[j] = getpar.GetParameter(j)
            print(self.par)
            print(f"--{time()-start_time} seconds--")
        #self.fitting()
        
    def n_peakstofit(self):# Loop on all found peaks. Eliminate peaks at the background level    
        n_peakstofit=0
        xpeaks=self.s.GetPositionX()
        for p in range(0,self.nfound):
            print(p)
            xp=xpeaks[p]
            bin=self.histogram.GetXaxis().FindBin(xp) 
            yp=self.histogram.GetBinContent(bin)
            #print(f'es {yp-TMath.Sqrt(yp)} > {self.fline.Eval(xp)} ??')
            if (abs(yp-TMath.Sqrt(yp)) > self.fline.Eval(xp)):
                self.par.append(yp)  #[3*n_peakstofit+2]=yp// "height"
                self.par.append(xp)  #[3*n_peakstofit+3]=xp[3*npeaks+3]// "mean"
                self.par.append(10)   #[3*n_peakstofit+4]=3#[3*npeaks+4]// "sigma"
                n_peakstofit+=1
                
        #self.par.append(n_peakstofit)
        #print(self.par)
        print(f'Found {n_peakstofit} useful peaks to fit\n')
        
    def fitting(self):
        #start_time = time()
        #print(f'Now fitting: it takes some time \n')
        #self.set_ranges()
        #print(self.par[-1])
        #input()
        fit=TF1('fit',fpeaks,0,1000,2+3*int(self.par[-1]))
        
        #fit.Draw()
        #self.c1.Update()
        input()
        TVirtualFitter.Fitter(self.h2,10+3*int(self.par[-1]))
        
        fit.SetParameters(self.par)
        fit.SetNpx(1000)
        self.h2.Fit(fit)
        print(f"--{time()-start_time} seconds--")

    def set_ranges(self):
        self.range_min = self.histogram.GetXaxis().GetXmin()
        self.range_max = self.histogram.GetXaxis().GetXmax()

      
if __name__ == '__main__':
  try:  
    FitPeaks(10,histo)
  except:
    raise
