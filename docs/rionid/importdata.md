# ImportData Module

The `importdata.py` module defines the `ImportData` class, which serves as the **Model** in the Model-View-Controller (MVC) design pattern. This class is responsible for handling experimental data, calculating mass-to-charge ratios, and simulating revolution frequencies for ions.

## Class

### `ImportData`

The `ImportData` class provides methods to load, process, and simulate experimental data for ion analysis.

#### Constructor: `__init__(self, refion, alphap, filename=None, reload_data=None, circumference=None)`

Initializes the `ImportData` instance.

#### Parameters:
- `refion` (str): Reference ion in the format `AAXX+CC` (e.g., `72Ge+35`).
- `alphap` (float): Momentum compaction factor or gamma transition.
- `filename` (str, optional): Path to the experimental data file.
- `reload_data` (bool, optional): Whether to reload the experimental data.
- `circumference` (float, optional): Circumference of the ring in meters.

---

## Methods

### Data Handling

#### `_get_cache_file_path(self, filename)`
Generates the path for the cached data file.

#### `_get_experimental_data(self, filename)`
Loads experimental data from the specified file. Supports multiple file formats:
- `.csv`
- `.bin_fre`, `.bin_time`, `.bin_amp`
- `.tdms`
- `.xml`
- `.Specan`
- `.npz`

#### `_save_experimental_data(self)`
Saves experimental data to a compressed `.npz` file.

#### `_load_experimental_data(self)`
Loads experimental data from a cached `.npz` file.

---

### Particle Simulation

#### `_set_particles_to_simulate_from_file(self, particles_to_simulate)`
Loads particle data from a file using the `LISEreader` class.

#### `_calculate_moqs(self, particles=None)`
Calculates the mass-to-charge ratios (`m/q`) for particles.

#### `_calculate_srrf(self, moqs=None, fref=None, brho=None, ke=None, gam=None, correct=None)`
Calculates the simulated relative revolution frequencies (SRRF) for particles.

#### `_simulated_data(self, harmonics=None, particles=False, mode=None)`
Simulates the expected measured frequencies and yields for each harmonic.

---

### Physics Calculations

#### `calculate_brho_relativistic(self, moq, frequency, circumference, harmonic)`
Calculates the relativistic magnetic rigidity (`Bρ`) of an ion.

#### `reference_frequency(self, fref=None, brho=None, ke=None, gam=None)`
Calculates the reference revolution frequency based on the provided parameters.

#### `calc_ref_rev_frequency(ref_mass, ring_circumference, brho=None, ref_charge=None, ke=None, aa=None, gam=None)`
Calculates the revolution frequency of the reference particle.

#### `gamma_brho(brho, charge, mass)`
Calculates the Lorentz factor (`γ`) from `Bρ`.

#### `gamma_ke(ke, aa, ref_mass)`
Calculates the Lorentz factor (`γ`) from kinetic energy.

#### `beta(gamma)`
Calculates the relativistic beta (`β`).

#### `velocity(beta)`
Calculates the velocity of the particle.

#### `calc_revolution_frequency(velocity, ring_circumference)`
Calculates the revolution frequency of the particle.

---

## Workflow

1. **Data Loading**:
   - Experimental data is loaded from a file or cache.
   - Particle data is loaded using the `LISEreader` class.

2. **Mass-to-Charge Ratio Calculation**:
   - Calculates `m/q` for particles using the `AMEData` and `Particle` classes.

3. **Revolution Frequency Simulation**:
   - Simulates the relative revolution frequencies (`SRRF`) for particles.
   - Applies optional polynomial corrections.

4. **Simulated Data Generation**:
   - Generates simulated frequencies and yields for each harmonic.

---

## Dependencies

The `importdata.py` module relies on the following libraries and modules:
- **Numpy**: For numerical operations.
- **Barion Modules**:
  - `ring`: Provides the `Ring` class for ring properties.
  - `amedata`: Provides the `AMEData` class for mass-energy conversions.
  - `particle`: Provides the `Particle` class for particle properties.
- **LISEreader**: For reading particle simulation files.
- **RionID Modules**:
  - `inouttools`: Provides utility functions for data input/output.

---

## Example Usage

The `ImportData` class is typically used to process experimental data and simulate ion properties. Below is an example of how to use it:

```python
from rionid.importdata import ImportData

# Initialize the ImportData object
data = ImportData(
    refion="72Ge+35",
    alphap=0.5,
    filename="input.csv",
    reload_data=True,
    circumference=100.0
)

# Load particles to simulate
data._set_particles_to_simulate_from_file("particles.lise")

# Calculate mass-to-charge ratios
data._calculate_moqs()

# Simulate revolution frequencies
data._calculate_srrf(fref=1e6)

# Generate simulated data for harmonics
data._simulated_data(harmonics=[1, 2, 3])
```