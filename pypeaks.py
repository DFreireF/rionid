from ROOT import TCanvas,TMath,TH1,TH1F,TF1,TRandom,TSpectrum,TVirtualFitter 
from array import array
from time import time

def fpeaks(x,par): #necessary to define it this way for making TF1.Fit() works
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

class FitPeaks():

    def __init__(self,npeaks,histogram):
        self.par = array('d',[]) #has to be this way for ROOT Fit() to work
        self.npeaks=npeaks
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
        # Use TSpectrum to find the peak candidates
        self.s = TSpectrum(self.npeaks) #(maximum number of peaks)
        self.nfound = self.s.Search(self.histogram,2,"",0.10)
        print(f'Found {self.nfound} candidate peaks to fit\n')
        
        if self.npeaks<0: #if you dont want any fitting, just the peaks found
            return None
        
        self.c1.cd(2)
        # Estimate background using TSpectrum.Background
        hb = self.s.Background(self.histogram,20,"same") #This function calculates the background spectrum in the input histogram, returned as a histogram.  
        self.set_ranges()
        # estimate linear background using a fitting method, predefined ROOT pol1
        self.fline = TF1('fline','pol1',self.range_min,self.range_max) 
        self.histogram.Fit('fline','qn')
        self.c1.Update()
        self.n_peakstofit()
        self.fitting()
        
    def n_peakstofit(self):# Loop on all found peaks. Eliminate peaks at the background level    
        n_peakstofit=0
        xpeaks=self.s.GetPositionX()
        self.par.append(self.fline.GetParameter(0)) #par[0] 
        self.par.append(self.fline.GetParameter(1)) #par[1]
        for p in range(0,self.nfound):
            xp=xpeaks[p]
            bin=self.histogram.GetXaxis().FindBin(xp) 
            yp=self.histogram.GetBinContent(bin)
            if (abs(yp-TMath.Sqrt(yp)) > self.fline.Eval(xp)):#compares if peak is over the background or not
                self.par.append(yp)  #"height"
                self.par.append(xp)  #"mean"
                self.par.append(100) #"sigma"
                n_peakstofit+=1
        print(f'Found {n_peakstofit} useful peaks to fit\n')
        
    def fitting(self):
        print(f'Now fitting: it takes some time \n')
        for i in range (0,10):#loop for making the thing to converge
            start_time = time()
            npars=int(len(self.par))
            fit=TF1('fit',fpeaks,self.range_min,self.range_max,npars)
            TVirtualFitter.Fitter(self.h2,10+npars-2)#*int(self.par[-1])
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

      
if __name__ == '__main__':
  try:  
    pass
  except:
    raise
