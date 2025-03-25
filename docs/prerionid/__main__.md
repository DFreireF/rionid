# PreRionID Main Module

The `__main__.py` module in the `prerionid` package serves as the entry point for processing Schottky data files. It provides functionality to analyze IQ data, generate spectrums, and save results in `.csv` or `.npz` formats. The module supports batch processing of multiple files and offers various options for customization.

## Functions

### `write_spectrum_to_csv(freq, power, filename, center=0, out=None)`
Writes the frequency and power spectrum data to a `.csv` file.

#### Parameters:
- `freq` (array): Frequency data.
- `power` (array): Power data.
- `filename` (str): Name of the input file.
- `center` (float, optional): Center frequency (default: `0`).
- `out` (str, optional): Output directory.

#### Workflow:
1. Combines frequency, power, and dBm values into a single array.
2. Saves the data to a `.csv` file with a timestamped filename.

---

### `read_masterfile(master_filename)`
Reads a list of filenames from a master file.

#### Parameters:
- `master_filename` (str): Path to the master file.

#### Returns:
- `list`: List of filenames.

---

### `create_exp_spectrum_csv(filename, time, skip, binning, out=None, fft=None)`
Processes a single file and saves the spectrum data as a `.csv` file.

#### Parameters:
- `filename` (str): Name of the input file.
- `time` (float): Duration of the analysis (in seconds).
- `skip` (float): Time to skip at the beginning of the file (in seconds).
- `binning` (int): Number of frequency bins.
- `out` (str, optional): Output directory.
- `fft` (str, optional): FFT method to use.

---

### `create_exp_spectrum_npz(filename, time, skip, binning, out=None, fft=None)`
Processes a single file and saves the spectrum data as a `.npz` file.

#### Parameters:
- `filename` (str): Name of the input file.
- `time` (float): Duration of the analysis (in seconds).
- `skip` (float): Time to skip at the beginning of the file (in seconds).
- `binning` (int): Number of frequency bins.
- `out` (str, optional): Output directory.
- `fft` (str, optional): FFT method to use.

---

### `main()`
Main function to parse command-line arguments and process files.

#### Workflow:
1. Parses command-line arguments using `argparse`.
2. Validates the output directory.
3. Processes files:
   - If a master file (`.txt`) is provided, processes all files listed in it.
   - Otherwise, processes individual files.
4. Saves the results in `.npz` format.

---

## Command-Line Interface

The `__main__.py` module can be executed as a standalone script. It accepts the following command-line arguments:

### Arguments:

#### Main Arguments:
- `filename` (str): Name of the input file(s) or a master file containing a list of filenames.

#### Data Processing Arguments:
- `-t`, `--time` (float): Duration of the analysis (in seconds).
- `-s`, `--skip` (float): Time to skip at the beginning of the file (in seconds).
- `-b`, `--binning` (int): Number of frequency bins (e.g., `1024`).
- `-ts`, `--timesize` (float): Size of the time bin (in seconds).
- `-m`, `--method` (str): FFT method to use (`npfft`, `fftw`, `welch`, `mtm`). Default: `npfft`.

#### Fancy Arguments:
- `-o`, `--outdir` (str): Output directory. Default: current working directory.
- `-v`, `--verbose`: Increases output verbosity.

---

### Example Usage:

#### Process a Single File:
```bash
python -m prerionid --filename data.iq --time 60 --skip 10 --binning 1024 --outdir ./output