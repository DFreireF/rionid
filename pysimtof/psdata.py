import argparse
import os
import sys
import logging as log
from iqtools import *
from datetime import datetime


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
        
<<<<<<< HEAD
        if self.fft:
            f, p, _ = iq.get_fft(nframes = nframes, lframes = self.binning)
            f = f + iq.center
=======
        if fft:
            freq, power, _ = get_fft(nframes = nframes, lframes = self.lframes)
>>>>>>> origin/master
        else:
            xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.binning)
            axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:, 0]))
            freq = (axx[0, :] + iq.center).reshape(len(axx[0, :]), 1) #frequency, index 0 as xx is 2d array
            power = (azz[0, :]).reshape(len(azz[0, :]), 1) #power
        normalized_power = power / power.max()
        return freq, normalized_power
    
<<<<<<< HEAD
    def _exp_data(self, fft = False):
=======
    def exp_data(self):
>>>>>>> origin/master
        
        if '.root' in self.filename: self.frequency, self.power = self.root_data()
        elif '.Specan' in self.filename : self.frequency, self.power = self.specan_data()        
        elif 'iq' in self.filename: self.frequency, self.power = self.iq_data(read_all = self.read_all) # tiq and iq.tdms ; also the order is important
        else: sys.exit()

def write_spectrum_to_csv(freq, power, filename, center = 0, out = None):
    
    concat_data = np.concatenate((freq, power, IQBase.get_dbm(power)))
    final_data = np.reshape(concat_data, (3, -1)).T
    date_time = datetime.now().strftime('%d.%H.%M')
    if out:
        filename = os.path.basename(filename)
    file_name = f'{filename}.{date_time}.csv'
    if out: file_name = os.path.join(out, file_name)
    print(f'created file: {file_name}')
    np.savetxt(file_name, final_data, header =
               f'Delta f [Hz] @ {center} [Hz]|Power [W]|Power [dBm]', delimiter = '|')
          
def main():
    scriptname = 'pySimToF_Data' 
    parser = argparse.ArgumentParser()

    # Main argument
    parser.add_argument('filename', type = str, nargs = '+', help = 'Name of the input file.')

    # Arguments for processing the data
    parser.add_argument('-t', '--time', type = float, nargs = '?', help = 'For how long in time to analyse.')
    parser.add_argument('-s', '--skip', type = float, nargs = '?', help = 'Starting point in time of the analysis.')
    parser.add_argument('-b', '--binning', type = int, nargs = '?', help = 'Number of frecuency bins.')

    # Fancy arguments
<<<<<<< HEAD
    parser.add_argument('-o', '--outdir', type = str, nargs = '?', default = os.getcwd(), help = 'Output directory.')
=======
    parser.add_argument('-o', '--outdir', type = str, nargs = '?', help = 'Output directory.')
>>>>>>> origin/master
    parser.add_argument('-v', '--verbose', help = 'Increase output verbosity', action = 'store_true')

    # Actions
    parser.add_argument('-fft', '--fft', help= 'Perform fft.', action = 'store_true')
    
    args = parser.parse_args()

    if args.outdir:
        if not os.path.isdir(args.outdir):
            sys.exit('Output directory does not exist. Check it.')

    print(f'Running {scriptname}. Processing...')
    if args.verbose: log.basicConfig(level = log.DEBUG)

    if ('txt') in args.filename[0]:
        filename_list = read_masterfile(args.filename[0])
        for file in filename_list:
            create_exp_spectrum_csv(file[0], args.time, args.skip, args.binning, out = args.outdir, fft = args.fft)
    else:
        for file in args.filename:
            create_exp_spectrum_csv(file, args.time, args.skip, args.binning, out = args.outdir, fft = args.fft) 
    
def read_masterfile(master_filename):
    # reads list filenames with experiment data. [:-1] to remove eol sequence.
    return [file[:-1] for file in open(master_filename).readlines()]
    
<<<<<<< HEAD
def create_exp_spectrum_csv(filename, time, skip, binning, out = None, fft = None):
    myexpdata = ProcessSchottkyData(filename, analysis_time = time, skip_time = skip, binning = binning, fft = fft)
    myexpdata._exp_data()
=======
def create_exp_spectrum_csv(filename, time, skip, binning, out = None):
    myexpdata = ProcessSchottkyData(filename, analysis_time = time, skip_time = skip, binning = binning)
    myexpdata.exp_data()
>>>>>>> origin/master
    write_spectrum_to_csv(myexpdata.frequency, myexpdata.power, filename, out = out)
    
if __name__ == '__main__':
    main()
