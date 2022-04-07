import argparse
import os
import logging as log
from pysimtof.importdata import *
from pysimtof.creategui import *


def main():
    
    scriptname = 'pySimToF' 
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required = True)

    # Main arguments
    parser.add_argument('datafile', type = str, nargs = '+', help = 'Name of the input file with data.')
    parser.add_argument('-hrm', '--harmonics', type = int, nargs = '+', help = 'Harmonics to simulate.')
    parser.add_argument('-ap', '--alphap', type = float, help = 'Momentum compaction factor of the ring.')
    parser.add_argument('-r', '--refion', type = str, help = 'Reference ion with format NucleonsNameChargestate :=  AAXX+CC. Example: 72Ge+35, 1H+1, 238U+92...')
    parser.add_argument('-psim', '--filep', type = str, help = 'Read list of particles to simulate. LISE file or something else.')

    # Arguments for each mode (exclusive)
    modes.add_argument('-b', '--brho', type = float, help = 'Brho value of the reference nucleus at ESR (isochronous mode).')
    modes.add_argument('-f', '--frev', type = float, help = 'Revolution frequency of the reference particle (standard mode).')
    
    # Arguments for the visualization
    parser.add_argument('-d', '--ndivs', type = int, default = 4, help = 'Number of divisions in the display.')
    parser.add_argument('-o', '--dops', type = int, default = 0, help = 'Display of srf data options. 0 -> constant height, else->scaled.')
    
    # Actions
    parser.add_argument('-v', '--verbose', help = 'Increase output verbosity.', action = 'store_true')
    parser.add_argument('-s', '--show', help = 'Show display. If not, save root file and close display', action = 'store_true')

    args = parser.parse_args()

    # Checking for arguments errors
    if args.brho is None and args.frev is None:
        parser.error('Please introduce the revolution frequency of the reference nucleus or the brho parameter.')

    # Extra details
    if args.verbose: log.basicConfig(level = log.DEBUG)
    if args.outdir: outfilepath = os.path.join(args.outdir, '')

    # Here we go:
    print(f'Running {scriptname}... Lets see what we have in our ring ;-)')
    log.info(f'File {args.datafile} passed for processing the information of {args.refion}.')

    # If it is a txt file with files or just files introduced by the terminal
    if ('txt') in args.datafile[0]:
        filename_list = read_masterfile(args.datafile[0])
        for datafile in datafile_list:
            controller(datafile[0], args.filep, args.harmonics, args.alphap, args.refion, args.ndivs, args.dops, args.show, brho = args.brho, frev = args.frev)
    else:
        for file in args.datafile:
            controller(file, args.filep, args.harmonics, args.alphap, args.refion, args.ndivs, args.dops, args.show, brho = args.brho, frev = args.frev)
    
def controller(data_file, particles_to_simulate, harmonics, alphap, ref_ion, ndivs, dops, show, brho = None, frev = None):
    
    mydata = ImportData(filename, harmonics, ref_nuclei, ref_charge, brho, gammat)
    mydata._set_secondary_args(particles_to_simulate)
    
    mydata._set_tertiary_args(time, skip, binning)
    mydata._exp_data() # -> exp_data
    
    mydata.calculate_moqs()
    mydata._calculate_srrf() # -> moq ; srrf
    mydata._simulated_data() # -> simulated frecs
    
    mycanvas = CreateGUI(ref_ion, mydata.nuclei_names, ndivs, dops, show)
    mycanvas._view(mydata.exp_data, mydata.simulated_data_dict, filename)
        
    

def read_masterfile(master_filename):
    # reads list filenames with experiment data. [:-1] to remove eol sequence.
    return [file[:-1] for file in open(master_filename).readlines()]

if __name__ == '__main__':
    main()
    
    '''
    Execution examples:
    /lustre/ap/litv-exp/2020-04-14_E121_rchen/NTCAP/iq/IQ_2020-04-06_00-59-38/0000126.iq.tdms
    python __main__.py frec_rui.root -l Tl205.lpp -hrm 124 125 126 127 -b 7.892305 -g 2.4234 -i 205Tl -c 81 -s -r
    python __main__.py /lustre/ap/litv-exp/2020-04-14_E121_rchen/NTCAP/iq/IQ_2020-04-06_00-59-38/0000126.iq.tdms -l Tl205.lpp -hrm 124 125 126 127 -b 7.892305 -g 2.4234 -i 205Tl -c 81 -s -r
    python __main__.py -l data/E143_TEline-ESR-72Ge.lpp -hrm 208 209 210 -g 1.395 -i 72Ge -c 32 -o 0 -d 1 -b 6.930373 /lustre/ap/litv-exp/2021-05-00_E143_TwoPhotonDeday_ssanjari/analyzers/410MHz/E143-410MHz-2021.05.08.21.18.07.820.tiq
    python __main__.py -l data/E143_TEline-ESR-72Ge.lpp -hrm 208 209 210 -g 1.395 -i 72Ge -c 32 -o 0 -d 1 -b 6.930373 410-isomer.txt
    '''    
