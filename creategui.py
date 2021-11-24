from ROOT import *


class CreateGUI():
    def __init__(self, frequency_data, power_data,
                 frequency_sim, power_sim, srrf_data, fcenter):
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
        self.set_formatting()
        self.draw_histograms()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(1, 3)

    def create_histograms(self):
        # real data
        self.h_tiqdata = TH1F('h_tiqdata', 'tiqdata', len(self.frequency_data),
                              self.f_min(self.fcenter, self.frequency_data),
                              self.f_max(self.fcenter, self.frequency_data))
        # simulated data
        self.h_simdata = TH1F('h_simdata', 'simdata', len(self.frequency_sim),
                              self.f_min(self.fcenter, self.frequency_sim),
                              self.f_max(self.fcenter, self.frequency_sim))

        self.hist_list = [self.h_tiqdata, self.h_simdata]

    def create_stack(self):
        self.stack_test = THStack()
        self.stack_test.Add(self.h_tiqdata)
        self.stack_test.Add(self.h_simdata)

        self.hist_list.append(self.stack_test)

    def histogram_fill(self):
        # fill tiqdata:
        for i, element in enumerate(self.frequency_data):
            self.h_tiqdata.Fill(
                self.frequency_data[i] + self.fcenter, self.power_data[i])

        # filling with simulated data:
        for i, element in enumerate(self.frequency_sim):
            self.h_simdata.Fill(self.frequency_sim[i], self.power_sim[i])

    def draw_histograms(self):
        linecolors = [kRed, kBlue, kGreen]

        for i, histogram in enumerate(self.hist_list):
            self.canvas_main.cd(i+1)
            if i == 2:
                self.stack_test.SetTitle('Histogram Stack')
                self.stack_test.Draw("nostack")
            else:
                histogram.SetLineColor(linecolors[i])
                histogram.Draw()

        self.canvas_main.Update()
        # self.canvas_main.SaveAs("p.pdf")

    @staticmethod
    def f_min(center, data):
        return center+data[0]

    @staticmethod
    def f_max(center, data):
        return center+data[-1]

    def set_formatting(self):
        pass


def test():
    print('Please run pysimtof.py to pass data')
    # mycanvas = CreateGUI(10, 10, 10, 10, 10)


if __name__ == '__main__':
    test()
