import creategui
import inputparams
import importdata
import pypeaks


def main():
    parameter_filename = 'data/InputParameters.txt'
    ip = inputparams.InputParams(parameter_filename)

    # import data and process:
    mydata = importdata.ImportData(ip.dict['rawdata_filename'])
    #peaks=pypeaks.FitPeaks(5,mydata.h,True)
    #peaks()
    #peaks=pypeaks.FitPeaks(5,mydata.h)

    # plot:
    mycanvas = creategui.CreateGUI(mydata.ff, mydata.pp, mydata.SRF,
                                   mydata.yield_data_normalised,
                                   mydata.SRRF, mydata.fcenter)


if __name__ == '__main__':
    main()
