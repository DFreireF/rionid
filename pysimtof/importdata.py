from barion.ring import Ring
from barion.amedata import *
from barion.particle import *
from lisereader.reader import *
from ROOT import *
from iqtools import *
import sys


class ImportData():
    '''
    Model (MVC)
    '''
    def __init__(self, filename, harmonics, refion, alphap):

        # Argparser arguments
        self.harmonics = harmonics
        self.ref_ion = refion
        self.alphap = alphap

        # Extra objects
        self.ring = Ring('ESR', 108.4) # 108.43 Ge
        
        for i, char in enumerate(refion):
            if char == '+': aux = i
        self.ref_charge = int(refion[aux:])

        # Get the experimental data
        self.experimental_data = read_experimental_data(filename)
        
    def set_particles_to_simulate_from_file(self, particles_to_simulate):
        
        # import ame from barion: # This would be moved somewhere else
        self.ame = AMEData()
        self.ame_data = self.ame.ame_table
        
        # Read with lise reader  # Extend lise to read not just lise files? 
        lise = LISEreader(particles_to_simulate)
        self.particles_to_simulate = lise.get_info_all()

    def calculate_moqs(self, particles = None):
        
        # Calculate the  moq from barion of the particles present in LISE file or of the particles introduced
        self.moq = dict()
        
        if particles:
            for particle in particles:
                ion_name = f'{particle.tbl_aa}{particle.tbl_name}+{particle.qq}'
                self.moq[ion_name] = particle.get_ionic_moq_in_u()

        else:
            self._import()
            for particle in self.particles_to_simulate:
                ion_name = f'{particle[1]}{particle[0]}+{particle[4][0]}'
                for ame in self.ame_data:
                    if particle[0] == ame[6] and particle[1] == ame[5]:
                        self.moq[ion_name] = Particle(particle[2], particle[3], self.ame, self.ring).get_ionic_moq_in_u()

    def _calculate_srrf(self, moqs = None, frev = None, brho = None):
        
        if moqs:
            self.moq = moqs

        if brho:
            mass_ref = AMEData.to_mev(self.moq[self.ref_ion] * self.ref_charge)
            self.frequence_rel = ImportData.calculate_ion_parameters(self.brho, self.ref_charge, mass_ref, self.ring.circumference)
            
        elif:
            self.frequence_rel = frev
            
        else:
            sys.exit('You forgot to pass to _calculate_srrf() the frev or brho')
            
        # Simulated relative revolution frequencies (respect to the reference particle)
        self.srrf = np.array([1 - self.alphap * (self.moq[name] - self.moq[self.ref_ion]) / self.moq[self.ref_ion]
                              for name in self.moq])
        
    def _simulated_data(self, particles = False):
        
        self.simulated_data_dict = dict()
        
        # Set the yield of the particles to simulate
        if particles: yield_data = [1 for i in range(len(self.moq))]
        else: yield_data = [lise[5] for lise in self.lise_data]
        
        # Get nuclei name for labels
        self.nuclei_names = [nuclei_name for nuclei_name in self.moq]
        
        # Simulate the expected meassured frecuency for each harmonic:
        for harmonic in self.harmonics:            
            simulated_data = np.array([])
            array_stack = np.array([])
            # get srf data
            harmonic_frequency = self.srrf * self.frequence_rel * harmonic
            print(harmonic_frequency, harmonic, self.frequence_rel * harmonic)
            # attach harmonic, frequency, yield data and ion properties together:
            array_stack = np.stack((harmonic_frequency, yield_data),
                                   axis=1)  # axis=1 stacks vertically
            simulated_data = np.append(simulated_data, array_stack)
            simulated_data = simulated_data.reshape(len(array_stack), 2)
            name = f'{harmonic}'            
            self.simulated_data_dict[name] = simulated_data
            
    @staticmethod
    def calculate_ion_parameters(brho, ref_charge, ref_mass, ring_circumference):
        
        gamma = ImportData.gamma(brho, ref_charge, ref_mass)
        beta = ImportData.beta(gamma)
        velocity = ImportData.velocity(beta)
        frequence_rel = ImportData.calc_freq_rel(velocity, ring_circumference)
        return frequence_rel
        
    @staticmethod
    def gamma(brho, ref_charge, ref_mass):
        # /1e6 necessary for mass from mev to ev.
        return np.sqrt(pow(brho*ref_charge*(AMEData.CC/1e6)/ref_mass, 2)+1)        
    
    @staticmethod
    def beta(gamma):
        return np.sqrt(gamma**2 - 1) / gamma

    @staticmethod
    def velocity(beta):
        return AMEData.CC * beta
    
    @staticmethod
    def calc_freq_rel(velocity, ring_circumference):
        return velocity / ring_circumference
    
    @staticmethod
    def read_csv(filename):
        f, p  = [np.array([]) for i in range(2)]
        with open(filename) as f:
            cont = f.readlines()[1:]
            for l in cont:
                l = l.split('|')
                f = np.append(f, float(l[0]))
                p = np.append(p, float(l[1]))
        return (np.stack((f, p), axis = 1).reshape((len(f), 2)))
