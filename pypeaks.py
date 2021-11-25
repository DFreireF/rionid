from ROOT import TCanvas,TMath,TH1,TH1F,TF1,TRandom,TSpectrum,TVirtualFitter 
#fitting function compose by various Gaussians; change by Voigt function maybe
from array import array

def fpeaks(x,par):
    result = par[0] + par[1]*x[0] #line
    for p in range(0,20): #for each peak 3 parameters
        norm  = par[3*p+2] 
        mean  = par[3*p+3]
        sigma = par[3*p+4]
        norm /= sigma*(TMath.Sqrt(TMath.TwoPi()))
        result += norm*TMath.Gaus(x[0],mean,sigma)
    return result
    
class FitPeaks():

    def __init__(self,npeaks,histogram):
        self.par = array('d',[])
        self.npeaks=npeaks
        self.histogram=histogram
        self.peaks()

    def peaks(self):
        #Generate n peaks at random
        self.par.append(0.8)
        self.par.append(-0.6/1000)
        h2=self.histogram
        gRandom=TRandom()
        for p in range(0,self.npeaks):
           self.par.append(1) # "height"
           self.par.append(10+gRandom.Rndm()*980)#[3*p+3] // "mean"
           self.par.append(3+2*gRandom.Rndm()) #[3*p+4] // "sigma"
        #1D function          
        c1 = TCanvas('c1','c1',10,10,1000,900)
        c1.Divide(1,2)
        c1.cd(1)
        self.histogram.Draw()
        # Use TSpectrum to find the peak candidates
        s = TSpectrum(2*self.npeaks) #(maximum number of peaks)
        nfound = s.Search(self.histogram,2,"",0.10)
        print(f'Found {nfound} candidate peaks to fit\n') 
        # Estimate background using TSpectrum::Background
        hb = s.Background(self.histogram,20,"same") #This function calculates the background spectrum in the input histogram, returned as a histogram.
        if hb: #is there any other option than this? I mean, is it satisfied always?
            c1.Update() 
        if self.npeaks<0: #if you dont want any fitting
            return 
        # estimate linear background using a fitting method
        c1.cd(2) 
        fline = TF1('fline','pol1',0,1000) #we will need to change the range 
        self.histogram.Fit('fline','qn') 
        # Loop on all found peaks. Eliminate peaks at the background level
        self.par[0]=fline.GetParameter(0) 
        self.par[1]=fline.GetParameter(1) 
        #self.npeaks=0  #makes sense? 
        xpeaks=s.GetPositionX() 
        for p in range(0,nfound):
              xp=xpeaks[p] 
              bin=self.histogram.GetXaxis().FindBin(xp) 
              yp=self.histogram.GetBinContent(bin) 
              if (yp-TMath.Sqrt(yp) < fline.Eval(xp)):
                  break
              else:
                  self.par[3*self.npeaks+2]=yp  #// "height"
                  self.par[3*self.npeaks+3]=xp  #[3*npeaks+3]// "mean"
                  self.par[3*self.npeaks+4]=3   #[3*npeaks+4]// "sigma"
                  self.npeaks+=1
                  
        print(f'Found {self.npeaks} useful peaks to fit\n') 
        print('Now fitting: Be patient\n')
        #a=[]
        #for i in range(0,1000):
        #    a.append(self.fpeaks(i))
        #[b.append(i) for i in range(0,1000)]
        #a=self.fpeaks(b)
        #a=self.fpeaks()
        fit=TF1('fit',fpeaks,0,1000,2+3*self.npeaks)
        #fit.Draw()
        #c1.Update()
        #fit.Draw()
        TVirtualFitter.Fitter(h2,10+3*self.npeaks)
        fit.SetParameters(self.par)
        fit.SetNpx(1000)
        h2.Fit(fit)
        #c1.Update()
      
if __name__ == '__main__':
  try:
    #histo=....  
    FitPeaks(10,histo)
  except:
    raise
