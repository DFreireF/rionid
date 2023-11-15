from ROOT import *
from barion.patternfinder import *
from .pypeaks import *
from .importdata import *
from datetime import datetime


class CreateGUI(object):
    '''
    View (MVC)
    '''
    def __init__(self, ref_ion, ion_names, ndivs, yield_option, show):
        
        self.ref_ion = ref_ion
        self.ion_names = ion_names
        self.ndivs = ndivs
        self.idx_case = yield_option
        self.show = show

    def _view(self, exp_data, simulated_data_dict, filename = 'Spectrum', out = ''):

        self.create_canvas()
        self.create_histograms(exp_data, simulated_data_dict, filename)
        self.histogram_fill()      
        self.set_xranges()
        self.set_yscales()
        self.create_stack(simulated_data_dict)
        self.draw_histograms()
        gSystem.ProcessEvents()
        
        if self.show:
            gApplication.Run()

        else:
            date_time = datetime.now().strftime('%Y.%m.%d_%H.%M.%S')
            info_name = f'{out}{filename}{date_time}'
            self.save_root(info_name)
        
    def create_canvas(self):
        
        # Create a canvas
        self.canvas_main = TCanvas('canvas', 'Frequency Histograms', 1500, 1500)
        self.canvas_main.SetFillColor(0)
        self.canvas_main.Divide(1, self.ndivs)
        self.canvas_peaks = TCanvas('canvas_peaks_srf', 'canvas_peaks_srf', 500, 500)

    def create_histograms(self, exp_data, simulated_data_dict, filename):
        
        self.histogram_dict = {'exp_data': np.array([TH1D('h_exp_data', filename, len(exp_data[:,0]),
                                                 exp_data[:, 0].min(), exp_data[:, 0].max()), exp_data], dtype = 'object').T,
                            **{f'srf{key}': np.array([TH1F(f'srf{key}', f'srf{key}', int(2e6),
                                                       float(min(simulated_data_dict[key][:, 0])), float(max(simulated_data_dict[key][:, 0]))), simulated_data_dict[key][:,:2].astype(np.float)], dtype = 'object').T for key in simulated_data_dict}
                            }
        list(map(lambda x: self.histogram_format(self.histogram_dict[x[1]][0], x[0], x[1]), enumerate(self.histogram_dict)))


    def histogram_fill(self):
        for key in self.histogram_dict:
            xbin = (self.histogram_dict[key][0].GetXaxis().FindBin(frec) for frec in self.histogram_dict[key][1][:, 0])
            values = (self.histogram_dict[key][1][i, 1] for i in range(self.histogram_dict[key][1].shape[0]))
            [self.histogram_dict[key][0].AddBinContent(x, v) for x, v in zip(xbin, values)]
            
    def set_xranges(self):
        
        xrange_divs = {}
        histogram = self.histogram_dict['exp_data'][0]
        n_bins_x = histogram.GetNbinsX()
        x = n_bins_x // self.ndivs
        for j in range(self.ndivs):
            xrange_divs[j] = np.array([x*j+1, x*(j+1)])
        self.xrange_divs = xrange_divs
           
    def set_yscales(self):
        self.ranges = []
        exp_data_hist = self.histogram_dict['exp_data'][0]
        exp_data_xaxis = exp_data_hist.GetXaxis()
        exp_data_yaxis = exp_data_hist.GetYaxis()
        
        # Loop over xrange_divs
        for x in self.xrange_divs:
            min_div, max_div = map(int, self.xrange_divs[x])
            exp_data_xaxis.SetRange(min_div, max_div)
            minimum = exp_data_hist.GetMinimum()
            maximum = exp_data_hist.GetMaximum()
        
            # Check if y-axis is logarithmic
            if minimum <= 0:
                self.logy = False
        
            self.ranges.append((maximum, min_div, max_div, minimum))
        
            # Loop over keys in histogram_dict
            for key in self.histogram_dict:
                if 'srf' in key:
                    srf_hist = self.histogram_dict[key][0]
                    srf_array = self.histogram_dict[key][1]
        
                    # Filter out frequencies outside of the xrange_divs range
                    srf_mask = (srf_array[:, 0] >= exp_data_xaxis.GetBinCenter(min_div)) & (srf_array[:, 0] <= exp_data_xaxis.GetBinCenter(max_div))
                    srf_filtered = srf_array[srf_mask]
        
                    # Loop over filtered frequencies and update histogram bin contents
                    for freq, value in srf_filtered:
                        xbin = srf_hist.FindBin(freq)
                        if self.idx_case == 0:
                            srf_hist.SetBinContent(xbin, maximum)
                        else:
                            scaled = srf_hist.GetBinContent(xbin) * maximum / srf_hist.GetMaximum()
                            srf_hist.SetBinContent(xbin, scaled)

        
    def create_stack(self, simulated_data_dict):
        
        self.exp_dict = dict()
        self.stack = dict()

        for j in range (0, self.ndivs):
           name = f'stack{j}'
           self.exp_dict[name] = self.histogram_dict['exp_data'][0].Clone()
           self.stack[name] = np.array([THStack()])
           [self.stack[name][0].Add(self.histogram_dict[key][0]) for key in self.histogram_dict if 'srf' in key]
           
    def set_xy_ranges(self, stack, rang):
        for h in [self.exp_dict[stack], self.stack[stack][0]]:
            h.SetMinimum(rang[3] / 1.1)
            h.SetMaximum(rang[0] * 2.2)
            h.GetXaxis().SetRange(rang[1], rang[2])
    
    def draw_histograms(self):
        
        self.labels = dict()
        
        self.legend = TLegend(0.9, 0.6, 0.99, 0.99, 'blNDC')
        self.set_legend(self.legend)
        
        for j, stack in enumerate(self.stack):
            
            self.canvas_main.cd(j + 1)
            if self.logy: self.canvas_main.cd(j + 1).SetLogy()
            
            self.exp_dict[stack].Draw('hist')
            self.stack[stack][0].Draw('same nostack')
            
            self.set_xy_ranges(stack, self.ranges[j])
            self.stack_format(self.stack[stack][0])
                        
        for color, key in enumerate(self.histogram_dict):
            self.legend.AddEntry(self.histogram_dict[key][0], f'{key}', 'l')
            if 'srf' in key:
                self.create_labels(key, color + 1)
                
        self.canvas_main.cd(1)
        self.legend.Draw('same')
        self.canvas_main.Update()
        
    def set_legend(self, legend):
        
        legend.SetHeader('Schottky Spectra', 'C')
        legend.SetLineColor(1)
        legend.SetLineStyle(1)
        legend.SetBorderSize(1)
        legend.SetLineWidth(1)
        legend.SetFillStyle(1)
        
    def stack_format(self, stack):
        
        stack.GetXaxis().SetTitle('Frequence [Hz]')
        stack.GetXaxis().CenterTitle(True)
        stack.GetXaxis().SetLabelFont(40)
        stack.GetXaxis().SetLabelSize(0.07)
        stack.GetXaxis().SetTitleSize(0.1)
        stack.GetXaxis().SetTitleFont(40)
        stack.GetXaxis().SetNdivisions(520)
        stack.GetYaxis().SetTitle('Amplitude')
        stack.GetYaxis().CenterTitle(True)
        stack.GetYaxis().SetLabelFont(42)
        stack.GetYaxis().SetLabelSize(0.07)
        stack.GetYaxis().SetTitleSize(0.10)
        stack.GetYaxis().SetTitleOffset(0.3)
        stack.GetYaxis().SetTitleFont(42)

    def histogram_format(self, histogram, color, name):
        
        if 'exp' in name:
            histogram.SetLineColor(4)
            histogram.SetMarkerStyle(1)

        else:            
            if color + 1 == 4: color = 224
            if color + 1 == 5: color = 94
            histogram.SetLineColor(color + 1)
            histogram.SetFillColor(color + 1)
        histogram.SetLineStyle(1)
        histogram.SetStats(0)

    def create_labels(self, key, color):
        xpeaks = self.set_peaks(key)
        self.set_peak_labels(xpeaks, key, color)

    def set_peaks(self, key):
        
        self.canvas_peaks.cd()
        peaks = FitPeaks(2000, self.histogram_dict[key][0].Clone(), False) # in Search set options nodraw to not draw it. #200 peaks to fit
        xpeaks = peaks.peak_finding()
        self.canvas_peaks.Update()
        return xpeaks
    
    def set_peak_labels(self, xpeaks, key, color):
        [self.set_peak_label(xpeak, key, color) for xpeak in xpeaks]

    def set_peak_label(self, xpeak, key, color):
        
        pattern = PatternFinder(self.histogram_dict[key][1][:,0], [xpeak])
        tmp = pattern.get_first_match_index()
        
        frec = self.histogram_dict[key][1][tmp,0]
        xlabel = self.histogram_dict[key][0].GetXaxis().FindBin(frec)
        ylabel = self.histogram_dict[key][0].GetBinContent(xlabel)
        
        ion_name = self.ion_names[tmp]
        label_name = f'{ion_name}{key}'
        
        refion = self.ref_ion in ion_name
        self.labels[label_name] = np.array([TLatex(frec, ylabel, ion_name), frec, refion]).T
        if self.canvas_cd(frec, index):
            self.draw_label(label_name, color)

    def draw_label(self, label, color):
        
        self.label_format(self.labels[label][0], self.labels[label][2], color)
        self.plotted_labels = np.array([self.labels[label]])
    
    def canvas_cd(self, frec, index):
        
        for key in self.xrange_divs:
            if (frec >= self.histogram_dict['exp_data'][0].GetBinCenter(int(self.xrange_divs[key][0]))) and (frec <= self.histogram_dict['exp_data'][0].GetBinCenter(int(self.xrange_divs[key][1]))):
                self.canvas_main.cd(int(key) + 1)
                return True
        return False
         
    def label_format(self, label, refion, color):
        label.SetLineColor(0)
        label.SetTextFont(110)
        label.SetTextSize(0.055)
        label.SetTextAngle(90)
        if color == 4: color = 225 #for not using the blue for this (since it is the data color)
        if color == 5: color = 95 #to avoid yellow
        label.SetTextColor(1 if refion else color)
        label.SetLineWidth(3)
        label.Draw('same')
        self.canvas_main.Update()
        
    def add_legend (self, histogram, key):
        self.legend.AddEntry(histogram,f'{key}', 'l')
        
    def save_pdf(self, name):
        self.canvas_main.SaveAs(f'{name}.pdf')

    def save_root(self, name):
        self.canvas_main.SaveAs(f'{name}.root')
