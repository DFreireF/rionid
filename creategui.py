from ROOT import *


class CreateGUI():
    def __init__(self, frequency_data,fcenter, power_data,
                 srf_data,srf_yield, srrf_data):
        self.frequency_data = frequency_data
        self.fcenter=fcenter
        self.power_data = power_data
        self.srf_data = srf_data
        self.srf_yield=srf_yield
        self.srrf_data=srrf_data
        #self.freq_min = frequency_min
        #self.freq_max = frequency_max

        self.create_canvas()
        self.create_histograms()
        self.histogram_fill()
        # self.create_latex_labels()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(1, 4)
        
    def f_min(self,center,data):
        return (data[0]+center)/center
    
    def f_max(self,center,data):
        return (data[-1]+center)/center
    
    def create_histograms(self):
        #self.freq_center = 0
        #self.freq_tl = 243.2712156  # check what this value should be, prob should be variable

        # setting normalised histogram range:
        #f_min = self.fcenter +self.frequency_data[0]#(self.freq_center + self.freq_min)/self.freq_tl
        #f_max = self.fcenter +self.frequency_data[-1]#(self.freq_center + self.freq_max)/self.freq_tl
        # hSim simulated histogram?
        h_sim = TH1F('h_sim', 'Experimental data, all of it', len(self.frequency_data),
                     self.f_min(self.fcenter,self.frequency_data), self.f_max(self.fcenter,self.frequency_data))
        # hFFt_px_ref (reference?)
        h_ref = TH1F('h_ref', 'Simulated Reference', len(self.srf_data),
                     self.f_min(self.fcenter,self.srf_data), self.f_max(self.fcenter,self.srf_data))
        # hSRF Histogram of simulated revolution frequency
        h_simfreq = TH1F('h_simfreq', 'FFT_reference', len(self.frequency_data),
                     self.f_min(self.fcenter,self.frequency_data), self.f_max(self.fcenter,self.frequency_data))
        # hSRRF Histogram of simulated relative revolution frequency
        h_rel_simfreq = TH1F('h_rel_simfreq', 'Sim. Rev. Freq.', len(self.frequency_data),
                     self.f_min(1,self.srrf_data), self.f_max(1,self.srrf_data))

        self.hist_list = [h_sim, h_ref, h_simfreq, h_rel_simfreq]

    def histogram_fill(self):
        # # filling with data, placeholder method
        # for i, histogram in enumerate(self.hist_list):
        #     self.canvas_main.cd(i+1)
        #     histogram.FillRandom('gaus', 1000)
        #     histogram.Draw()
        # self.canvas_main.Update()

        # filling with simulated data:\
        for i, histogram in enumerate(self.hist_list):
            self.canvas_main.cd(i+1)
            if i!=1:
                for j,element in enumerate(self.frequency_data):
                    histogram.Fill(self.frequency_data[j]+self.fcenter,
                                   self.power_data[j])
            elif i==1:
                for j,element in enumerate(self.srf_data):
                    histogram.Fill(self.srf_data[j], self.srf_yield[j])
            elif i==3:
                for j,element in enumerate(self.srrf_data):
                    histogram.Fill(self.srrf_data[j], self.srf_yield[j])
                    
            histogram.Draw()
            
        self.canvas_main.Update()
        self.canvas_main.SaveAs("p.pdf")

def test():
    mycanvas = CreateGUI(10, 10, 10, 10, 10)


if __name__ == '__main__':
    test()
