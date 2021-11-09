from root import *
# eventually change to from root import TCanvas, SetCanvasFormat, ... etc


class CanvasFormat():
    def __init__(self):
        pass

    def set_format_c_1(self):
        c_1 = TPad()
        c_1.SetLeftMargin(0.10)
        c_1.SetRightMargin(0.05)
        c_1.SetTopMargin(0.12)
        c_1.SetBottomMargin(0.25)
        c_1.SetFrameBorderMode(0)
        c_1.SetLogy(1)
        return c_1

    def set_latex_format(self):
        tex = TLatex()
        tex.SetTextColor(2)
        tex.SetTextAngle(90)
        tex.SetLineWidth(2)
        return tex.Draw()
    
    def gammat_calculator(self):
        gGAMMAT = TGraph()
        k = -0.5
        gGAMMAT.SetName('gGAMMAT')
        gGAMMAT.SetPoint(0, 0.998, 2.4234 + (0.98 - 1)*k)
        gGAMMAT.SetPoint(1, 1.000, 2.4234 + (1.000 - 1)*k)
        gGAMMAT.SetPoint(2, 1.002, 2.4234 + (1.02 - 1)*k)
        return gGAMMAT

    def setup_tpad(self):
        # Tpad r3
        r3 = TRandom3()
        # Tpad c0
        c0 = TCanvas('c0', 'c0', 0, 0, 1000, 300)
        SetCanvasFormat(c0)
        # Tpad c
        c = TCanvas('c', 'c', 0, 0, 1000, 880)
        SetCanvasFormat(c)
        c.cd()
        # Tpad c_1
        c_1 = TPad('c_1', 'c_1', 0.00, 0.75, 0.99, 0.99)
        SetPadFormat(c_1)
        c.cd()
        # Tpad c_2
        c_2 = TPad('c_2', 'c_2', 0.0, 0.50, 0.99, 0.75)
        SetPadFormat(c_2)
        c.cd()
        # Tpad c_2_1
        c_2_1 = TPad('c_2_1', 'c_2_1', 0.70, 0.6, 0.86, 0.7189711)
        SetPadFormat(c_2_1)
        c_2_1.SetLeftMargin(0.02857143)
        c_2_1.SetRightMargin(0.02857143)
        c_2_1.SetTopMargin(0.01851852)
        c_2_1.SetBottomMargin(0.01851852)
        # Tpad c_2_2
        c_2_2 = TPad('c_2_2', 'c_2_2', 0.45, 0.6, 0.61, 0.7189711)
        SetPadFormat(c_2_2)
        c_2_2.SetLeftMargin(0.02857143)
        c_2_2.SetRightMargin(0.02857143)
        c_2_2.SetTopMargin(0.01851852)
        c_2_2.SetBottomMargin(0.01851852)
        c.cd()
        # Tpad c_3
        c_3 = TPad('c_3', 'c_3', 0.0, 0.25, 0.99, 0.50)
        SetPadFormat(c_3)
        c.cd()
        # Tpad c_4
        c_4 = TPad('c_4', 'c_4', 0.0, 0.0, 0.99, 0.25)
        SetPadFormat(c_4)
        c_4.SetLogy(0)

        return r3, c0, c, c_1, c_2_1, c_2_2, c_3, c_4

    #not sure about this one, gZ not defined etc...
    def remove_points(self):
        k = gZ.GetN()
        for i in range(0, k):
            gZ.RemovePoint(0)
            gA.RemovePoint(0)
            gCharge.RemovePoint(0)
            gmoq.RemovePoint(0)
            gi.RemovePoint(0)

    def set_latex_labels(self):
        tex200Au79 = TLatex(0.9999552, 2.176887e+14, '^{200}Au^{79+}')
        tex200Au79.SetTextColor(2)
        tex200Au79.SetTextSize(0.08)
        tex200Au79.SetTextAngle(88.21009)
        tex200Au79.SetLineWidth(2)
        tex200Au79.Draw()
        tex200Hg79 = TLatex(0.999965, 2.176887e+13, '^{200}Au^{79+}')
        tex200Hg79.SetTextColor(2)
        tex200Hg79.SetTextSize(0.08)
        tex200Hg79.SetTextAngle(88.21009)
        tex200Hg79.SetLineWidth(2)
        tex200Hg79.Draw()

    @staticmethod
    def set_format_c():
        c.SetFillColor(0)
        c.SetBorderMode(0)
        c.SetBorderSize(2)
        c.SetFrameBorderMode(0)
        return c