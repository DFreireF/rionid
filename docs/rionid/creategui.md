# CreateGUI Module

The `creategui.py` module defines the `CreateGUI` class, which is responsible for visualizing experimental and simulated data using ROOT histograms. It follows the Model-View-Controller (MVC) design pattern, where this class serves as the **View**.

## Class

### `CreateGUI`

The `CreateGUI` class provides methods to create, format, and display histograms for experimental and simulated data. It also supports saving the visualizations to files.

#### Constructor: `__init__(self, ref_ion, ion_names, ndivs, yield_option, show)`

Initializes the `CreateGUI` instance.

#### Parameters:
- `ref_ion` (str): The reference ion used in the simulation.
- `ion_names` (list): List of ion names to display.
- `ndivs` (int): Number of divisions for the histogram display.
- `yield_option` (int): Determines how the yield is displayed (e.g., scaled or constant height).
- `show` (bool): Whether to display the visualization interactively.

---

## Methods

### `_view(self, exp_data, simulated_data_dict, filename='Spectrum', out='')`

Main method to create and display the visualization.

#### Workflow:
1. Creates ROOT canvases and histograms.
2. Fills histograms with experimental and simulated data.
3. Sets axis ranges and scales.
4. Draws histograms and overlays simulated data on experimental data.
5. Displays the visualization interactively or saves it to a file.

---

### `create_canvas(self)`

Creates ROOT canvases for displaying histograms.

---

### `create_histograms(self, exp_data, simulated_data_dict, filename)`

Creates histograms for experimental and simulated data.

#### Parameters:
- `exp_data` (array): Experimental data.
- `simulated_data_dict` (dict): Simulated data for each harmonic.
- `filename` (str): Name of the histogram.

---

### `histogram_fill(self)`

Fills the histograms with data.

---

### `set_xranges(self)`

Divides the x-axis into ranges based on the number of divisions (`ndivs`).

---

### `set_yscales(self)`

Sets the y-axis scales for the histograms, including logarithmic scaling if applicable.

---

### `create_stack(self, simulated_data_dict)`

Creates a stack of histograms for simulated data.

#### Parameters:
- `simulated_data_dict` (dict): Simulated data for each harmonic.

---

### `draw_histograms(self)`

Draws the histograms on the ROOT canvases and overlays simulated data on experimental data.

---

### `set_legend(self, legend)`

Formats the legend for the visualization.

#### Parameters:
- `legend` (TLegend): ROOT legend object.

---

### `histogram_format(self, histogram, color, name)`

Formats individual histograms.

#### Parameters:
- `histogram` (TH1D/TH1F): ROOT histogram object.
- `color` (int): Color for the histogram.
- `name` (str): Name of the histogram.

---

### `create_labels(self, key, color)`

Creates labels for peaks in the histograms.

#### Parameters:
- `key` (str): Key identifying the histogram.
- `color` (int): Color for the labels.

---

### `set_peaks(self, key)`

Finds peaks in the histogram using the `FitPeaks` class.

#### Parameters:
- `key` (str): Key identifying the histogram.

#### Returns:
- `list`: List of peak positions.

---

### `set_peak_labels(self, xpeaks, key, color)`

Adds labels to the peaks in the histogram.

#### Parameters:
- `xpeaks` (list): List of peak positions.
- `key` (str): Key identifying the histogram.
- `color` (int): Color for the labels.

---

### `save_pdf(self, name)`

Saves the visualization as a PDF file.

#### Parameters:
- `name` (str): Name of the output file.

---

### `save_root(self, name)`

Saves the visualization as a ROOT file.

#### Parameters:
- `name` (str): Name of the output file.

---

## Dependencies

The `creategui.py` module relies on the following libraries and modules:
- **ROOT**: For creating and managing histograms and canvases.
- **Numpy**: For numerical operations.
- **Datetime**: For timestamping output files.
- **Barion Modules**:
  - `patternfinder`: Provides the `PatternFinder` class for identifying patterns in data.
- **RionID Modules**:
  - `pypeaks`: Provides the `FitPeaks` class for peak fitting.

---

## Example Usage

The `CreateGUI` class is typically used to visualize simulation results. Below is an example of how to use it:

```python
from rionid.creategui import CreateGUI

# Example data
ref_ion = "72Ge+35"
ion_names = ["72Ge+35", "73Ge+35", "74Ge+35"]
ndivs = 4
yield_option = 1
show = True

# Initialize the GUI
gui = CreateGUI(ref_ion, ion_names, ndivs, yield_option, show)

# Example experimental and simulated data
exp_data = ...
simulated_data_dict = ...

# Create and display the visualization
gui._view(exp_data, simulated_data_dict, filename="Spectrum", out="./output/")
```