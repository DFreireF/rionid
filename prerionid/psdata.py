import sys
from iqtools import *
from datetime import datetime

class ProcessSchottkyData(object):
    '''
    Class for Schottky data processing
    '''
    def __init__(self, filename, skip_time = None, analysis_time = None, binning = None, time_bin_size = None, method = 'npfft'):

        self.filename = filename
        self.iq = get_iq_object(filename)
        self.method = method #['npfft', 'fftw', 'welch', 'mtm']

        if binning is not None:
            self.binning = binning
        elif time_bin_size is not None:
            self.binning = int(self.iq.fs * time_bin_size)

        if skip_time is not None and analysis_time is not None:
            self.nframes = int(analysis_time * self.iq.fs / self.binning)
            self.sframes = int(skip_time     * self.iq.fs / self.binning)
        else:
            self.read_all = True

    def tdms_data(self, read_all = False):

        iq = get_iq_object(self.filename)
        if not read_all:
            nframes = int(self.analysis_time * iq.fs / self.binning)
            sframes = int(self.skip_time * iq.fs / self.binning)
            iq.read(nframes = nframes, lframes = self.binning, sframes = sframes)
        else:
            iq.read_samples(iq.nsamples_total)
        
        xx, _, zz = iq.get_spectrogram(nframes = nframes, lframes = self.binning)
        
        freq = xx[0,:] + iq.center
        power = (azz[0, :]).reshape(len(azz[0, :]), 1) #power
        return freq, power
    
    def tiq_data(self, time = None, skip = None):
        
        if time and skip:
            nframes = int(self.analysis_time * self.iq.fs / self.binning)
            sframes = int(self.skip_time * self.iq.fs / self.binning)
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

    def get_exp_data(self):
        if 'tdms' in self.filename: 
            self.frequency, self.power = self.tdms_data()
        elif 'tiq' in self.filename: 
            self.frequency, self.power = self.tiq_data()        
        else: 
            sys.exit()

    def save_exp_data(self):
        #add also path
        outfile = f'{self.filename}_{datetime.now().strftime('%d-%H.%M.%S')}'
        np.savez(outfile, x = self.frequency, y = self.power)

#def root_data(self):
#        
#    from ROOT import TFile
#    fdata = TFile(self.filename)
#    histogram = fdata.Get(fdata.GetListOfKeys()[0].GetName())
#    freq = np.array([[histogram.GetXaxis().GetBinCenter(i) * 1e6] for i in range(1,histogram.#GetNbinsX())]) # 1e6 for units
#    power = np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbins#())])          
#    return freq, power
#
#def specan_data(self):
#        
#    freq, power, _ = read_rsa_specan_xml(self.filename)
#    power = power - power.min() #in order to avoid negative values: power - (-|value_min|) > #power
#    normalized_power = power / power.max()
#    return freq, normalized_power