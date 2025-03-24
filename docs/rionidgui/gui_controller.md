# GUI Controller

The `gui_controller.py` module is responsible for handling the simulation workflow in the Rionid GUI. It provides functions to process input data, perform calculations, and save simulation results.

## Functions

### `import_controller`

This is the main function that orchestrates the simulation process.

#### Parameters:
- `datafile` (str, optional): Path to the input data file.
- `filep` (str, optional): Path to the particle simulation file.
- `alphap` (float, optional): Alpha parameter for calculations.
- `refion` (str, optional): Reference ion for the simulation.
- `harmonics` (str, optional): Space-separated harmonic numbers.
- `nions` (int, optional): Number of ions to display in the output.
- `amplitude` (float, optional): Amplitude for calculations (currently unused).
- `circumference` (float, optional): Circumference of the accelerator.
- `mode` (str, optional): Mode of operation (`'Frequency'`, `'Bρ'`, `'Kinetic Energy'`, or `'Gamma'`).
- `value` (float, optional): Value corresponding to the selected mode.
- `reload_data` (bool, optional): Whether to reload the input data.

#### Returns:
- `ImportData` object containing the simulated spectrum data, or `None` if an error occurs.

#### Workflow:
1. Initializes parameters based on the input.
2. Uses the `ImportData` class to process the input data and perform calculations.
3. Simulates data for the specified harmonics.
4. Displays the top `nions` ions using the `display_nions` function.
5. Saves the simulation results to a file using the `save_simulation_results` function.

---

### `display_nions`

Displays the top `nions` ions based on their yield data.

#### Parameters:
- `nions` (int): Number of ions to display.
- `yield_data` (array): Yield data for the ions.
- `nuclei_names` (array): Names of the nuclei.
- `simulated_data_dict` (dict): Dictionary containing simulated data for each harmonic.
- `ref_ion` (str): Reference ion for the simulation.
- `harmonics` (list): List of harmonic numbers.

---

### `save_simulation_results`

Saves the simulation results to a file.

#### Parameters:
- `mydata` (`ImportData`): Object containing the simulation data.
- `harmonics` (list): List of harmonic numbers.
- `sort_index` (list): Indices of the sorted simulation results.
- `filename` (str, optional): Name of the output file (default: `'simulation_result.out'`).

#### Output:
- Saves the results in a structured format, including ion names, frequencies, yields, mass-to-charge ratios, and masses.

---

## Example Usage

```python
from rionidgui.gui_controller import import_controller

result = import_controller(
    datafile="input.dat",
    filep="particles.dat",
    alphap=0.5,
    refion="C12",
    harmonics="1 2 3",
    nions=5,
    circumference=100.0,
    mode="Frequency",
    value=1e6,
    reload_data=True
)
```