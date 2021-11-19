from ROOT import *


class Canvas():
    def __init__(self):

        # (eventually will be input)
        self.freq_min = 10
        self.freq_max = 280

        self.create_canvas()
        self.create_histograms(self.freq_min, self.freq_max)
        self.histogram_fill()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(2, 2)
        print('Canvas created.')

    def create_histograms(self, freq_min, freq_max):
        self.freq_center = 0
        self.freq_tl = 243.2712156  # check what this value should be, prob should be variable
        self.nbins = int(1e2)  # placeholder value, should be variable

        # note: TH1F('name', 'title', int: nbinsx, xlow, xup)
        
        # simulated histogram? old name: hSim
        h_sim = TH1F('h_sim', 'Simulated Something', int(200e3), 400, 700)
        # hFFt_px_ref (reference?)
        h_ref = TH1F('h_ref', 'Simulated', self.nbins,
                     (self.freq_center + freq_min)/self.freq_tl,
                     (self.freq_center+freq_max)/self.freq_tl)
        # hSRF Histogram of simulated revolution frequency
        h_simfreq = TH1F('h_simfreq', 'FFT_reference', self.nbins,
                         (self.freq_center+freq_min)/self.freq_tl,
                         (self.freq_center+freq_max)/self.freq_tl)
        # hSRF Histogram of simulated revolution frequency
        h_rel_simfreq = TH1F('h_rel_simfreq', 'Sim. Rev. Freq.', self.nbins,
                             (self.freq_center+freq_min)/self.freq_tl,
                             (self.freq_center+freq_max)/self.freq_tl)

        self.hist_list = [h_sim, h_ref, h_simfreq, h_rel_simfreq]
        print('histograms created')

    def histogram_fill(self):
        # filling with data, placeholder method
        for i, histogram in enumerate(self.hist_list):
            self.canvas_main.cd(i+1)
            histogram.FillRandom('gaus', 10000)
            histogram.Draw()
            print(f'filling histogram {i+1}')
            
        self.canvas_main.Update()
        print('Histograms filled.')


def test():
    mycanvas = Canvas()

if __name__ == '__main__':
    test()
    # prevent canvas from closing in pyroot:
    gApplication.Run()
