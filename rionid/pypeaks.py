from ROOT import TCanvas, TMath, TH1, TH1F, TF1, TRandom, TSpectrum, TVirtualFitter, gApplication
from time import time
from numpy import array,append,argsort

GAUSSIAN_THRESHOLD = 1e-6
GAUSSIAN_UPPER_LIMIT = 1e10

def gaussians(x, par):
    """
    Calculate the sum of gaussians.

    Parameters:
    - x: array-like, input data.
    - par: array-like, parameters for the gaussians.

    Returns:
    - result: sum of the gaussians.
    """
    npeakstofit = 0
    while abs(par[npeakstofit]) > GAUSSIAN_THRESHOLD and abs(par[npeakstofit]) < GAUSSIAN_UPPER_LIMIT:
        npeakstofit += 1
    npeakstofit = (npeakstofit - 3) // 3

    result = par[0] + par[1]*x[0]  # linear part
    for p in range(npeakstofit):
        norm, mean, sigma = par[3*p+2:3*p+5]
        norm /= sigma * TMath.Sqrt(TMath.TwoPi())
        result += norm * TMath.Gaus(x[0], mean, sigma)
    return result

class FitPeaks():

    def __init__(self, npeaks, histogram, tofit):
        self.par = array([], dtype='d')
        self.npeaks = int(npeaks)
        # boolean to make fitting or not (if not, does peak finding etc)
        self.tofit = tofit
        self.histogram = histogram
        self.h2 = histogram

    def set_canvas(self):  # Generates canvas, 1 with found peaks, 1 with fitting
        self.c1 = TCanvas('c1', 'c1', 10, 10, 1000, 900)
        self.c1.Divide(1, 2)

    def peaks(self):
        self.set_canvas()
        self.c1.cd(1)
        self.histogram.Draw()
        self.c1.Update()
        
        self.peak_finding()  # PeakFinding finds peaks (surprise)

        self.set_ranges()

        self.c1.cd(2)
        self.background()
        self.c1.Update()

        if self.tofit:
            n_peaks=self.n_peakstofit()
            info_peaks=self.peaks_info(n_peaks)
            print(info_peaks)
            #self.gaussians_fitting()
            
    def peak_finding(self):
        # Use TSpectrum to find the peak candidates
        self.peak = TSpectrum(self.npeaks) #(maximum number of peaks)
        self.nfound = self.peak.Search(self.histogram, 1,"", 0.0001)
        self.histogram.Draw()
        self.xpeaks=self.peak.GetPositionX()
        return array([self.xpeaks[i] for i in range(0,self.nfound)])

    def peak_finding_background(self):
        #search for peaks once the background is substracted
        self.peakb=TSpectrum(self.npeaks) #(maximum number of peaks)
        self.histogram_background = self.peakb.Background(self.histogram, 20, 'same')
        self.histogram.Add(self.histogram_background,-1)
        self.nfound=self.peakb.Search(self.histogram, 1,"",0.0001)
        xpeaks=self.peakb.GetPositionX()
        return array([xpeaks[i] for i in range(0, self.nfound)])
    
    @staticmethod
    def get_background_average(histogram_list):
        hback_list=array([TSpectrum.Background(histogram,20,'same') for histogram in histogram_list])
        hback=[hback_list[0].Add(hback_list[i]) for i in range(1,len(hback_list))]
        return hback[0]/len(hback_list)
    
    @staticmethod
    def peak_finding2(histogram):
        source, dest, fPositionX, fPositionY = [array([]) for i in range(0,4)]
        nbins=histogram.GetNbinsX()
        histogram.SetTitle('High resolution peak searching, number of iterations = 3')
        histogram.GetXaxis().SetRange(1,nbins)
        histogram_d=TH1F('dest','', nbins, 0, nbins)
        print(nbins)
        for i in range(0, nbins):
            source=append(source, histogram.GetBinContent(i+1)) 
        spectrum=TSpectrum()
        nfound=spectrum.SearchHighRes(source, dest, nbins, 8, 2, True, 3, True, 3)
        print('B')
        xpeaks=spectrum.GetPositionX()
        for peak in xpeaks:
            bin = 1+int(peak+0.5)
            fPositionX=append(fPositionX, histogram.GetBinCenter(bin))
            fPositionY=append(fPositionY, histogram.GetBinContent(bin))
        
        pm = TPolyMarker(nfound, fPositionX, fPositionY)
        histogram.GetListOfFunctions().Add(pm)
        pm.SetMarkerStyle(23)
        pm.SetMarkerColor(kRed)
        pm.SetMarkerSize(1.3)
 
        [histogram_d.SetBinContent(i+1, dest[i]) for i in range(0, nbins)]
        histogram_d.SetLineColor(kRed)
        histogram_d.Draw('SAME')
        input('asdasd')
#        for i in range(0, nfound):
#            calculate distance, barion
        
    def background(self):
        # Estimate background using TSpectrum.Background
        self.histogram_background = self.peak.Background(self.histogram, 20, 'same') #This function calculates the background spectrum in histogram
        # estimate linear background using a fitting method, predefined ROOT pol1
        self.fline = TF1('fline', 'pol1', self.range_min, self.range_max)
        self.histogram.Fit('fline', 'qn')

    def n_peakstofit(self):  # Loop on all found peaks. Eliminate peaks at the background level
        n_peakstofit = 0
        self.par = append(
            self.par, [self.fline.GetParameter(0), self.fline.GetParameter(1)])
        for xpeak in (self.xpeaks):
            xbin=self.histogram.GetXaxis().FindBin(xpeak) 
            ypeak=self.histogram.GetBinContent(xbin)
            if (ypeak) > self.fline.Eval(xpeak):#compares if peak is over the background or not
                self.par=append(self.par,[ypeak,xpeak,100])#mean,height,sigma;initial seeds for the fitting
                n_peakstofit+=1
        print(f'Found {n_peakstofit} useful peaks to fit\n')
        return n_peakstofit
        
    def peaks_info(self,npeaks):#return array with ypeak, xpeak of each peak, sorted in decreasing order
        height,position,aux2=(array([]) for _ in range(3))
        for i in range(0,npeaks):
           height=append(height,[self.par[3*i+2]])
           position=append(position,[self.par[3*i+3]])
        aux=argsort(height)
        for index in aux:
            aux2=append(aux2,[height[index],position[index]])
        return aux2[::-1]

    def gaussians_fitting(self):
        print(f'Now fitting: it takes some time \n')
        self.hcopy=self.histogram.Copy()
        for i in range(0, 10):  # loop for making the thing to converge
            start_time = time()
            npars = int(len(self.par))
            fit = TF1('fit', gaussians, self.range_min, self.range_max, npars)
            TVirtualFitter.Fitter(self.hcopy, npars)
            fit.SetParameters(self.par)
            fit.SetNpx(1000)
            self.hcopy.Fit(fit)
            self.c1.Update()
            getpar = self.hcopy.GetFunction('fit')
            for j in range(getpar.GetNumberFreeParameters()):
                self.par[j] = getpar.GetParameter(j)
            print(f'it took {time()-start_time} seconds, not that bad')
    
    def set_ranges(self):
        self.range_min = self.histogram.GetXaxis().GetXmin()
        self.range_max = self.histogram.GetXaxis().GetXmax()