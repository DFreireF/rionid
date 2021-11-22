import creategui, inputparams
# import importdata


def main():
    parameter_filename = 'data/InputParameters.txt'
    ip=inputparams.InputParams(parameter_filename)
    
    # 'data/410-j' is now in pdict['']
    print(ip.dict['rawdata_filename'])
    
    #now pass filename of rawdata to ImportData
    
    #then,
    mycanvas = creategui.CreateGUI() 


if __name__ == '__main__':
    main()
