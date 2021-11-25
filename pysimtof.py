import creategui
import inputparams
import importdata
import pypeaks


def main():
    parameter_filename = 'data/InputParameters.txt'
    ip = inputparams.InputParams(parameter_filename)

    # import data and process:
    mydata = importdata.ImportData(ip.dict['rawdata_filename'])
    peaks=pypeaks.FitPeaks(1,mydata.h)
    #peaks()
    # print(mydata.ff)
    # print(mydata.pp)

    # plot:
    #mycanvas = creategui.CreateGUI(mydata.ff, mydata.pp, mydata.SRF,
    #                               mydata.yieldd, mydata.SRRF, mydata.fcenter)


if __name__ == '__main__':
    main()
