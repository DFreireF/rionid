from ROOT import *


class CreateGUI():
    def __init__(self):
        # (eventually will be input)
        self.freq_min = 10
        self.freq_max = 280

        self.create_canvas()
        self.create_histograms()
        self.histogram_fill()
        self.create_latex_labels()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(2, 2)

    def create_histograms(self):
        self.freq_center = 0
        self.freq_tl = 243.2712156  # check what this value should be, prob should be variable
        self.nbins = int(1e2)  # placeholder value, should be variable
        # setting normalised histogram range:
        normalised_min = (self.freq_center + self.freq_min)/self.freq_tl
        normalised_max = (self.freq_center + self.freq_max)/self.freq_tl

        # hSim simulated histogram?
        h_sim = TH1F('h_sim', 'Simulated Histogram', int(200e3), 400, 700)
        # hFFt_px_ref (reference?)
        h_ref = TH1F('h_ref', 'Simulated Reference', self.nbins,
                     normalised_min, normalised_max)
        # hSRF Histogram of simulated revolution frequency
        h_simfreq = TH1F('h_simfreq', 'FFT_reference', self.nbins,
                         normalised_min, normalised_max)
        # hSRRF Histogram of simulated relative revolution frequency
        h_rel_simfreq = TH1F('h_rel_simfreq', 'Sim. Rev. Freq.', self.nbins,
                             normalised_min, normalised_max)

        self.hist_list = [h_sim, h_ref, h_simfreq, h_rel_simfreq]

    def histogram_fill(self):
        # filling with data, placeholder method
        for i, histogram in enumerate(self.hist_list):
            self.canvas_main.cd(i+1)
            histogram.FillRandom('gaus', 1000)
            histogram.Draw()
        self.canvas_main.Update()


def test():
    mycanvas = CreateGUI()


if __name__ == '__main__':
    test()
