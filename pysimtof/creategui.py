from ROOT import *
import numpy as np
import pypeaks
import patternfinder
import ImportData2 as importdata


class CreateGUI():
    def __init__(self, exp_data, simulated_data_dict, ref_ion, nuclei_names):
        self.npeaks = 5
        self.ref_ion=ref_ion
        self.nuclei_names=nuclei_names
        nbins=int(1e6)
        ndivs=4
        
        self.create_canvas(ndivs)
        self.create_histograms(exp_data, simulated_data_dict, nbins)
        self.create_stack(exp_data, simulated_data_dict, nbins, ndivs)
        
    def __call__(self):
        self.histogram_fill()
        self.draw_histograms()
        self.canvas_peaks.Close()
        gSystem.ProcessEvents()

    def create_canvas(self, ndivs):
        self.canvas_main = TCanvas('canvas', 'Frequency Histograms',
                                   800, 800)
        self.canvas_main.SetFillColor(0)
        self.canvas_main.Divide(1, ndivs)
        
        self.canvas_peaks = TCanvas('canvas_peaks', 'peaks',
                                    500, 500)
        
    def create_histograms(self, exp_data, simulated_data_dict, nbins):
        self.histogram_dict = {'exp_data': np.array([TH1F('h_exp_data', 'exp_data', nbins, exp_data[0, 0], exp_data[-1, 0]),
                                                   exp_data], dtype='object').T}
        for key in simulated_data_dict:
            name = f'{key}h'
            self.histogram_dict[name]=np.array([TH1F(name, name, nbins, simulated_data_dict[key][:, 0].min(), simulated_data_dict[key][:, 0].max()),
                                                simulated_data_dict[key][:,:]], dtype='object').T
            
    def create_stack(self, exp_data, simulated_data_dict, nbins, ndivs):
        self.stack=dict()
        self.case_range=dict()
        
        x=int(len(exp_data[:,0])/ndivs)  # dividing range in ndivs
        
        for j in range (0, ndivs):
            name=f'stack{j}'
            self.stack[name]=np.array([THStack()])
            for color, key in enumerate(self.histogram_dict):
                self.stack[name][0].Add(self.histogram_dict[key][0])
                if 'exp' in key: self.case_range[str(j)]= np.array([exp_data[x*j, 0], exp_data[x*(j+1)-1, 0]]).T
                self.histogram_format(self.histogram_dict[key][0], color)

    def histogram_fill(self):
        for key in self.histogram_dict:
            xbin=[self.histogram_dict[key][0].GetXaxis().FindBin(freq) for freq in self.histogram_dict[key][1][:,0]]
            [self.histogram_dict[key][0].AddBinContent(xbin,self.histogram_dict[key][1][i,1]) for i,xbin in enumerate(xbin)]
            if 'h' in key: self.h_scale(self.histogram_dict[key][0])
            #if 'exp' in key: self.histogram_dict[key][0].SetMarkerStyle(kFullCircle)
            
    def h_scale (self, h2):
        self.maximum=self.histogram_dict['exp_data'][0].GetMaximum()
        scale = self.maximum/h2.GetMaximum()
        h2.Scale(scale)
            
    def draw_histograms(self):
        self.Labels = dict()
        self.legend= TLegend(0.9,0.6,0.99,0.99,'blNDC')
        self.set_legend(self.legend)
        for j,stack in enumerate(self.stack):
            self.canvas_main.cd(j+1)
            self.canvas_main.cd(j+1).SetLogy(1)
            self.stack[stack][0].Draw('nostack')
            self.stack[stack][0].GetXaxis().SetRangeUser(self.case_range[str(j)][0], self.case_range[str(j)][1])
            self.stack[stack][0].SetMinimum(self.maximum/1000)
            self.stack[stack][0].SetMaximum(self.maximum*10)
            self.stack_format(self.stack[stack][0])
            self.canvas_main.Update()
            
        for color, key in enumerate(self.histogram_dict):
            self.legend.AddEntry(self.histogram_dict[key][0],f'{key}', 'l')
            if 'h' in key:
                self.create_labels(key, color*20)
        
        self.canvas_main.cd(1)
        self.legend.Draw('same')
        self.canvas_main.Update()
        
    def set_legend(self, legend):
        legend.SetHeader('Schottky Spectra','C')
        legend.SetLineColor(1)
        legend.SetLineStyle(1)
        legend.SetBorderSize(1)
        legend.SetLineWidth(1)
        legend.SetFillColor(kGreen)
        legend.SetFillStyle(1)
        
    def stack_format(self,stack):
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

            
    def histogram_format(self, histogram, color):
        histogram.SetLineColor(color+1)
        histogram.SetLineStyle(2)
        histogram.SetFillColor(0)
        #histogram.SetMarkerStyle(kFullCircle)
        histogram.SetStats(0)
        
    def create_labels(self, key, color):
        xpeaks=self.set_peaks(key)
        self.set_peak_labels(xpeaks, key, color)
                       
    def set_peaks(self, key):
        self.canvas_peaks.cd()
        peaks=pypeaks.FitPeaks(self.npeaks, self.histogram_dict[key][0].Clone(), False)
        xpeaks= peaks.peak_finding()
        self.canvas_peaks.Update()
        return xpeaks
    
    def set_peak_labels(self, xpeaks, key, color):
        for xpeak in xpeaks:
            self.set_peak_label(xpeak, key, color)

    def set_peak_label(self, xpeak, key, color):
        pattern=patternfinder.PatternFinder(self.histogram_dict[key][1][:,0], [xpeak])
        tmp=pattern.get_first_match_index()
        
        frec=self.histogram_dict[key][1][tmp,0]
        xlabel=self.histogram_dict[key][0].GetXaxis().FindBin(frec)
        ylabel=self.histogram_dict[key][0].GetBinContent(xlabel)
        
        nuclei_name=self.nuclei_names[tmp]
        label_name = f'{nuclei_name}_{key}'
        
        RefIon=False
        if self.ref_ion in nuclei_name: RefIon=True
        self.Labels[label_name] = np.array([TLatex(frec, ylabel, label_name), frec, RefIon]).T
        self.draw_label(label_name, color)
            
    def draw_label(self, label, color):
        self.canvas_cd(self.Labels[label][1])
        self.label_format(self.Labels[label][0], self.Labels[label][2], color)
                                    
    def canvas_cd(self, frec):
        for key in self.case_range:
            if frec >= self.case_range[key][0] and frec <= self.case_range[key][1]:
                self.canvas_main.cd(int(key)+1)
                break
         
    def label_format(self, label, RefIon, color):#good ; index->color
        label.SetTextFont(110)
        label.SetTextSize(0.055)
        label.SetTextAngle(90)
        label.SetTextColor(color+4)
        if RefIon: label.SetTextColor(2)
        label.SetLineWidth(3)
        label.Draw('same')
        self.canvas_main.Update()
        
    def add_legend (self, histogram, key):
        self.legend.AddEntry(histogram,f'{key}', 'l')
        
    def save_plot_pdf(self):
        self.canvas_main.SaveAs('plot.pdf')
        self.canvas_main.Update()
        
def test():
    #filename = '/lustre/ap/litv-exp/2021-07-03_E143_TwoPhotonDecay_ssanjari/analyzers/245/245MHz-2021.07.01.13.53.31.717.tiq'
    filename = '/lustre/ap/litv-exp/2021-07-03_E143_TwoPhotonDecay_ssanjari/ntcap/iq/IQ_2021-06-30_12-35-43/0000675.iq.tdms'
    LISE_filename='data/E143_TEline-ESR-72Ge.lpp'
    harmonics=[125, 127]
    Brho=6.90922
    Gammat=1.395
    ref_iso='72Ge'
    ref_charge=32
    
    mydata = importdata.ImportData(filename, LISE_filename, harmonics, Brho, Gammat, ref_iso, ref_charge)
    mycanvas = CreateGUI(mydata.exp_data, mydata.simulated_data_dict)

if __name__ == '__main__':
    test()
