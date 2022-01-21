import argparse
import logging as log
from ROOT import *
from pysimtof.importdata import *
from pysimtof.creategui import *
from pysimtof.version import __version__

def main():
    scriptname = 'pySimToF' 
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, default='data/245test.tiq', help='Name of the input file.')
    parser.add_argument('-l', '--lise_file', type=str, nargs='?', default='data/E143_TEline-ESR-72Ge.lpp', help='Name of the LISE file.')
    parser.add_argument('-hdr', '--header-filename', nargs='?', type=str, default=None,
                        help='Name of header file.')
    
    parser.add_argument('-hrm', '--harmonics', type=int, nargs='+', help='Harmonics to simulate')
    parser.add_argument('-b', '--brho', type=float, default=6.90922, help='Brho value of the reference ion beam at ESR')
    parser.add_argument('-g', '--gammat', type=float, default=1.395, help='GammaT value of ESR')
    
    parser.add_argument('-i', '--refisotope', type=str, default='72Ge', help='Isotope of study')
    parser.add_argument('-c', '--refcharge', type=float, default=32, help='Charge state of the studied isotope')

    parser.add_argument('-v', '--verbose',
                        help='Increase output verbosity', action='store_true')
    
    parser.add_argument("-s", "--spdf",
                        help="Save canvas to pdf.", action="store_true")

    args = parser.parse_args()
    
    print(f'Running {scriptname} V{__version__}')
    if args.verbose: log.basicConfig(level=log.DEBUG)

    # here we go:
    log.info(f'File {args.filename} passed for processing the information of {args.refisotope}+{args.refcharge}.')
    
    
    mydata=ImportData(args.filename, args.lise_file, args.harmonics, args.brho, args.gammat, args.refisotope, args.refcharge)
    mycanvas = CreateGUI(mydata.exp_data, mydata.simulated_data_dict, args.refisotope, mydata.nuclei_names)
    mycanvas()
        
        
    if args.spdf: mycanvas.save_plot_pdf()##have to change this
    gApplication.Run()    

if __name__ == '__main__':
    main()
