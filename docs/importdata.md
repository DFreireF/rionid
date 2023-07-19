## ImportData Documentation

The provided Python code defines a class `ImportData` that represents the Model component of the Model-View-Controller (MVC) design pattern. It is designed to handle the import and processing of experimental and simulated data for Schottky spectra analysis.

### Class: ImportData

#### Constructor:
- `__init__(self, refion, alphap, filename=None)`: Constructor to initialize the ImportData object.
  - Parameters:
    - `refion`: A string representing the reference ion.
    - `alphap`: A floating-point number representing alpha value.
    - `filename`: (optional) A string representing the filename of the experimental data file.
  - Returns: None

#### Methods:

1. `_set_particles_to_simulate_from_file(self, particles_to_simulate)`: Sets the particles to simulate based on the provided data.
   - Parameters:
     - `particles_to_simulate`: A list of particle data to be simulated.
   - Returns: None

2. `_calculate_moqs(self, particles=None)`: Calculates the mass over charge (moq) for particles present in the LISE file or particles introduced.
   - Parameters:
     - `particles`: (optional) A list of particle data for which moq needs to be calculated.
   - Returns: None

3. `_calculate_srrf(self, moqs=None, fref=None, brho=None, ke=None, gam=None, correct=None)`: Calculates the simulated relative revolution frequencies (SRRF) based on provided parameters or using previously calculated moq values.
   - Parameters:
     - `moqs`: (optional) A dictionary containing moq values for various ions.
     - `fref`: (optional) The reference frequency in Hz.
     - `brho`: (optional) The magnetic rigidity in T.m.
     - `ke`: (optional) The kinetic energy per nucleon in MeV/u.
     - `gam`: (optional) The Lorentz gamma factor.
     - `correct`: (optional) A polynomial coefficient for correcting the simulated frequencies.
   - Returns: None

4. `_simulated_data(self, harmonics=None, particles=False)`: Simulates the measured frequency and expected yield for each harmonic.
   - Parameters:
     - `harmonics`: (optional) A list of integers representing harmonics for simulation.
     - `particles`: A boolean indicating whether to simulate particle data.
   - Returns: None

5. `reference_frequency(self, fref=None, brho=None, ke=None, gam=None)`: Calculates the reference frequency based on provided parameters or given conditions.
   - Parameters:
     - `fref`: (optional) The reference frequency in Hz.
     - `brho`: (optional) The magnetic rigidity in T.m.
     - `ke`: (optional) The kinetic energy per nucleon in MeV/u.
     - `gam`: (optional) The Lorentz gamma factor.
   - Returns: The calculated reference frequency in Hz.

6. `calc_ref_rev_frequency(ref_mass, ring_circumference, brho=None, ref_charge=None, ke=None, aa=None, gam=None)`: Calculates the reference revolution frequency based on provided parameters.
   - Parameters:
     - `ref_mass`: The reference mass in atomic mass units (u).
     - `ring_circumference`: The circumference of the ring in meters (m).
     - `brho`: (optional) The magnetic rigidity in T.m.
     - `ref_charge`: (optional) The reference ion charge.
     - `ke`: (optional) The kinetic energy per nucleon in MeV/u.
     - `aa`: (optional) The atomic mass number of the reference ion.
     - `gam`: (optional) The Lorentz gamma factor.
   - Returns: The calculated reference revolution frequency in Hz.

7. `gamma_brho(brho, charge, mass)`: Calculates the Lorentz gamma factor based on magnetic rigidity.
   - Parameters:
     - `brho`: The magnetic rigidity in T.m.
     - `charge`: The charge of the particle.
     - `mass`: The mass of the particle in atomic mass units (u).
   - Returns: The calculated Lorentz gamma factor.

8. `gamma_ke(ke, aa, ref_mass)`: Calculates the Lorentz gamma factor based on kinetic energy per nucleon.
   - Parameters:
     - `ke`: The kinetic energy per nucleon in MeV/u.
     - `aa`: The atomic mass number of the reference ion.
     - `ref_mass`: The reference mass in atomic mass units (u).
   - Returns: The calculated Lorentz gamma factor.

9. `beta(gamma)`: Calculates the beta factor based on the Lorentz gamma factor.
   - Parameters:
     - `gamma`: The Lorentz gamma factor.
   - Returns: The calculated beta factor.

10. `velocity(beta)`: Calculates the velocity of the particle based on the beta factor.
    - Parameters:
      - `beta`: The beta factor of the particle.
    - Returns: The calculated velocity in m/s.

11. `calc_revolution_frequency(velocity, ring_circumference)`: Calculates the revolution frequency of the particle based on its velocity and the circumference of the ring.
    - Parameters:
      - `velocity`: The velocity of the particle in m/s.
      - `ring_circumference`: The circumference of the ring in meters (m).
    - Returns: The calculated revolution frequency in Hz.

12. `gammat(alphap)`: Calculates the gamma_t factor based on the alpha parameter.
    - Parameters:
      - `alphap`: The alpha parameter.
    - Returns: The calculated gamma_t factor.

13. `read_psdata(filename, dbm=False)`: Reads the experimental data from a file.
    - Parameters:
      - `filename`: The name of the file containing the experimental data.
      - `dbm`: A boolean indicating whether the file is in dBm format.
    - Returns: A numpy array containing the experimental data (frequency and yield).