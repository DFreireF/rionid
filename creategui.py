from ROOT import *


class CreateGUI():
    def __init__(self, frequency_data, power_data,
                 frequency_sim, power_sim, srrf_data, fcenter):
        # setting object variables:
        self.frequency_data = frequency_data
        self.power_data = power_data
        self.frequency_sim = frequency_sim
        self.power_sim = power_sim
        self.srrf_data = srrf_data
        self.fcenter = fcenter

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

    def create_histograms(self):
        # experimental data
        self.h_tiqdata = TH1F('h_tiqdata', 'tiqdata', len(self.frequency_data),
                              self.f_min(self.fcenter, self.frequency_data),
                              self.f_max(self.fcenter, self.frequency_data))

        # simulated data
        self.h_simdata = TH1F('h_simdata', 'simdata', len(self.frequency_sim),
                              self.f_min(self.fcenter, self.frequency_sim),
                              self.f_max(self.fcenter, self.frequency_sim))

        self.hist_list = [self.h_tiqdata, self.h_simdata]

    def create_stack(self):
        # overlaying histograms
        self.h_stack = THStack()
        self.h_stack.Add(self.h_tiqdata)
        self.h_stack.Add(self.h_simdata)

        self.hist_list.append(self.h_stack)

    def histogram_fill(self):
        # fill with experimental data:
        for i, element in enumerate(self.frequency_data):
            self.h_tiqdata.Fill(
                self.frequency_data[i] + self.fcenter, self.power_data[i])

        # filling with simulated data:
        for i, element in enumerate(self.frequency_sim):
            self.h_simdata.Fill(self.frequency_sim[i], self.power_sim[i])
            #Nx_SRF=self.h_simdata.GetXaxis().FindBin(self.frequency_sim[i])
            #self.h_simdata.SetBinContent(Nx_SRF,self.power_sim[i])
            
    def draw_histograms(self):
        linecolors = [kRed, kBlue, kGreen]

        for i, histogram in enumerate(self.hist_list):
            self.canvas_main.cd(i+1)  # move to correct canvas
            # drawing h_stack:
            if i+1 == 3:
                histogram.SetTitle('Histogram Stack')
                histogram.Draw("nostack")  # "nostack" overlays histograms
                histogram.SetMaximum(2)
                histogram.Draw("nostack")  # "nostack" overlays
            # drawing other histograms:
            else:
                histogram.SetLineColor(linecolors[i])
                histogram.Draw()
                if i+1 == 2:  # changing range
                    pass
                    # for range of tiqdata:
                    # histogram.GetXaxis().SetLimits(
                    #     self.h_tiqdata.GetXaxis().GetXmin(),self.h_tiqdata.GetXaxis().GetXmax())

                    # for arbitrary range:
                    # .SetRangeUser not working on this histogram for some reason
                    # histogram.Draw()

        self.canvas_main.Update()
        # self.canvas_main.SaveAs("histogram_plot.pdf")

    @staticmethod
    def f_min(center, data):  # find minimum frequency
        return center+data[0]

    @staticmethod
    def f_max(center, data):  # find maximum frequency
        return center+data[-1]


def test():
    import importdata
    mydata = importdata.ImportData('data/410-j')
    mycanvas = CreateGUI(mydata.ff, mydata.pp, mydata.SRF,
                         mydata.yield_data_normalised,
                         mydata.SRRF, mydata.fcenter)


if __name__ == '__main__':
    test()
