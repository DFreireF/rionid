from ROOT import *


class Canvas():
    def __init__(self):
        pass

    def create_histograms(self, freq_min, freq_max):
        freq_center = int(0)
        freq_tl = 243.2712156  # check what this value should be, prob should be variable
        nbins = int(1e2)  # placeholder value, should be variable

        #note: TH1F('name', 'title', nbinsx, xlow, xup)

        # simulated histogram? old name: hSim
        h_sim = TH1F('h_sim', 'Simulated Something', int(200e3), 400, 700)
        # hFFt_px_ref (reference?)
        h_ref = TH1F('h_ref', 'Simulated',
                     nbins, (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)
        # hSRF Histogram of simulated revolution frequency
        h_simfreq = TH1F('h_simfreq', 'FFT_reference',
                         nbins, (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)
        # hSRF Histogram of simulated revolution frequency
        h_rel_simfreq = TH1F('h_rel_simfreq', 'Simulated Revolution Frequency',
                             nbins, (freq_center+freq_min)/freq_tl, (freq_center+freq_max)/freq_tl)

        self.hist_list = [h_sim, h_ref, h_simfreq, h_rel_simfreq]

# ================ old and not working ==================
# def test():
#     mycanvas = Canvas()
#     mycanvas.create_histograms(freq_min, freq_max)

#     canvas_1 = TCanvas('canvas_1', 'Main Plot',600,600)
#     for histogram in mycanvas.hist_list:
#         histogram.FillRandom('gaus', 10000)
#         histogram.Draw()
# =======================================================

def test():
    freq_min = 10
    freq_max = 280
    mycanvas=Canvas()
    mycanvas.create_histograms(freq_min,freq_max)
    
    for histogram in mycanvas.hist_list:    
        histogram.FillRandom('gaus', 10000)
        
    return mycanvas


if __name__ == '__main__':
    canvas_1 = TCanvas('canvas_1', 'Main Plot',600,600)
    mycanvas = test()
    for histogram in mycanvas.hist_list:
        histogram.Draw()
        
    canvas_1.Update()
    
    # prevent canvas from closing in pyroot:
    gApplication.Run()
