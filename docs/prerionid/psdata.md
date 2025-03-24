# Process Schottky Data Module

The `psdata.py` module defines the `ProcessSchottkyData` class, which is responsible for processing Schottky data. It provides methods for reading, analyzing, and saving power spectrogram data from IQ files.

## Class

### `ProcessSchottkyData`

The `ProcessSchottkyData` class processes Schottky data from IQ files using various methods such as FFT, Welch, and multitaper methods.

#### Constructor: `__init__(self, filename, skip_time=None, analysis_time=None, binning=None, time_bin_size=None, method='npfft')`

Initializes the `ProcessSchottkyData` instance.

#### Parameters:
- `filename` (str): Path to the IQ file.
- `skip_time` (float, optional): Time to skip at the beginning of the file (in seconds).
- `analysis_time` (float, optional): Duration of the data to analyze (in seconds).
- `binning` (int, optional): Number of samples per bin.
- `time_bin_size` (float, optional): Size of each time bin (in seconds).
- `method` (str, optional): Method for processing the data. Options include:
  - `'npfft'`: Numpy FFT (default).
  - `'fftw'`: FFTW library.
  - `'welch'`: Welch's method.
  - `'mtm'`: Multitaper method.

---

## Methods

### Data Processing

#### `get_exp_data(self)`
Reads and processes the experimental data from the IQ file.

#### Workflow:
1. Reads the IQ data:
   - If `skip_time` and `analysis_time` are provided, reads a specific portion of the data.
   - Otherwise, reads the entire file.
2. Computes the power spectrogram using the specified method.
3. Extracts the frequency and power data:
   - `freq`: Frequency data (adjusted for the center frequency).
   - `power`: Averaged power data.

---

### Data Saving

#### `save_exp_data(self, outdir=None)`
Saves the processed frequency and power data to a `.npz` file.

#### Parameters:
- `outdir` (str, optional): Directory to save the output file. If not provided, saves the file in the same directory as the input file.

#### Workflow:
1. Generates a timestamped filename.
2. Saves the frequency (`x`) and power (`y`) data to a `.npz` file.

---

## Workflow

1. **Initialization**:
   - The IQ file is loaded using the `iqtools` library.
   - Parameters such as binning and time ranges are configured.

2. **Data Processing**:
   - Reads the IQ data and computes the power spectrogram.
   - Extracts and averages the power data over time.

3. **Data Saving**:
   - Saves the processed data to a `.npz` file for further analysis.

---

## Dependencies

The `psdata.py` module relies on the following libraries:
- **iqtools**: For reading and processing IQ files.
- **Numpy**: For numerical operations.
- **Datetime**: For generating timestamped filenames.

---

## Example Usage

### Processing Schottky Data:
```python
from prerionid.psdata import ProcessSchottkyData

# Initialize the processor
processor = ProcessSchottkyData(
    filename="data.iq",
    skip_time=10,
    analysis_time=60,
    time_bin_size=0.1,
    method="npfft"
)

# Process the data
processor.get_exp_data()

# Save the processed data
processor.save_exp_data(outdir="output")
```