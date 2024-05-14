from numpy import polyval, array, stack, append, sqrt, genfromtxt
import sys
import re

from barion.ring import Ring
from barion.amedata import AMEData
from barion.particle import Particle

from lisereader.reader import LISEreader

from rionid.inouttools import * 


class ImportData(object):
    '''
    Model (MVC)
    '''
    def __init__(self, refion, alphap, filename = None):

        # Argparser arguments
        self.ref_ion = refion
        self.alphap = alphap
        
        # Extra objects
        self.ring = Ring('ESR', 108.4)
        self.ref_charge = int(refion[refion.index('+'):])
        self.ref_aa = int(re.split('(\d+)', refion)[1])
        self.experimental_data = None
        
        # Get the experimental data
        #if filename: self._get_experimental_data(filename)
            
    def _get_experimental_data(self, filename):
        _, file_extension = os.path.splitext(filename)
        if file_extension.lower() == '.csv':
            self.experimental_data = read_psdata(filename, dbm = False)
        if file_extension.lower() == '.bin_fre' or file_extension.lower() == '.bin_time' or file_extension.lower() == '.bin_amp':
            self.experimental_data = handle_read_tdsm_bin(filename)
        if file_extension.lower() == '.tdms':
            self.experimental_data = handle_read_tdsm(filename)
            #substitute this
        if file_extension.lower() == '.xml':
            self.experimental_data = handle_read_rsa_specan_xml(filename)
        if file_extension.lower() == '.Specan':
            self.experimental_data = handle_read_rsa_specan_xml(filename)
        if file_extension.lower() == '.npz':
            if file_extension.lower() == 'tiq.npz':
                #Shahab processed tiq files format (with 3 arrays)
                self.experimental_data = handle_tiqnpz_data(filename)
            else:    
                # Spectrum data (2 arrays)
                self.experimental_data = handle_prerionidnpz_data(filename)
        #if :
        #    handle_read_rsa_result_csv(filename)
        #if :
        #    handle_read_rsa_data_csv

    def _set_particles_to_simulate_from_file(self, particles_to_simulate):
        
        # import ame from barion: # This would be moved somewhere else
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table
        
        # Read with lise reader  # Extend lise to read not just lise files? 
        lise = LISEreader(particles_to_simulate)
        self.particles_to_simulate = lise.get_info_all()

    def _calculate_moqs(self, particles = None):
        
        # Calculate the  moq from barion of the particles present in LISE file or of the particles introduced
        self.moq = dict()
        
        if particles:
            for particle in particles:
                ion_name = f'{particle.tbl_aa}{particle.tbl_name}+{particle.qq}'
                self.moq[ion_name] = particle.get_ionic_moq_in_u()
        else:
            for particle in self.particles_to_simulate:
                ion_name = f'{particle[1]}{particle[0]}+{particle[4][0]}'
                for ame in self.ame_data:
                    if particle[0] == ame[6] and particle[1] == ame[5]:
                        pp = Particle(particle[2], particle[3], self.ame, self.ring)
                        pp.qq = particle[4][0]
                        # implement into simtofat lines below
                        if ion_name == self.ref_ion: self.moq[ion_name] = pp.get_ionic_moq_in_u()
                        else: self.moq[ion_name] = pp.get_ionic_moq_in_u()

    def _calculate_srrf(self, moqs = None, fref = None, brho = None, ke = None, gam = None, correct = None):
        if moqs:
            self.moq = moqs
        
        self.ref_mass = AMEData.to_mev(self.moq[self.ref_ion] * self.ref_charge)
        self.ref_frequency = self.reference_frequency(fref = fref, brho = brho, ke = ke, gam = gam)

        # Simulated relative revolution frequencies (respect to the reference particle)
        self.srrf = array([1 - self.alphap * (self.moq[name] - self.moq[self.ref_ion]) / self.moq[self.ref_ion]
                              for name in self.moq])
        if correct:
            self.srrf = self.srrf + polyval(array(correct), self.srrf * self.ref_frequency) / self.ref_frequency
        
    def _simulated_data(self, harmonics = None, particles = False):
        # Dictionary with the simulated meassured frecuency and expected yield, for each harmonic
        self.simulated_data_dict = dict()
        
        # Set the yield of the particles to simulate
        if particles: self.yield_data = array([1 for i in range(len(self.moq))])
        else: self.yield_data = array([lise[5] for lise in self.particles_to_simulate])
        # We normalize the yield to avoid problems with ranges and printing
        #yield_data = [yieldd / max(yield_data) for yieldd in yield_data]

        # Get nuclei name for labels
        self.nuclei_names = array([nuclei_name for nuclei_name in self.moq])
        
        # Simulate the expected measured frequency for each harmonic:
        for harmonic in harmonics:
            simulated_data = array([])
            array_stack = array([])
        
            # get srf data
            harmonic_frequency = self.srrf * self.ref_frequency * harmonic
        
            # attach harmonic, frequency, yield data and ion properties together:
            array_stack = stack((harmonic_frequency, self.yield_data, self.nuclei_names), axis=1)  # axis=1 stacks vertically
            simulated_data = append(simulated_data, array_stack)
        
            simulated_data = simulated_data.reshape(len(array_stack), 3)
            name = f'{harmonic}'
            self.simulated_data_dict[name] = simulated_data
            
    def reference_frequency(self, fref = None, brho = None, ke = None, gam = None):
        
        # If no frev given, calculate frev with brho or with ke, whatever you wish
        if fref:
            return fref
        elif brho:
            return ImportData.calc_ref_rev_frequency(self.ref_mass, self.ring.circumference,
                                                     brho = brho, ref_charge = self.ref_charge)
        elif ke:
            return ImportData.calc_ref_rev_frequency(self.ref_mass, self.ring.circumference,
                                                     ke = ke, aa = self.ref_aa)
        elif gam:
            return ImportData.calc_ref_rev_frequency(self.ref_mass, self.ring.circumference,
                                                     gam = gam)
            
        else: sys.exit('None frev, brho, ke or gam')
        
    @staticmethod
    def calc_ref_rev_frequency(ref_mass, ring_circumference, brho = None, ref_charge = None, ke = None, aa = None, gam = None):
        
        if brho:
            gamma = ImportData.gamma_brho(brho, ref_charge, ref_mass)
            
        elif ke:
            gamma = ImportData.gamma_ke(ke, aa, ref_mass)
            
        elif gam:
            gamma = gam
        
        beta = ImportData.beta(gamma)
        velocity = ImportData.velocity(beta)
        
        return ImportData.calc_revolution_frequency(velocity, ring_circumference)
        
    @staticmethod
    def gamma_brho(brho, charge, mass):
        # 1e6 necessary for mass from mev to ev.
        return sqrt(pow(brho * charge * AMEData.CC / (mass * 1e6), 2)+1)
    
    @staticmethod
    def gamma_ke(ke, aa, ref_mass):
        # ke := Kinetic energy per nucleon
        return (ke * aa) / (ref_mass) + 1
    
    @staticmethod
    def beta(gamma):
        return sqrt(gamma**2 - 1) / gamma

    @staticmethod
    def velocity(beta):
        return AMEData.CC * beta
    
    @staticmethod
    def calc_revolution_frequency(velocity, ring_circumference):
        return velocity / ring_circumference
