from ROOT import *
from barion.patternfinder import *
from pysimtof.pypeaks import *
from pysimtof.importdata import *

class CreateGUI():
    '''
    View (MVC)
    '''
    
    def __init__(self, exp_data, simulated_data_dict, ref_ion, nuclei_names, ndivs, filename):
        
        self.ref_ion = ref_ion
        self.nuclei_names = nuclei_names
        
        self.create_canvas(ndivs)
        self.create_histograms(exp_data, simulated_data_dict, filename)
        self.histogram_fill()
        self.create_stack(exp_data, simulated_data_dict, ndivs)
        
    def _set_args(self, idx_case):
        
        self.histogram_scale(idx_case)
        self.draw_histograms()
        self.canvas_peaks.Close()
        gSystem.ProcessEvents()
        gApplication.Run() #for now only

    def create_canvas(self, ndivs):
        self.canvas_main = TCanvas('canvas', 'Frequency Histograms',
                                   800, 800)
        self.canvas_main.SetFillColor(0)
        self.canvas_main.Divide(1, ndivs)
        self.canvas_peaks = TCanvas('canvas_peaks_srf', 'canvas_peaks_srf',
                                    500, 500)

    def create_histograms(self, exp_data, simulated_data_dict, filename):
        self.histogram_dict = {'exp_data': np.array([TH1D('h_exp_data', filename, len(exp_data[:,0]),
                                                          exp_data[:, 0].min(), exp_data[:, 0].max()), exp_data], dtype='object').T}
        for key in simulated_data_dict:
            name = f'srf{key}'
            self.histogram_dict[name]=np.array([TH1F(name, name, int(1e6),
                                                     simulated_data_dict[key][:, 0].min(), simulated_data_dict[key][:, 0].max()), simulated_data_dict[key][:,:]], dtype='object').T
            
        [self.histogram_format(self.histogram_dict[key][0], color, key) for color, key in enumerate(self.histogram_dict)]

    def histogram_fill(self):
        for key in self.histogram_dict:
            xbin=[self.histogram_dict[key][0].GetXaxis().FindBin(frec) for frec in self.histogram_dict[key][1][:,0]]
            [self.histogram_dict[key][0].AddBinContent(xbin,self.histogram_dict[key][1][i,1]) for i,xbin in enumerate(xbin)]
            
    def histogram_scale (self, idx_case):
        maximum=self.histogram_dict['exp_data'][0].GetMaximum()
        for key in self.histogram_dict:
            if 'srf' in key: 
                if idx_case==0:
                    for frec in (self.histogram_dict[key][1][:,0]):
                        self.histogram_dict[key][0].SetBinContent(self.histogram_dict[key][0].FindBin(frec), maximum) 
                else:
                    scale = maximum/self.histogram_dict[key][0].GetMaximum()
                    self.histogram_dict[key][0].Scale(scale)
                
    def create_stack(self, exp_data, simulated_data_dict, ndivs):
        self.xrange_divs=dict()
        self.exp_dict=dict()
        self.stack=dict()
        x=int(len(exp_data[:,0])/ndivs)  # dividing range in ndivs
        for j in range (0, ndivs):
           name=f'stack{j}'
           self.xrange_divs[str(j)]= np.array([exp_data[x*j, 0], exp_data[x*(j+1)-1, 0]]).T
           self.exp_dict[name]=self.histogram_dict['exp_data'][0].Clone()
           self.stack[name]=np.array([THStack()])
           [self.stack[name][0].Add(self.histogram_dict[key][0]) for key in self.histogram_dict if 'srf' in key]
            
    def draw_histograms(self):
        self.labels = dict()
        self.legend= TLegend(0.9,0.6,0.99,0.99,'blNDC')
        self.set_legend(self.legend)
        for j, stack in enumerate(self.stack):
            self.canvas_main.cd(j+1)
            self.canvas_main.cd(j+1).SetLogy(1)
            self.exp_dict[stack].Draw('hist')
            self.stack[stack][0].Draw('same nostack')
            self.set_ranges(j,stack)
            self.stack_format(self.stack[stack][0])
            self.canvas_main.Update()
            
        for color, key in enumerate(self.histogram_dict):
            self.legend.AddEntry(self.histogram_dict[key][0],f'{key}', 'l')
            if 'srf' in key:
                self.create_labels(key, color+1)
        self.canvas_main.cd(1)
        self.legend.Draw('same')
        self.canvas_main.Update()
        
    def set_legend(self, legend):
        legend.SetHeader('Schottky Spectra','C')
        legend.SetLineColor(1)
        legend.SetLineStyle(1)
        legend.SetBorderSize(1)
        legend.SetLineWidth(1)
        legend.SetFillStyle(1)
        
    def set_ranges(self, index, stack):
        index_min=np.where(self.histogram_dict['exp_data'][1][:,0]==self.xrange_divs[str(index)][0])
        index_max=np.where(self.histogram_dict['exp_data'][1][:,0]==self.xrange_divs[str(index)][1])
        index_maxy_range=index_min[0][0]+np.argmax(self.histogram_dict['exp_data'][1][index_min[0][0]:index_max[0][0],1])
        maximum=self.histogram_dict['exp_data'][1][index_maxy_range,1]
        self.exp_dict[stack].SetMinimum(maximum/10000)
        self.exp_dict[stack].SetMaximum(maximum*100)
        self.exp_dict[stack].GetXaxis().SetRangeUser(self.xrange_divs[str(index)][0], self.xrange_divs[str(index)][1])
        self.stack[stack][0].SetMinimum(maximum/10000)
        self.stack[stack][0].SetMaximum(maximum*100)
        self.stack[stack][0].GetXaxis().SetRangeUser(self.xrange_divs[str(index)][0], self.xrange_divs[str(index)][1])
        
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
            if color+1==4: color=224
            if color+1==5: color=94
            histogram.SetLineColor(color+1)
            histogram.SetFillColor(color+1)
        histogram.SetLineStyle(1)
        histogram.SetStats(0)

    def create_labels(self, key, color):
        xpeaks=self.set_peaks(key)
        self.set_peak_labels(xpeaks, key, color)

    def set_peaks(self, key):
        self.canvas_peaks.cd()
        peaks=FitPeaks(200, self.histogram_dict[key][0].Clone(), False) # in Search set options nodraw to not draw it. #200 peaks to fit
        xpeaks= peaks.peak_finding()
        self.canvas_peaks.Update()
        return xpeaks
    
    def set_peak_labels(self, xpeaks, key, color):
        [self.set_peak_label(xpeak, key, color) for xpeak in xpeaks]

    def set_peak_label(self, xpeak, key, color):
        pattern=PatternFinder(self.histogram_dict[key][1][:,0], [xpeak])
        tmp=pattern.get_first_match_index()
        
        frec=self.histogram_dict[key][1][tmp,0]
        xlabel=self.histogram_dict[key][0].GetXaxis().FindBin(frec)
        ylabel=self.histogram_dict[key][0].GetBinContent(xlabel)
        
        nuclei_name=self.nuclei_names[tmp]
        label_name = f'{nuclei_name}{key}'
        
        refion=False
        if self.ref_ion in nuclei_name:refion=True
        self.labels[label_name] = np.array([TLatex(frec, ylabel, nuclei_name), frec, refion]).T
        self.draw_label(label_name, color)

    def draw_label(self, label, color):
        self.canvas_cd(self.labels[label][1])
        if self.plot_this_label:
            self.label_format(self.labels[label][0], self.labels[label][2], color)
            self.plotted_labels=np.array([self.labels[label]])
                                    
    def canvas_cd(self, frec):
        self.plot_this_label=False
        for key in self.xrange_divs:
            if (frec>=self.xrange_divs[key][0]) and (frec<=self.xrange_divs[key][1]):
                self.canvas_main.cd(int(key)+1)
                self.plot_this_label=True
                break
         
    def label_format(self, label, refion, color):
        label.SetTextFont(110)
        label.SetTextSize(0.055)
        label.SetTextAngle(90)
        if color==4: color=225 #for not using the blue for this (since it is the data color)
        if color==5: color=95 #to avoid yellow
        label.SetTextColor(color)
        if refion: label.SetTextColor(1)
        label.SetLineWidth(3)
        label.Draw('same')
        self.canvas_main.Update()
        
    def add_legend (self, histogram, key):
        self.legend.AddEntry(histogram,f'{key}', 'l')
        
    def save_pdf(self, name):
        self.canvas_main.SaveAs(f'{name}.pdf')

    def save_root(self, name):
        self.canvas_main.SaveAs(f'{name}.root')
