import creategui
import inputparams
import importdata


def main():
    parameter_filename = 'data/InputParameters.txt'
    ip = inputparams.InputParams(parameter_filename)

    # import data and process:
    mydata = importdata.ImportData(ip.dict['rawdata_filename'])
    print(mydata.ff)
    print(mydata.pp)

    # plot:
    mycanvas = creategui.CreateGUI(mydata.ff, mydata.pp, mydata.SRF,
                                   mydata.frequence_min, mydata.frequence_max,
                                   mydata.nbins)


if __name__ == '__main__':
    main()
