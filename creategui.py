from ROOT import *
import numpy as np

class CreateGUI():
    def __init__(self, analyzers_data,
                  simulated_data, fcenter,harmonics):
        # setting object variables: add NTCAP_data,
        
        self.frequency_data = analyzers_data[:,0]
        self.power_data = analyzers_data[:,1]
        
        self.frequency_sim = simulated_data[:,1]
        self.power_sim= simulated_data[:,2]
        self.harmonics=harmonics
        
        #self.srrf_data = srrf_data
        self.fcenter = fcenter

        self.create_canvas()
        self.create_histograms()
       # self.create_stack()

        self.histogram_fill()
        self.draw_histograms()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(1, 3)
        
        #self.canvas_NTCAP=TCanvas(
        #    'canvas_NTCAP', 'Frequency Histograms', 800, 800)
        #self.canvas_NTCAP.Divide(1,4)
        
    def create_histograms(self):
        # experimental data
        self.h_tiqdata = [TH1F('h_tiqdata', 'tiqdata', len(self.frequency_data),
                              self.f_min(self.fcenter, self.frequency_data),
                                        self.f_max(self.fcenter, self.frequency_data))]

        # simulated data, list with the different harmonic's sim data 
        #self.h_simdata = [TH1F('h_simdata'+str(k), 'simdata'+str(k), len(self.frequency_sim),
        #                      self.frequency_sim[],
        #                       self.f_max(self.fcenter, self.frequency_sim)) for k in range(0,len(self.harmonics))]
        name='h_srf_'
        for sim in self.simulated_data:
            if sim[0]==self.harmonics[0]:
                self.name+str(self.harmonics[0])=[TH1F(name+str(self.harmonics[0]),
                        len(self.simulated_data)/len(self.harmonics), self.simulated_data[0,1],
                                                                      self.simulated_data[-1,0])]
            elif sim[0]==self.harmonics[1]:
                self.(name+str(self.harmonics[1]))=[TH1F(name+str(self.harmonics[1]),
                        len(self.simulated_data)/len(self.harmonics), self.simulated_data[0,1],
                                                                      self.simulated_data[-1,0])]
            elif sim[0]==self.harmonics[2]:
                self.(name+str(self.harmonics[2]))=[TH1F(name+str(self.harmonics[2]),
                        len(self.simulated_data)/len(self.harmonics), self.simulated_data[0,1],
                                                                      self.simulated_data[-1,0])]                       
                                                   
        #self.h_NTCAP=TH1F('h_NTCAP', 'NTCAPdata', len(self.f_data_NTCAP),
        #                      self.f_min(self.fcenter, self.f_data_NTCAP),
        #                      self.f_max(self.fcenter, self.f_data_NTCAP))
        
            
        #def create_stack(self):
        #    # overlaying histograms
        #    self.h_stack = THStack()
        #    self.h_stack.Add(self.h_tiqdata[0])
        #    [self.h_stack.Add(self.h_simdata[k]) for k,harmonic in enumerate(self.harmonics)]
	#    self.h_stack_sim = THStack()
        #    [self.h_stack_sim.Add(self.h_simdata[k]) for k,harmonic in enumerate(self.harmonics)]
        #    # add to list of histograms:
        #    self.hist_list.append(self.h_stack)
        #
        
    def histogram_fill(self):
        # fill with experimental data:
        [self.h_tiqdata[0].Fill(self.frequency_data[i] + self.fcenter, self.power_data[i])
         for i,element in enumerate(self.frequency_data)]
        name='h_srf_'
        for sim self.simulated_data:
            if sim[0]==self.harmonics[0]:
                self.(name+str(self.harmonics[0])).Fill(sim[1], sim[2])
            elif sim[0]==self.harmonics[1]:
                self.(name+str(self.harmonics[0])).Fill(sim[1], sim[2])
            elif sim[0]==self.harmonics[2]:
                self.(name+str(self.harmonics[0])).Fill(sim[1], sim[2])
                
        # filling with simulated data:
        #[self.h_simdata[k].Fill(self.frequency_sim[i], self.power_sim[i])
        # for k,harmonics in enumerate(self.harmonics) for i, element in enumerate(self.frequency_sim)]

    def draw_histograms(self):
        self.hist_list = [self.h_tiqdata[0],self.h_srf_124,self.h_srf_125,self.h_srf_126]
        r = TRandom()#random generator for the colors
        for i, histogram in enumerate(self.hist_list):
            color = int(((113-51)*r.Rndm()+51))
            histogram.SetLineColor(color)
            if i==0:
                self.canvas_main.cd(1)  # move to correct canvas
                histogram.Draw()
                self.canvas_main.cd(3)
                histogram.Draw('histo same')
            else:
                self.canvas_main.cd(2)
                histogram.Draw('histo same')
                self.canvas_main.cd(3)
                histogram.Draw('histo same')
                
            
            # drawing h_stack:
            #if i+1 == 3:
            #    histogram.SetTitle('Histogram Stack')
            #    histogram.Draw("nostack")  # "nostack" overlays histograms
            #    histogram.SetMaximum(2)
            #    histogram.SetLineColor(color)
            #    histogram.Draw("nostack")  # "nostack" overlays
                
            # drawing other histograms:
            #else:
            #    histogram.SetLineColor(color)
            #    histogram.Draw()

        self.canvas_main.Update()
        self.canvas_main.SaveAs("histogram_plot.pdf")

    @staticmethod
    def f_min(center, data):  # find minimum frequency
        return center+data[0]

    @staticmethod
    def f_max(center, data):  # find maximum frequency
        return center+data[-1]


def test():
    import importdata
    mydata = importdata.ImportData('data/410-j')
    mycanvas = CreateGUI(mydata.analyzer_data, mydata.simulated_data,
                         mydata.fcenter, mydata.harmonics)


if __name__ == '__main__':
    test()
