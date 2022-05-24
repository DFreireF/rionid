import argparse
import os
import logging as log
from pysimtof.importdata import *
from pysimtof.creategui import *


def main():
    
    scriptname = 'pySimToF' 
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required = True)

    # Main Arguments
    parser.add_argument('datafile', type = str, nargs = '+', help = 'Name of the input file with data.')
    parser.add_argument('-ap', '--alphap', type = float, help = 'Momentum compaction factor of the ring.')
    parser.add_argument('-r', '--refion', type = str, help = 'Reference ion with format NucleonsNameChargestate :=  AAXX+CC. Example: 72Ge+35, 1H+1, 238U+92...')
    parser.add_argument('-psim', '--filep', type = str, help = 'Read list of particles to simulate. LISE file or something else.')
    
    # Secondary Arguments
    parser.add_argument('-hrm', '--harmonics', type = int, nargs = '*', help = 'Harmonics to simulate.')

    # Arguments for Each Mode (Exclusive)
    modes.add_argument('-b', '--brho', type = float, help = 'Brho value of the reference nucleus at ESR (isochronous mode).')
    modes.add_argument('-ke', '--kenergy', type = float, help = 'Kinetic energy of reference nucleus at ESR (isochronous mode).')
    modes.add_argument('-f', '--fref', type = float, help = 'Revolution frequency of the reference particle (standard mode).')
    
    # Arguments for the Visualization
    parser.add_argument('-d', '--ndivs', type = int, default = 4, help = 'Number of divisions in the display.')
    parser.add_argument('-am', '--amplitude', type = int, default = 0, help = 'Display of srf data options. 0 -> constant height, else->scaled.')
    
    # Actions
    parser.add_argument('-l', '--log', dest = 'logLevel', choices = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default = 'INFO', help = 'Set the logging level.')
    parser.add_argument('-s', '--show', help = 'Show display. If not, save root file and close display', action = 'store_true')
    parser.add_argument('-o', '--outdir', type = str, nargs = '?', default = os.getcwd(), help = 'Output directory.')

    args = parser.parse_args()

    # Checking for Argument Errors
    if args.brho is None and args.fref is None and args.kenergy is None:
        parser.error('Please introduce the revolution frequency of the reference nucleus or the brho parameter.')

    # Extra Details
    if args.logLevel: log.basicConfig(level = log.getLevelName(args.logLevel))
    if args.outdir: outfilepath = os.path.join(args.outdir, '')

    # Here We Go:
    print(f'Running {scriptname}... Lets see what we have in our ring ;-)')
    log.info(f'File {args.datafile} passed for processing the information of {args.refion}.')

    # If it is a txt file with files or just files introduced by the terminal
    if ('txt') in args.datafile[0]:
        datafile_list = read_masterfile(args.datafile[0])
        for datafile in datafile_list:
            controller(datafile[0], args.filep, args.harmonics, args.alphap, args.refion, args.ndivs, args.amplitude, args.show, brho = args.brho, fref = args.fref, ke = args.kenergy, out = args.outdir, harmonics = args.harmonics)
    else:
        for file in args.datafile:
            controller(file, args.filep, args.alphap, args.refion, args.ndivs, args.amplitude, args.show, brho = args.brho, fref = args.fref, ke = args.kenergy, out = args.outdir, harmonics = args.harmonics)
    
def controller(data_file, particles_to_simulate, alphap, ref_ion, ndivs, amplitude, show, brho = None, fref = None, ke = None, out = None, harmonics = None):
    
    log.debug(f'Tracking of variables introduced:\n {data_file} = data_file, {particles_to_simulate} = particles_to_simulate, {harmonics} = harmonics, {alphap} = alphap, {ref_ion} = ref_ion, {ndivs} = ndivs, {amplitude} = amplitude, {show} = show, {brho} = brho, {fref} = fref, {ke} = ke')
    
    mydata = ImportData(ref_ion, alphap, filename = data_file)
    log.debug(f'Experimental data = {mydata.experimental_data}')
    mydata._set_particles_to_simulate_from_file(particles_to_simulate)
    
    mydata._calculate_moqs()
    log.debug(f'moqs = {mydata.moq}')
    
    mydata._calculate_srrf(fref = fref, brho = brho, ke = ke)
    log.debug(f'Revolution (or meassured) frequency of {ref_ion} = {mydata.ref_frequency}')
    
    mydata._simulated_data(harmonics = harmonics) # -> simulated frecs
    log.debug(f'Simulation results = {mydata.simulated_data_dict}')
    log.info(f'Simulation performed. Now we are going to start the display.')
    
    mycanvas = CreateGUI(ref_ion, mydata.nuclei_names, ndivs, amplitude, show)
    mycanvas._view(mydata.experimental_data, mydata.simulated_data_dict, filename = data_file, out = out)
    
    log.info(f'Program has ended. Hope you have found what you were looking for. :)')
        
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
