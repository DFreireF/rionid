import argparse
import os
import logging as log
from datetime import datetime
from pysimtof.importdata import *
from pysimtof.creategui import *


def main():
    
    scriptname = 'pySimToF' 
    parser = argparse.ArgumentParser()
    
    parser.add_argument('filename', type = str, nargs = '+', help = 'Name of the input file.')
    parser.add_argument('-l', '--lise_file', type = str, nargs = '?',help = 'Name of the LISE file.')
    parser.add_argument('-hrm', '--harmonics', type = int, nargs = '+', help = 'Harmonics to simulate.')
    parser.add_argument('-b', '--brho', type = float, default = 6.90922, help = 'Brho value of the reference ion beam at ESR.')
    parser.add_argument('-g', '--gammat', type = float, default = 1.395, help = 'GammaT value of ESR.')
    parser.add_argument('-i', '--refisotope', type = str, default = '72Ge', help = 'Isotope of study.')
    parser.add_argument('-c', '--refcharge', type = int, default = 32, help = 'Charge state of the studied isotope.')
    parser.add_argument('-d', '--ndivs', type = int, default = 4, help = 'Number of divisions in the display.')
    parser.add_argument('-o', '--dops', type = int, default = 1, help = 'Display of srf data options. 0-> constant height, else->scaled.')
    parser.add_argument('-t', '--time', type = float, default = 1, help = 'Data time to analyse.')
    parser.add_argument('-sk', '--skip', type = float, default = 0, help = 'Start of the analysis.')
    parser.add_argument('-bin', '--binning', type = int, default = 1024, help = 'Number of frecuency bins.')
    parser.add_argument('-out', '--outdir', type = str, default = '.', help = 'output directory.')

    parser.add_argument('-v', '--verbose',
                        help = 'Increase output verbosity', action = 'store_true')

    parser.add_argument('-s', '--spdf',
                        help = 'Save canvas to pdf.', action = 'store_true')

    parser.add_argument('-r', '--sroot',
                        help = 'Save canvas to root.', action = 'store_true')

    args = parser.parse_args()

    print(f'Running {scriptname}')
    if args.verbose: log.basicConfig(level = log.DEBUG)
    if args.outdir: outfilepath = os.path.join(args.outdir, '')

    # here we go:
    log.info(f'File {args.filename} passed for processing the information of {args.refisotope}+{args.refcharge}.')
    
    if ('txt') in args.filename[0]:
        filename_list = read_masterfile(args.filename[0])
        for filename in filename_list:
            controller(filename[0], args.lise_file, args.harmonics, args.brho, args.gammat, args.refisotope, args.refcharge, args.ndivs, args.dops, args.spdf, args.sroot, args.time, args.skip, args.binning)
    else:
        for file in args.filename:
            controller(file, args.lise_file, args.harmonics, args.brho, args.gammat, args.refisotope, args.refcharge, args.ndivs, args.dops, args.spdf, args.sroot, args.time, args.skip, args.binning)
            gApplication.Run()
    
def read_masterfile(master_filename):
    # reads list filenames with experiment data. [:-1] to remove eol sequence.
    return [file[:-1] for file in open(master_filename).readlines()]
    
def controller(filename, lise_file, harmonics, brho, gammat, ref_nuclei, ref_charge, ndivs, dops, spdf, sroot, time, skip, binning):
    
    mydata = ImportData(filename, harmonics, ref_nuclei, ref_charge, brho, gammat)
    mydata._set_secondary_args(lise_file)
    mydata._set_tertiary_args(time, skip, binning)
    mydata._exp_data() # -> exp_data
    mydata.calculate_moqs()
    mydata._calculate_srrf() # -> moq ; srrf
    mydata._simulated_data() # -> simulated frecs
    
    mycanvas = CreateGUI(ref_nuclei, mydata.nuclei_names, ndivs, dops)
    mycanvas._view(mydata.exp_data, mydata.simulated_data_dict, filename)
        
    date_time = datetime.now().strftime('%Y.%m.%d_%H.%M.%S')
    info_name = f'{outfilepath}{date_time}_b{brho}_g{gammat}'
    if spdf: mycanvas.save_pdf(info_name)
    if sroot: mycanvas.save_root(info_name)

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
