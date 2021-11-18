from ROOT import *


class CanvasFormat():
    def __init__(self):
        pass

    def create_histograms(self, freq_min, freq_max):
        freq_center = 0
        freq_tl = 243.2712156  # check what this value should be, prob should be variable

        #note: TH1F('name', 'title', nbinsx, xlow, xup)

        # simulated histogram? old name: hSim
        h_sim = TH1F('h_sim', 'Simulated Something', 200e3, 400, 700)

        # hFFt_px_ref (reference?)
        h_ref = TH1F('h_ref', 'Simulated',
                     (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)

        # hSRF Histogram of simulated revolution frequency
        h_simfreq = TH1F('h_simfreq', 'FFT_reference',
                         (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)

        # hSRF Histogram of simulated revolution frequency
        h_rel_simfreq = TH1F('h_rel_simfreq', 'Simulated Revolution Frequency',
                             (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)

        self.hist_list = [h_sim, h_ref, h_simfreq, h_rel_simfreq]


if __name__ == '__main__':
    try:
        pass
    except:
        raise
