from ROOT import TCanvas,TMath,TH1,TH1F,TF1,TRandom,TSpectrum,TVirtualFitter 
from array import array
from time import time

def gaussians(x,par): #necessary to define it this way for making TF1.Fit() works
    #--------------------horrible------------------------#
    i=0
    aux=1
    while aux>1e-6 and aux<1e10: #this part is awful but it works
        aux=abs(par[i])
        i=i+1
    npeakstofit=int((i-1-2)/3) #whatever it takes phylosophy
    #--------------------------------------------------#
    result = par[0] + par[1]*x[0] #line
    for p in range(0,npeakstofit):#for each peak 3 parameters
        norm  = par[3*p+2] 
        mean  = par[3*p+3]
        sigma = par[3*p+4]
        norm /= sigma*(TMath.Sqrt(TMath.TwoPi()))
        result += norm*TMath.Gaus(x[0],mean,sigma)
    return result

def decay_curve(x,par):
    return p[0]+p[1]*TMath.Exp(-x[0]/p[2])
    
class FitPeaks():

    def __init__(self,npeaks,histogram,tofit):
        self.par = array('d',[]) #has to be this way for ROOT Fit() to work
        self.npeaks=npeaks
        self.tofit=tofit #boolean to make fitting or not (if not, does peak finding etc)
        self.histogram=histogram
        self.h2=histogram
        self.peaks()
        
    #def __call__(self): #This method can be very useful.
        #self.peaks()
        #self.fitting()
        
    def set_canvas(self):#Generates canvas, 1 with found peaks, 1 with fitting
        self.c1 = TCanvas('c1','c1',10,10,1000,900)
        self.c1.Divide(1,2)
              
    def peaks(self):
        self.set_canvas()
        self.c1.cd(1)
        self.histogram.Draw()
        self.c1.Update()
        
        self.peak_finding() #PeakFinding finds peaks (surprise)
        
        self.set_ranges()
        
        self.c1.cd(2)
        self.background()
        self.c1.Update()
        
        if self.tofit:#if it is True
            self.n_peakstofit()
            self.gaussians_fitting()
            
    def peak_finding(self):
        # Use TSpectrum to find the peak candidates
        self.s = TSpectrum(self.npeaks) #(maximum number of peaks)
        self.nfound = self.s.Search(self.histogram,2,"",0.10)
        self.xpeaks=self.s.GetPositionX()
        print(f'Found {self.nfound} candidate peaks to fit at positions:\n')
        for xpeak in self.xpeaks:
            print(f'at positions {xpeak}')
        
    def background(self):
        # Estimate background using TSpectrum.Background
        hb = self.s.Background(self.histogram,20,"same") #This function calculates the background spectrum in the input histogram, returned as a histogram.  
        # estimate linear background using a fitting method, predefined ROOT pol1
        self.fline = TF1('fline','pol1',self.range_min,self.range_max) 
        self.histogram.Fit('fline','qn')
        
    def n_peakstofit(self):# Loop on all found peaks. Eliminate peaks at the background level    
        n_peakstofit=0
        self.par.append(self.fline.GetParameter(0)) #par[0] 
        self.par.append(self.fline.GetParameter(1)) #par[1]
        for xpeak in (self.xpeaks):
            bin=self.histogram.GetXaxis().FindBin(xpeak) 
            ypeak=self.histogram.GetBinContent(bin)
            if (abs(yp-TMath.Sqrt(ypeak)) > self.fline.Eval(xpeak)):#compares if peak is over the background or not
                self.par.append(ypeak)  #"height"
                self.par.append(xpeak)  #"mean"
                self.par.append(100) #"sigma" initial estimation
                n_peakstofit+=1
        print(f'Found {n_peakstofit} useful peaks to fit\n')
        
    def gaussians_fitting(self):
        print(f'Now fitting: it takes some time \n')
        for i in range (0,10):#loop for making the thing to converge
            start_time = time()
            npars=int(len(self.par))
            fit=TF1('fit',gaussians,self.range_min,self.range_max,npars)
            TVirtualFitter.Fitter(self.h2,npars)
            fit.SetParameters(self.par)
            fit.SetNpx(1000)
            self.h2.Fit(fit)
            self.c1.Update()
            getpar = self.h2.GetFunction('fit')
            for j in range(getpar.GetNumberFreeParameters()):
                self.par[j] = getpar.GetParameter(j)
            #print(self.par)
            print(f"it took {time()-start_time} seconds, not that bad")

    def set_ranges(self):
        self.range_min = self.histogram.GetXaxis().GetXmin()
        self.range_max = self.histogram.GetXaxis().GetXmax()
        
    def decay_fit(self,histogram):#histogram with the interesting data
        par=array('d',[4.5,0.05,20])#initial seeds
        range_min=histogram.GetXaxis().GetXmin()
        range_max=histogram.GetXaxis().GetXmax()
        decay_fit=TF1('decay_fit',decay_curve,range_min,range_max,len(par))
        TVirtualFitter.Fitter(histogram,len(par))
        fit.SetParameters(par)
        fit.SetNpx(1000)
        histogram.Fit(decay_fit)
        getpar = histogram.GetFunction('decay_fit')
        for j in range(getpar.GetNumberFreeParameters()):
            par[j] = getpar.GetParameter(j)
        #return par? just plot?

      
if __name__ == '__main__':
  try:  
    pass
  except:
    raise
