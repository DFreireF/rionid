# InOutTools Module

The `inouttools.py` module provides utility functions for reading, processing, and writing experimental data in various formats. These tools are essential for handling input/output operations in the RionID application.

## Functions

### File Reading

#### `read_tdsm_bin(path)`
Reads `.bin_fre`, `.bin_time`, and `.bin_amp` files and processes them into frequency, time, and amplitude arrays.

#### Parameters:
- `path` (str): Path to the `.bin_fre` file (other files must have the same base name).

#### Returns:
- `frequency` (array): Frequency data.
- `time` (array): Time data.
- `amplitude` (array): Amplitude data.

---

#### `handle_read_tdsm_bin(path)`
Processes `.bin` files and returns frequency and averaged amplitude data.

#### Parameters:
- `path` (str): Path to the `.bin_fre` file.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude_avg` (array): Averaged amplitude data.

---

#### `handle_read_rsa_specan_xml(filename)`
Reads and processes `.xml` files from RSA spectrum analyzers.

#### Parameters:
- `filename` (str): Path to the `.xml` file.

#### Returns:
- `freq` (array): Frequency data.
- `power` (array): Normalized power data.

---

#### `handle_read_rsa_data_csv(filename)`
Reads and processes `.csv` files containing RSA data.

#### Parameters:
- `filename` (str): Path to the `.csv` file.

#### Returns:
- `data` (array): Processed data.

---

#### `handle_read_rsa_result_csv(filename)`
Reads and processes `.csv` files containing RSA results.

#### Parameters:
- `filename` (str): Path to the `.csv` file.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude` (array): Amplitude data.

---

#### `handle_tiqnpz_data(filename)`
Processes `.npz` files containing TIQ data.

#### Parameters:
- `filename` (str): Path to the `.npz` file.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude_average` (array): Averaged amplitude data.

---

#### `handle_spectrumnpz_data(filename)`
Processes `.npz` files containing spectrum data.

#### Parameters:
- `filename` (str): Path to the `.npz` file.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude` (array): Amplitude data.

---

#### `handle_prerionidnpz_data(filename)`
Processes `.npz` files containing pre-RionID data.

#### Parameters:
- `filename` (str): Path to the `.npz` file.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude` (array): Amplitude data.

---

#### `read_psdata(filename, dbm=False)`
Reads `.psdata` files and extracts frequency and amplitude data.

#### Parameters:
- `filename` (str): Path to the `.psdata` file.
- `dbm` (bool, optional): Whether to use dBm values for amplitude.

#### Returns:
- `frequency` (array): Frequency data.
- `amplitude` (array): Amplitude data.

---

### File Writing

#### `write_arrays_to_ods(file_name, sheet_name, names, *arrays)`
Writes multiple arrays to an ODS spreadsheet.

#### Parameters:
- `file_name` (str): Name of the output ODS file.
- `sheet_name` (str): Name of the sheet in the ODS file.
- `names` (list): List of column names.
- `*arrays` (list of arrays): Data arrays to write.

#### Workflow:
1. Creates a new ODS spreadsheet.
2. Adds a sheet with the specified name.
3. Writes column names and data arrays to the sheet.
4. Saves the spreadsheet to the specified file.

---

## Workflow

1. **File Reading**:
   - Reads experimental data from various file formats (`.bin`, `.xml`, `.csv`, `.npz`, etc.).
   - Processes the data into frequency, amplitude, and other relevant arrays.

2. **Data Processing**:
   - Normalizes power data.
   - Averages amplitude data across time.

3. **File Writing**:
   - Exports processed data to ODS spreadsheets for further analysis.

---

## Dependencies

The `inouttools.py` module relies on the following libraries:
- **Numpy**: For numerical operations.
- **iqtools**: For reading RSA spectrum analyzer files.
- **ezodf**: For writing ODS spreadsheets.
- **OS**: For file path operations.

---

## Example Usage

### Reading `.bin` Files:
```python
from rionid.inouttools import handle_read_tdsm_bin

frequency, amplitude_avg = handle_read_tdsm_bin("data.bin_fre")
print(f"Frequency: {frequency}")
print(f"Averaged Amplitude: {amplitude_avg}")
```