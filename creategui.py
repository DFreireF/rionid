from ROOT import *
import numpy as np
import pypeaks
import patternfinder

class CreateGUI():
    def __init__(self, analyzers_data,
                 simulated_data_dict, NTCAP_data, harmonics):
        # setting object variables:
        # frec =analyzers_data[:,0]   power =analyzers_data[:,1]
        self.analyzers_data = analyzers_data
        # frec=simulated_data[:,0] power=simulated_data[:,1], ion properties=[:,2,3,4]; key=harmonic number
        self.simulated_data_dict = simulated_data_dict
        self.NTCAP_data = NTCAP_data
        self.harmonics = harmonics
        self.npeaks = 5

        self.create_histograms()
        self.histogram_fill()
        self.create_canvas()
        self.draw_histograms()

        # prevents gui closing in pyroot. must go last in init!
        gApplication.Run()

    def create_canvas(self):
        self.canvas_main = TCanvas(
            'canvas_main', 'Frequency Histograms', 800, 800)
        self.canvas_main.Divide(1, 3)

        self.canvas_NTCAP = TCanvas(
            'canvas_NTCAP', 'Frequency Histograms', 800, 800)
        self.canvas_NTCAP.Divide(1, 4)

        self.canvas_peaks = TCanvas(
            'canvas_peaks', 'peaks', 800, 800)

    def create_histograms(self):
        nbins=int(1e5)
        self.histogram_peak=dict()
        
        # experimental data
        self.histogram_dict = {'tiqdata': np.array([TH1F('h_tiqdata', 'tiqdata', nbins, self.analyzers_data[0, 0], self.analyzers_data[-1, 0]),
                                                   self.analyzers_data], dtype='object').T}
        # create histograms with each harmonic info
        for key in self.simulated_data_dict:
            name = f'srf {key}'
            self.histogram_dict[name]=np.array([TH1F(name, name, nbins, self.simulated_data_dict[key][:, 0].min(),
                                                     self.simulated_data_dict[key][:, 0].max()), self.simulated_data_dict[key][:,:]], dtype='object').T
        # histo with NTCAP info
        self.histogram_dict['NTCAPdata']=  np.array([TH1F('NTCAPdata', 'NTCAPdata', nbins, self.NTCAP_data[0, 0], self.NTCAP_data[-1, 0]),
                                          self.NTCAP_data], dtype='object').T
        
    def histogram_fill(self):
        for key in self.histogram_dict:
            xbin=[self.histogram_dict[key][0].GetXaxis().FindBin(freq) for freq in self.histogram_dict[key][1][:,0]]
            [self.histogram_dict[key][0].AddBinContent(xbin,self.histogram_dict[key][1][i,1]) for i,xbin in enumerate(xbin)]
            
    def draw_histograms(self):
        self.Labels = dict()
        
        for i,key in enumerate(self.histogram_dict):
            # plotting tiq histo
            if 'tiq' in key:
                self.canvas_main.cd(1)  # move to correct canvas
                self.hist_plot_short(self.histogram_dict[key][0],i,self.canvas_main)
                self.canvas_main.cd(3)  # move to correct canvas
                name=str(i)+key
                self.clone_histo(name,self.histogram_dict[key][0],self.analyzers_data[0,0], self.analyzers_data[-1,0])
                self.hist_plot_short(globals()[name],i,self.canvas_main)

            # plotting data with the simulated harmonic
            elif 'srf' in key:
                name=str(i)+key

                self.canvas_main.cd(2)  # move to correct canvas
                self.hist_plot_short(self.histogram_dict[key][0],i,self.canvas_main)
                #input()
                self.create_labels(key,name,self.canvas_main,i)
                #input()
                self.canvas_main.cd(3)  # move to correct canvas
                
                self.clone_histo(name,self.histogram_dict[key][0],
                                 self.histogram_dict[key][1][:,0].min(),self.histogram_dict[key][1][:,0].max())
                self.hist_plot_short(globals()[name],i,self.canvas_main)

            # plotting data with NTCAP + simulated harmonics
            elif 'NTCAP' in key:
                x = int(len(self.histogram_dict[key][1][:,0])/4)  # dividing range in 4
                for j in range(0, 4):
                    self.canvas_NTCAP.cd(j+1)
                    name='NTCAP_copy'+str(j)
                    self.clone_histo(name,self.histogram_dict[key][0],
                                 self.histogram_dict[key][1][x*j,0], self.histogram_dict[key][1][x*(j+1)-1,0])
                    self.hist_plot_short(globals()[name],i,self.canvas_NTCAP)
                    self.create_labels_NTCAP(
                        self.histogram_dict[key][1][x*j,0], self.histogram_dict[key][1][x*(j+1)-1,0],self.canvas_NTCAP,j)

        # saving histos in pdf
      #  self.canvas_main.SaveAs('histogram_plot.pdf')
      #  self.canvas_NTCAP.SaveAs('NTCAP_plot.pdf')
      
    def hist_plot_short(self,histogram,index,canvas):
        histogram.SetLineColor(index+1)
        histogram.SetLineStyle(1)
        histogram.Draw('same')
        gPad.BuildLegend(0.75, 0.75, 0.95, 0.95)
        canvas.Update()
        
    def create_labels(self,key,name,canvas,index):
        xpeaks=self.set_peaks(key)
        canvas.cd(2)
        [self.set_peak_labels(key,name,xpeak,index) for xpeak in xpeaks]
        canvas.Update()

    def clone_histo(self,name,histogram,range_min,range_max):
        globals()[name]=histogram.Clone()
        globals()[name].Draw('same')
        globals()[name].GetXaxis().SetRangeUser(range_min, range_max)
        
    def create_labels_NTCAP(self, range_min, range_max,canvas,j):
        index=0
        for key in self.histogram_dict:
            if 'srf' in key:
                index+=1
                name=key+str(index)+str(j)
                self.clone_histo(name, self.histogram_dict[key][0],range_min,range_max)        
                self.hist_plot_short(globals()[name],index,canvas)
                
                xpeaks=self.set_peaks(key)
                for xpeak in xpeaks:
                    if xpeak <= range_max and xpeak >= range_min:
                        canvas.cd(j+1)
                        self.set_peak_labels(key,name,xpeak,index)
                        
                self.canvas_NTCAP.Update()
                        
    def set_peaks(self, key):
        self.canvas_peaks.cd()
        peaks=pypeaks.FitPeaks(self.npeaks,self.histogram_dict[key][0].Clone(),False)
        xpeaks= peaks.peak_finding()
        self.canvas_peaks.Update()
        return xpeaks

    def set_peak_labels(self, key,name,xpeak,index):
        pattern=patternfinder.PatternFinder(self.histogram_dict[key][1][:,0],[xpeak])
        tmp=pattern.get_first_match_index()
        
        xlabel=self.histogram_dict[key][0].GetXaxis().FindBin(self.histogram_dict[key][1][tmp,0])
        ylabel=self.histogram_dict[key][0].GetBinContent(xlabel)
        
        Aion, Zion, Qion=[int(self.histogram_dict[key][1][tmp,i]) for i in range(2,5)]
        label_name = f'{Aion}A{Zion}Z+{Qion}q{key}{name}'
        
        self.RefIon=False
        if Aion==72 and Zion==32: self.RefIon=True
        self.Labels[label_name] = TLatex(
            self.histogram_dict[key][1][tmp,0], ylabel, label_name)
        self.label_format(index, self.Labels[label_name])

    def label_format(self,index,label):
        label.SetTextFont(110)
        label.SetTextSize(0.055)
        label.SetTextAngle(90)
        label.SetTextColor(index+2)
        if self.RefIon: label.SetTextColor(2)
        label.SetLineWidth(3)
        label.Draw('same')


def test():
    import importdata
    mydata = importdata.ImportData('data/410-j', 'data/tdms-example')
    mycanvas = CreateGUI(mydata.analyzer_data, mydata.simulated_data_dict,
                         mydata.NTCAP_data, mydata.harmonics)


if __name__ == '__main__':
    test()
