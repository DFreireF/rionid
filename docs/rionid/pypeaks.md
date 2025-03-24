# PyPeaks Module

The `pypeaks.py` module provides tools for peak detection and fitting in histograms using ROOT. It includes the `FitPeaks` class for managing peak finding, background subtraction, and Gaussian fitting, as well as the `gaussians` function for calculating the sum of Gaussian functions.

## Functions

### `gaussians(x, par)`
Calculates the sum of Gaussian functions.

#### Parameters:
- `x` (array-like): Input data.
- `par` (array-like): Parameters for the Gaussian functions.

#### Returns:
- `result` (float): Sum of the Gaussian functions.

#### Workflow:
1. Determines the number of peaks to fit based on the parameters.
2. Calculates the linear part of the function.
3. Adds the contribution of each Gaussian to the result.

---

## Class

### `FitPeaks`

The `FitPeaks` class provides methods for peak detection, background subtraction, and Gaussian fitting in histograms.

#### Constructor: `__init__(self, npeaks, histogram, tofit)`

Initializes the `FitPeaks` instance.

#### Parameters:
- `npeaks` (int): Maximum number of peaks to detect.
- `histogram` (TH1): ROOT histogram to analyze.
- `tofit` (bool): Whether to perform Gaussian fitting.

---

## Methods

### Peak Detection

#### `peak_finding(self)`
Uses `TSpectrum` to detect peaks in the histogram.

#### Returns:
- `xpeaks` (array): Positions of the detected peaks.

---

#### `peak_finding_background(self)`
Detects peaks after subtracting the background.

#### Returns:
- `xpeaks` (array): Positions of the detected peaks.

---

#### `peak_finding2(histogram)`
Performs high-resolution peak detection.

#### Parameters:
- `histogram` (TH1): ROOT histogram to analyze.

#### Returns:
- `fPositionX` (array): X positions of the detected peaks.
- `fPositionY` (array): Y positions of the detected peaks.

---

### Background Subtraction

#### `background(self)`
Estimates the background using `TSpectrum.Background` and a linear fit.

---

#### `get_background_average(histogram_list)`
Calculates the average background from a list of histograms.

#### Parameters:
- `histogram_list` (list): List of ROOT histograms.

#### Returns:
- `hback` (TH1): Average background histogram.

---

### Peak Fitting

#### `n_peakstofit(self)`
Determines the number of peaks to fit and initializes parameters for Gaussian fitting.

#### Returns:
- `n_peakstofit` (int): Number of peaks to fit.

---

#### `peaks_info(self, npeaks)`
Returns information about the detected peaks, sorted by height.

#### Parameters:
- `npeaks` (int): Number of peaks to analyze.

#### Returns:
- `aux2` (array): Array of peak heights and positions.

---

#### `gaussians_fitting(self)`
Performs Gaussian fitting on the histogram.

---

### Visualization

#### `set_canvas(self)`
Creates ROOT canvases for displaying histograms and fitting results.

---

#### `set_ranges(self)`
Sets the X-axis range for the histogram.

---

### Workflow

1. **Peak Detection**:
   - Detects peaks in the histogram using `TSpectrum`.
   - Optionally subtracts the background before peak detection.

2. **Background Subtraction**:
   - Estimates the background using `TSpectrum.Background`.
   - Optionally performs a linear fit to refine the background estimation.

3. **Gaussian Fitting**:
   - Fits the detected peaks with Gaussian functions.
   - Iteratively refines the fit parameters.

4. **Visualization**:
   - Displays the histogram, detected peaks, and fitted Gaussians on ROOT canvases.

---

## Dependencies

The `pypeaks.py` module relies on the following libraries:
- **ROOT**: For histogram manipulation, peak detection, and fitting.
- **Numpy**: For numerical operations.

---

## Example Usage

### Detecting Peaks:
```python
from rionid.pypeaks import FitPeaks

# Example histogram
histogram = ...

# Initialize the FitPeaks object
fit_peaks = FitPeaks(npeaks=5, histogram=histogram, tofit=False)

# Detect peaks
xpeaks = fit_peaks.peak_finding()
print(f"Detected peaks: {xpeaks}")
```