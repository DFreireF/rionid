from ROOT import *
import numpy as np


class CreateGUI():
    def __init__(self, analyzers_data,
                  simulated_data, NTCAP_data,harmonics):
        # setting object variables: add NTCAP_data,
        self.analyzers_data = analyzers_data #frec =analyzers_data[:,0]   power =analyzers_data[:,1]
        self.simulated_data=simulated_data # harmonic= simulated_data[:,0] frec=simulated_data[:,1] power=simulated_data[:,2]
        self.NTCAP_data=NTCAP_data
        self.harmonics=harmonics
        #self.srrf_data = srrf_data
        self.create_canvas()
        self.create_histograms()
        self.create_stack()
        self.histogram_fill()
        self.draw_histograms()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()
        

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(1, 3)
        
        self.canvas_NTCAP=TCanvas(
            'canvas_NTCAP', 'Frequency Histograms', 800, 800)
        self.canvas_NTCAP.Divide(1,4)
        
    def create_histograms(self):
        # experimental data
        globals()['h_tiqdata'] = TH1F('h_tiqdata', 'tiqdata', len(self.analyzers_data[:,0]),
                                      self.analyzers_data[0,0], self.analyzers_data[-1,0])
        self.histogram_list=np.array(['h_tiqdata'])
        #create histograms with each harmonic info
        for harmonic in self.harmonics:
            name='h srf '
            name=name+str(harmonic)
            globals()[name]=TH1F(name, name, int(len(self.simulated_data[:,0])/len(self.harmonics[:])), #for stacking change this to the same than the other
                                 self.simulated_data[0,1], self.simulated_data[-1,1])
            self.histogram_list=np.append(self.histogram_list,name)
                                                   
        globals()['h_NTCAP']=TH1F('h_NTCAP', 'NTCAPdata', len(self.NTCAP_data[:,0]),
                                  self.NTCAP_data[0,0], self.NTCAP_data[-1,0])
                    
    def create_stack(self):
        # overlaying histograms
        gStyle.SetPalette(kOcean)
        globals()['h_stack_complete'] = THStack()
        globals()['h_stack_sim'] = THStack()
        globals()['h_stack_NTCAP'] = THStack()
        
        globals()['h_stack_complete'].Add(globals()['h_tiqdata'])
        globals()['h_stack_NTCAP'].Add(globals()['h_NTCAP'])
        
        [h_stack_complete.Add(globals()[name]) for name in self.histogram_list if 'srf' in name]
        [globals()['h_stack_sim'].Add(globals()[name]) for name in self.histogram_list if 'srf' in name]
        [globals()['h_stack_NTCAP'].Add(globals()[name]) for name in self.histogram_list if 'srf' in name]
        # add to list of histograms:
        self.histogram_list=np.append(self.histogram_list,['h_stack_complete','h_stack_sim','h_stack_NTCAP'])
        
    def histogram_fill(self):
        # fill with experimental data:
        [globals()['h_tiqdata'].Fill(self.analyzers_data[i,0], self.analyzers_data[i,1])
         for i,element in enumerate(self.analyzers_data[:,0])]
        [globals()[name].Fill(sim[1],sim[2]) for name in self.histogram_list if 'srf' in name for h in name.split()
         if h.isdigit() for sim in self.simulated_data if int(h)==int(sim[0])]
        [globals()['h_NTCAP'].Fill(self.NTCAP_data[i,0], self.NTCAP_data[i,1])
         for i,element in enumerate(self.NTCAP_data[:,0])]
        
    def draw_histograms(self):
        r = TRandom()#random generator for the colors
        for i, histogram in enumerate(self.histogram_list):
            color = int(((113-51)*r.Rndm()+51))
            print(histogram)
            if 'tiq' in histogram:
                globals()[histogram].SetLineColor(color)
                self.canvas_main.cd(1)  # move to correct canvas
                globals()[histogram].Draw()
                self.canvas_main.Update()
            elif 'sim' in histogram:
                self.canvas_main.cd(2)  # move to correct canvas
                globals()[histogram].Draw('plc nostack')
                self.canvas_main.Update()
            elif 'complete' in histogram:
                self.canvas_main.cd(3)  # move to correct canvas
                globals()[histogram].Draw('plc nostack')
                globals()[histogram].GetXaxis().SetRangeUser(self.analyzers_data[0,0],self.analyzers_data[-1,0])
                self.canvas_main.Update()
            elif 'NTCAP' in histogram:
                x=int(len(self.NTCAP_data[:,0])/4)
                self.canvas_NTCAP.cd(1)
                globals()[histogram].Draw('plc nostack')
                globals()[histogram].GetXaxis().SetRangeUser(self.NTCAP_data[0,0],self.NTCAP_data[0+x*1,0])
                self.canvas_NTCAP.Modified()
                self.canvas_NTCAP.Update()
                input()
                self.canvas_NTCAP.cd(2)
                globals()[histogram].Draw('plc nostack')
                globals()[histogram].GetXaxis().SetRangeUser(self.NTCAP_data[0+x*1,0],self.NTCAP_data[0+x*2,0])
                self.canvas_NTCAP.Modified()
                self.canvas_NTCAP.Update()
                input()
                self.canvas_NTCAP.cd(3)
                globals()[histogram].Draw('plc nostack')
                globals()[histogram].GetXaxis().SetRangeUser(self.NTCAP_data[0+x*2,0],self.NTCAP_data[0+x*3,0])
                self.canvas_NTCAP.Modified()
                self.canvas_NTCAP.Update()
                input()
                self.canvas_NTCAP.cd(4)
                globals()[histogram].Draw('plc nostack')
                globals()[histogram].GetXaxis().SetRangeUser(self.NTCAP_data[0+3*x,0],self.NTCAP_data[-1,0])
                self.canvas_NTCAP.Modified()
                self.canvas_NTCAP.Update()
                input()

        #self.canvas_main.Update()
        #self.canvas_main.SaveAs('histogram_plot.pdf')
        #self.canvas_NTCAP.Update()
        input()
        self.canvas_NTCAP.SaveAs('NTCAP_plot.pdf')
    
def test():
    import importdata
    mydata = importdata.ImportData('data/410-j','data/tdms-example')
    mycanvas = CreateGUI(mydata.analyzer_data, mydata.simulated_data,
                         mydata.NTCAP_data, mydata.harmonics)


if __name__ == '__main__':
    test()
