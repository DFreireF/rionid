# Main Module

The `__main__.py` module serves as the entry point for the RionID application. It provides a command-line interface (CLI) for running simulations and visualizing results. The module supports both batch processing and interactive visualization.

## Functions

### `main()`

The `main()` function parses command-line arguments, validates inputs, and orchestrates the simulation and visualization workflow.

#### Workflow:
1. **Argument Parsing**:
   - Uses `argparse` to define and parse CLI arguments.
   - Supports mutually exclusive modes (`brho`, `fref`, `kenergy`, `gamma`) for specifying the reference particle's properties.
2. **Input Validation**:
   - Ensures that at least one mode (`brho`, `fref`, `kenergy`, or `gamma`) is provided.
3. **Simulation Execution**:
   - Processes input files and runs simulations using the `controller` or `controller2` functions.
4. **Visualization**:
   - Displays results interactively or saves them to files, depending on the provided arguments.

---

### `controller(data_file, ...)`

Handles the simulation workflow for a single input file.

#### Parameters:
- `data_file` (str): Path to the experimental data file.
- `particles_to_simulate` (str): Path to the file containing particles to simulate.
- `alphap` (float): Momentum compaction factor or gamma transition.
- `ref_ion` (str): Reference ion in the format `AAXX+CC` (e.g., `72Ge+35`).
- `ndivs` (int): Number of divisions in the display.
- `amplitude` (int): Display scaling option.
- `show` (bool): Whether to show the visualization.
- `brho`, `fref`, `ke`, `gam` (float, optional): Reference particle properties.
- `out` (str, optional): Output directory.
- `harmonics` (list, optional): Harmonics to simulate.
- `correct` (list, optional): Polynomial correction parameters.
- `ods` (bool, optional): Whether to write results to an ODS file.
- `nions` (int, optional): Number of ions to display.

#### Workflow:
1. Loads experimental data using the `ImportData` class.
2. Calculates mass-to-charge ratios (`moqs`) and simulated frequencies.
3. Displays results interactively or saves them to files.

---

### `controller2(data_file, ...)`

Similar to `controller`, but uses the `CreatePyGUI` class for visualization.

---

### `display_nions(nions, ...)`

Filters and displays the top `nions` ions based on their yield.

#### Parameters:
- `nions` (int): Number of ions to display.
- `yield_data` (array): Yield data for the ions.
- `nuclei_names` (array): Names of the nuclei.
- `simulated_data_dict` (dict): Simulated data for each harmonic.
- `ref_ion` (str): Reference ion.
- `harmonics` (list): Harmonics to simulate.

---

### `read_masterfile(master_filename)`

Reads a list of filenames from a master file.

#### Parameters:
- `master_filename` (str): Path to the master file.

#### Returns:
- `list`: List of filenames.

---

## Command-Line Arguments

The `__main__.py` module supports the following CLI arguments:

### Main Arguments:
- `datafile` (str): Name of the input file(s) with data.
- `-ap`, `--alphap` (float): Momentum compaction factor or gamma transition.
- `-r`, `--refion` (str): Reference ion (e.g., `72Ge+35`).
- `-psim`, `--filep` (str): File containing particles to simulate.
- `-hrm`, `--harmonics` (float): Harmonics to simulate.

### Secondary Arguments:
- `-n`, `--nions` (int): Number of ions to display, sorted by yield.

### Exclusive Mode Arguments:
- `-b`, `--brho` (float): Brho value of the reference nucleus.
- `-ke`, `--kenergy` (float): Kinetic energy of the reference nucleus.
- `-gam`, `--gamma` (float): Lorentz factor gamma of the reference particle.
- `-f`, `--fref` (float): Revolution frequency of the reference particle.

### Visualization Arguments:
- `-d`, `--ndivs` (int): Number of divisions in the display.
- `-am`, `--amplitude` (int): Display scaling option.
- `-s`, `--show`: Show the display (default: save and close).
- `-w`, `--ods`: Write results to an ODS file.

### Other Arguments:
- `-l`, `--log` (str): Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- `-o`, `--outdir` (str): Output directory.
- `-c`, `--correct` (list): Polynomial correction parameters.

---

## Example Usage

### Run a Simulation with Visualization:
```bash
python -m rionid --datafile input.dat -ap 0.5 -r 72Ge+35 -f 1e6 -s
```