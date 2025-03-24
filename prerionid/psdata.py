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
        self.read_all = False

        if binning is not None:
            self.binning = int(binning)
        elif time_bin_size is not None:
            self.binning = int(self.iq.fs * time_bin_size)

        if skip_time is not None and analysis_time is not None:
            self.nframes = int(analysis_time * self.iq.fs / self.binning)
            self.sframes = int(skip_time     * self.iq.fs / self.binning)
        else:
            self.read_all = True
            self.nframes = int(self.iq.nsamples_total / self.binning)

    def get_exp_data(self):

        if not self.read_all:
            self.iq.read(nframes = self.nframes, lframes = self.binning, sframes = self.sframes)
        else:
            self.iq.read_samples(self.iq.nsamples_total)
        
        xx, _, zz = self.iq.get_power_spectrogram(nframes = self.nframes, lframes = self.binning, sparse = True)
        
        self.freq = xx[0,:] + self.iq.center
        self.power = np.average(zz, axis = 0) #power

    def save_exp_data(self, outdir = None):
        #add also path
        if outdir:
            outfile = outdir + '_'+datetime.now().strftime('%Y-%M-%d_%H.%M.%S')
        else:
            outfile = self.filename+'_'+datetime.now().strftime('%Y-%M-%d_%H.%M.%S')
        np.savez(outfile, x = self.freq, y = self.power)