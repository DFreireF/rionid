from ROOT import *
import numpy as np


class CreateGUI():
    def __init__(self, analyzers_data,
                  simulated_data, NTCAP_data,harmonics):
        # setting object variables: add NTCAP_data,
        self.analyzers_data = analyzers_data #frec =analyzers_data[:,0]   power =analyzers_data[:,1]
        self.simulated_data=simulated_data # harmonic= simulated_data[:,0] frec=simulated_data[:,1] power=simulated_data[:,2], ion name=[:,3]
        self.NTCAP_data=NTCAP_data
        self.harmonics=harmonics
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
        self.h_tiqdata= TH1F('h_tiqdata', 'tiqdata', len(self.analyzers_data[:,0]),
                                      self.analyzers_data[0,0], self.analyzers_data[-1,0])
        self.histogram_dict=dict()
        self.histogram_dict['h_tiqdata']=self.h_tiqdata
        #create histograms with each harmonic info
        for harmonic in self.harmonics:
            name=f'h srf {harmonic}'
            self.histogram_dict[name]=TH1F(name, name, int(len(self.simulated_data[:,1])/len(self.harmonics[:])),
                                           self.simulated_data[0,1], self.simulated_data[-1,1])
        #histo with NTCAP info                                          
        self.h_NTCAP=TH1F('h_NTCAP', 'NTCAPdata', len(self.NTCAP_data[:,0]),
                                  self.NTCAP_data[0,0], self.NTCAP_data[-1,0])
                    
    def create_stack(self):
        # overlaying histograms
        self.h_stack_complete = THStack()
        self.h_stack_sim = THStack()
        self.h_stack_NTCAP = THStack()
        
        self.h_stack_complete.Add(self.h_tiqdata)
        self.h_stack_NTCAP.Add(self.h_NTCAP)
        
        [self.h_stack_complete.Add(self.histogram_dict[name]) for name in self.histogram_dict if 'srf' in name]
        [self.h_stack_sim.Add(self.histogram_dict[name]) for name in self.histogram_dict if 'srf' in name]
        [self.h_stack_NTCAP.Add(self.histogram_dict[name]) for name in self.histogram_dict if 'srf' in name]

        self.histogram_dict['h_stack_complete']=self.h_stack_complete
        self.histogram_dict['h_stack_sim']=self.h_stack_sim
        self.histogram_dict['h_stack_NTCAP']=self.h_stack_NTCAP
        
    def histogram_fill(self):
        # fill analyzers data:
        [self.h_tiqdata.Fill(self.analyzers_data[i,0], self.analyzers_data[i,1])
         for i,element in enumerate(self.analyzers_data[:,0])]
        # fill with simulated data
        [self.histogram_dict[name].Fill(sim[1],0.9) for name in self.histogram_dict if 'srf' in name for h in name.split()
         if h.isdigit() for sim in self.simulated_data if int(h)==int(sim[0])]
        # fill with NTCAP data
        [self.h_NTCAP.Fill(self.NTCAP_data[i,0], self.NTCAP_data[i,1])
         for i,element in enumerate(self.NTCAP_data[:,0])]
    
    def draw_histograms(self):
        self.Labels=dict()

        for i, histogram in enumerate(self.histogram_dict):
            #plotting tiq histo
            if 'tiq' in histogram:
                self.canvas_main.cd(1)  # move to correct canvas
                gStyle.SetPalette(kDarkRainBow)
                self.histogram_dict[histogram].Draw('plc')
                self.canvas_main.Update()
                
            #plotting data with the simulated harmonic
            elif 'sim' in histogram:
                self.canvas_main.cd(2)  # move to correct canvas
                gStyle.SetPalette(kDarkRainBow)
                gStyle.SetErrorX(0)
                self.histogram_dict[histogram].Draw('l plc nostack')
                gPad.BuildLegend(0.75,0.75,0.95,0.95)
                self.canvas_main.Update()
                
            #plotting data with the harmonics + tiq data
            elif 'complete' in histogram:
                self.canvas_main.cd(3)  # move to correct canvas
                gStyle.SetPalette(kDarkRainBow)
                self.histogram_dict[histogram].Draw()
                self.histogram_dict[histogram].GetXaxis().SetRangeUser(self.simulated_data[0,1],self.simulated_data[-1,1])
                self.histogram_dict[histogram].Draw('plc nostack')
                self.canvas_main.Update()
                
            #plotting data with NTCAP + simulated harmonics
            elif 'NTCAP' in histogram:
                x=int(len(self.NTCAP_data[:,0])/4) #dividing range in 4
                for j in range(0,4):
                    self.canvas_NTCAP.cd(j+1)
                    gStyle.SetPalette(kDarkRainBow)
                    name='copy_NTCAP'+str(j)
                    self.name=self.histogram_dict[histogram].Clone()
                    self.name.Draw()
                    self.name.GetXaxis().SetRangeUser(self.NTCAP_data[x*j,0],self.NTCAP_data[x*(j+1)-1,0])
                    self.name.Draw('plc nostack')
                    self.canvas_NTCAP.Update()
                    self.create_labels(self.NTCAP_data[x*j,0],self.NTCAP_data[x*(j+1)-1,0])
                    
        #saving histos in pdf
        self.canvas_main.SaveAs('histogram_plot.pdf')
        self.canvas_NTCAP.SaveAs('NTCAP_plot.pdf')
 #       for i,name in enumerate(self.histogram_dict):
            
#       =self.histogram_dict[name].Clone()
#   for sim in self.simulated_data:
#       aux= a.GetXaxis().FindBin(sim[1])
#       a.SetBinContent(aux,1.5)
          
    def create_labels(self,range_min,range_max):
        for name in self.histogram_dict:
            if 'srf' in name:
                for h in name.split():
                    if h.isdigit():
                        for sim in self.simulated_data:
                            if int(h)==int(sim[0]) and sim[1]<=range_max and sim[1]>=range_min:
                                name=f'A:{sim[3]}Z:{sim[4]}Q:+{sim[5]}har:{h}'
                                if sim[3]==72.0: print('hola')
                                self.Labels[name] = TLatex(sim[1], sim[2], name)
                                self.label_format(self.Labels[name])
                                self.canvas_NTCAP.Update()

    def label_format(self, label):
        label.SetTextFont(110)
        label.SetTextSize(0.055)
        label.SetTextAngle(90)
        label.SetTextColor(3)
        label.SetLineWidth(1)
        label.Draw('nostack')
        
def test():
    import importdata
    mydata = importdata.ImportData('data/410-j','data/tdms-example')
    mycanvas = CreateGUI(mydata.analyzer_data, mydata.simulated_data,
                         mydata.NTCAP_data, mydata.harmonics)


if __name__ == '__main__':
    test()
