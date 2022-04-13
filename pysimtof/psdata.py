import argparse
import os
import logging as log
from datetime import datetime

class ProcessSchottkyData(object):
    '''
    Class for Schottky data processing
    '''
    def __init__(self, filename, skip_time = None, analysis_time = None, binning = None):
        self.filename = filename
        self.skip_time = skip_time
        self.analysis_time = analysis_time
        self.binnig = binning
         
    def _exp_data(self):
        
        if 'root' in self.filename: self.exp_data = self.exp_data_root()
        elif 'tiq' in self.filename: self.exp_data = self.exp_data_analyser()
        elif 'tdms' in self.filename: self.exp_data = self.exp_data_ntcap()
        elif 'Specan' in self.filename : self.exp_data = self.exp_data_specan()
        
        else: sys.exit()
        

     def exp_data_root(self):
          ##This part may need to be changed to have the same frecuency "units"
          fdata = TFile(self.filename)
          histogram = fdata.Get('FFT_Total_px')# change this to, fdata.ls() and choose one
             f = np.array([[histogram.GetXaxis().GetBinCenter(i) * 1e6] for i in range(1, histogram.GetNbinsX())])#*1000+245*10**6
             p = np.array([[histogram.GetBinContent(i)] for i in range(1, histogram.GetNbinsX())])          
             return (np.stack((f, p), axis = 1)).reshape((len(f),2))

    def iq_data(self, read_all = False):

        iq = get_iq_object(self.filename)
        nframes = int(self.data_time * iq.fs / self.lframes)
        sframes = int(self.skip_time * iq.fs / self.lframes)
        iq.read(nframes = nframes, lframes = self.lframes, sframes = sframes)
        xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.lframes)
        axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:,0]))
        ff = (axx[0, :] + iq.center).reshape(len(axx[0, :]),1) #frequency, index 0 as xx is 2d array
        pp = (azz[0, :]).reshape(len(azz[0, :]),1) #power
        pp = pp / pp.max()
        return (np.stack((ff, pp), axis = 1)).reshape((len(ff), 2))
    
    def exp_data_ntcap(self):
        
        iq = get_iq_object(self.filename)
        iq.read_samples(1)
        nframes = int(self.data_time * iq.fs / self.lframes)
        sframes = int(self.skip_time * iq.fs / self.lframes)
        iq.read(nframes = nframes, lframes = self.lframes, sframes = sframes)        
        # import xx:frequency, yy:time, zz:power
        xx, yy, zz = iq.get_spectrogram(nframes = nframes, lframes = self.lframes)
        axx, ayy, azz = get_averaged_spectrogram(xx, yy, zz, len(xx[:,0]))
        ff = (axx[0, :] + iq.center).reshape(len(axx[0, :]),1) #frequency, index 0 as xx is 2d array
        pp = (azz[0, :]).reshape(len(azz[0, :]),1) #power
        pp = pp / pp.max()
        return (np.stack((ff, pp), axis = 1)).reshape((len(ff), 2))
    
    def exp_data_specan(self):
        
        f, p, _ = read_rsa_specan_xml(self.filename)
        p = p - p.min()
        p = p / p.max()
        return (np.stack((f, p), axis = 1)).reshape((len(f), 2))

   def _set_tertiary_args(self, data_time, skip_time, binning):
        
        self.data_time = data_time
        self.skip_time = skip_time
        self.lframes = binning

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
    
    parser.add_argument('filename', type = str, nargs = '+', help = 'Name of the input file.')
    
    parser.add_argument('-t', '--time', type = float, default = 1, help = 'Data time to analyse.')
    parser.add_argument('-s', '--skip', type = float, default = 0, help = 'Start of the analysis.')
    parser.add_argument('-b', '--binning', type = int, default = 1024, help = 'Number of frecuency bins.')
    parser.add_argument('-o', '--outdir', type = str, default = '.', help = 'output directory.')

    parser.add_argument('-v', '--verbose',
                        help = 'Increase output verbosity', action = 'store_true')

    args = parser.parse_args()

    print(f'Running {scriptname}')
    if args.verbose: log.basicConfig(level = log.DEBUG)
    if args.outdir: outfilepath = os.path.join(args.outdir, '')

    if ('txt') in args.filename[0]:
        filename_list = read_masterfile(args.filename[0])
        for filename in filename_list:
            controller(filename[0], args.time, args.skip, args.binning)
    else:
        for file in args.filename:
            controller(filename[0], args.time, args.skip, args.binning)
    
def read_masterfile(master_filename):
    # reads list filenames with experiment data. [:-1] to remove eol sequence.
    return [file[:-1] for file in open(master_filename).readlines()]
    
def create_exp_spectrum(filename, time, skip, binning):
    
    myexpdata = Process(filename, harmonics, ref_nuclei, ref_charge, brho, gammat)
    mydata._set_secondary_args(lise_file)
    mydata._set_tertiary_args(time, skip, binning)
    mydata._exp_data() # -> exp_data
    mydata.calculate_moqs()
    mydata._calculate_srrf() # -> moq ; srrf
    mydata._simulated_data() # -> simulated frecs
    
    mycanvas = CreateGUI(ref_nuclei, mydata.nuclei_names, ndivs, dops)
    mycanvas._view(mydata.exp_data, mydata.simulated_data_dict, filename)
        
    
if __name__ == '__main__':
    main()
