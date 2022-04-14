import argparse
import os
import logging as log
from iqtools import *
from datetime import datetime

class ProcessSchottkyData(object):
    '''
    Class for Schottky data processing
    '''
    def __init__(self, filename, skip_time = None, analysis_time = None, binning = None):

        self.filename = filename
        self.read_all = False
        if skip_time is not None and analysis_time is not None and binning is not None: 
            self.skip_time = skip_time
            self.analysis_time = analysis_time
            self.binnig = binning
        else:
            self.read_all = True
         
    def _exp_data(self):
        
        if '.root' in self.filename: self.frequency, self.power = self.exp_data_root()
        elif '.Specan' in self.filename : self.frequency, self.power = self.exp_data_specan()        
        elif 'iq' in self.filename: self.frequency, self.power = self.iq_data(read_all = self.read_all)
        else: sys.exit()
        
    def exp_data_root(self):
        from ROOT import *
        ##This part may need to be changed to have the same frecuency "units"
        fdata = TFile(self.filename)
        histogram = fdata.Get('FFT_Total_px')# change this to, fdata.ls() and choose one
        f = np.array([[histogram.GetXaxis().GetBinCenter(i) * 1e6] for i in range(1, histogram.GetNbinsX())])#*1000+245*10**6
        p = np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbinsX())])          
        return f, p

    def exp_data_specan(self):
        
        f, p, _ = read_rsa_specan_xml(self.filename)
        p = p - p.min()
        p = p / p.max()
        return f, p

    def iq_data(self, read_all = False, fft = True):

        iq = get_iq_object(self.filename)
        iq.read_samples(1)
        if not read_all:
            nframes = int(self.data_time * iq.fs / self.lframes)
            sframes = int(self.skip_time * iq.fs / self.lframes)
            iq.read(nframes = nframes, lframes = self.lframes, sframes = sframes)
        else:
            iq.read_samples(iq.nsamples_total)
        
        if fft:
            f, p, _ = get_fft(nframes = nframes, lframes = self.lframes)
        else:
            xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.lframes)
            axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:, 0]))
            f = (axx[0, :] + iq.center).reshape(len(axx[0, :]), 1) #frequency, index 0 as xx is 2d array
            p = (azz[0, :]).reshape(len(azz[0, :]), 1) #power
        p = p / p.max()
        return f, p

def write_spectrum_to_csv(f, p, filename, center = 0):
    a = np.concatenate((f, p, IQBase.get_dbm(p)))
    b = np.reshape(a, (3, -1)).T
    
    date_time = datetime.now().strftime('%d_%H.%M.')
    file_name = f'{outfilepath}{date_time}_{filename}.csv'
    
    np.savetxt(file_name, b, header =
               'Delta f [Hz] @ {:.2e} [Hz]|Power [W]|Power [dBm]'.format(center), delimiter='|')
          
def main():
    scriptname = 'pySimToF_Data' 
    parser = argparse.ArgumentParser()

    # Main argument
    parser.add_argument('filename', type = str, nargs = '+', help = 'Name of the input file.')

    # Arguments for processing the data
    parser.add_argument('-t', '--time', type = float, nargs = '?', help = 'Data time to analyse.')
    parser.add_argument('-s', '--skip', type = float, nargs = '?', help = 'Start of the analysis.')
    parser.add_argument('-b', '--binning', type = int, nargs = '?', help = 'Number of frecuency bins.')

    # Fancy arguments
    parser.add_argument('-o', '--outdir', type = str, default = '.', help = 'output directory.')
    parser.add_argument('-v', '--verbose', help = 'Increase output verbosity', action = 'store_true')

    args = parser.parse_args()

    print(f'Running {scriptname}. Processing...')
    if args.verbose: log.basicConfig(level = log.DEBUG)
    if args.outdir: outfilepath = os.path.join(args.outdir, '')

    if ('txt') in args.filename[0]:
        filename_list = read_masterfile(args.filename[0])
        for filename in filename_list:
            create_exp_spectrum_csv(filename[0], args.time, args.skip, args.binning)
    else:
        for file in args.filename:
            create_exp_spectrum_csv(filename[0], args.time, args.skip, args.binning)            
    
def read_masterfile(master_filename):
    # reads list filenames with experiment data. [:-1] to remove eol sequence.
    return [file[:-1] for file in open(master_filename).readlines()]
    
def create_exp_spectrum_csv(filename, time, skip, binning):
    myexpdata = ProcessSchottkyData(filename, analysis_time = time, skip_time = skip, binning = binning)
    write_spectrum_to_csv(myexpdata.frequency, myexpdata.power, filename)
    
if __name__ == '__main__':
    main()
