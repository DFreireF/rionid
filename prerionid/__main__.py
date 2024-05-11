import argparse
import sys
import os
import logging as log


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
    scriptname = 'RionID_DataProcessing' 
    print(scriptname)
    parser = argparse.ArgumentParser()

    # Main argument
    parser.add_argument('filename', type = str, nargs = '+', help = 'Name of the input file.')

    # Arguments for processing the data
    parser.add_argument('-t', '--time', type = float, nargs = '?', help = 'For how long in time to analyse.')
    parser.add_argument('-s', '--skip', type = float, nargs = '?', help = 'Starting point in time of the analysis.')
    parser.add_argument('-b', '--binning', type = int, nargs = '?', help = 'Number of frecuency bins.')

    # Fancy arguments
    parser.add_argument('-o', '--outdir', type = str, nargs = '?', default = os.getcwd(), help = 'Output directory.')
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

def create_exp_spectrum_csv(filename, time, skip, binning, out = None, fft = None):
    myexpdata = ProcessSchottkyData(filename, analysis_time = time, skip_time = skip, binning = binning, fft = fft)
    myexpdata._exp_data()
    write_spectrum_to_csv(myexpdata.frequency, myexpdata.power, filename, out = out)
    
if __name__ == '__main__':
    main()
