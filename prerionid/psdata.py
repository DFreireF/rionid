import sys
from iqtools import *

class ProcessSchottkyData(object):
    '''
    Class for Schottky data processing
    '''
    def __init__(self, filename, skip_time = None, analysis_time = None, binning = None, fft = False):

        self.filename = filename
        self.read_all = False
        self.fft = fft
        if skip_time is not None and analysis_time is not None and binning is not None: 
            self.skip_time = skip_time
            self.analysis_time = analysis_time
            self.binning = binning
        else:
            self.read_all = True
        
    def root_data(self):
        
        from ROOT import TFile
        fdata = TFile(self.filename)
        histogram = fdata.Get(fdata.GetListOfKeys()[0].GetName())
        freq = np.array([[histogram.GetXaxis().GetBinCenter(i) * 1e6] for i in range(1, histogram.GetNbinsX())]) # 1e6 for units
        power = np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbinsX())])          
        return freq, power

    def specan_data(self):
        
        freq, power, _ = read_rsa_specan_xml(self.filename)
        power = power - power.min() #in order to avoid negative values: power - (-|value_min|) > power
        normalized_power = power / power.max()
        return freq, normalized_power

    def iq_data(self, read_all = False):

        iq = get_iq_object(self.filename)
        iq.read_samples(1) # Necessary for iq.tdms files
        if not read_all:
            nframes = int(self.analysis_time * iq.fs / self.binning)
            sframes = int(self.skip_time * iq.fs / self.binning)
            iq.read(nframes = nframes, lframes = self.binning, sframes = sframes)
        else:
            iq.read_samples(iq.nsamples_total)
        
        if self.fft:
            f, p, _ = iq.get_fft(nframes = nframes, lframes = self.binning)
            f = f + iq.center
        else:
            xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.binning)
            axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:, 0]))
            freq = (axx[0, :] + iq.center).reshape(len(axx[0, :]), 1) #frequency, index 0 as xx is 2d array
            power = (azz[0, :]).reshape(len(azz[0, :]), 1) #power
        normalized_power = power / power.max()
        return freq, normalized_power
    
    def _exp_data(self, fft = False):
        
        if '.root' in self.filename: 
            self.frequency, self.power = self.root_data()
        elif '.Specan' in self.filename: 
            self.frequency, self.power = self.specan_data()        
        elif 'iq' in self.filename: 
            self.frequency, self.power = self.iq_data(read_all = self.read_all) # tiq and iq.tdms ; also the order is important
        else: sys.exit()

