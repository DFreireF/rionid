# RionID (Ringed IONs IDentification) Usage Guide
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://DFreireF.github.io/rionid)[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8169341.svg)](https://doi.org/10.5281/zenodo.8169341)



`rionid` is a Python code that simulates the time-of-flight (ToF) spectrum of particles in a storage ring. Here is a guide on how to use pySimToF:

## Installation

+    Download and install [Barion](https://github.com/xaratustrah/barion) from [@Xaratustrah](https://github.com/xaratustrah), [LISEreader](https://github.com/gwgwhc/lisereader) from [@gwgwhc](https://github.com/gwgwhc) and [PyROOT](https://root.cern/manual/python/)

+    Download or clone the `rionid` repository:
  ```bash
    git clone https://github.com/DFreireF/rionid.git
  ```
+    Then in the cloned directory: 
  ```bash
    pip install .
  ```
## Usage

Navigate to the directory containing the `rionid` code in your terminal.
Run `python __main__.py [arguments]`, replacing `[arguments]` with the desired arguments (detailed below).

## Arguments

The following arguments are available for use with `rionid`:
#### Main Arguments

+    `datafile` (required): Name of the input file with data. Can also be a list of files in a txt file.
+    `alphap`: Momentum compaction factor of the ring.
+    `refion`: Reference ion with format NucleonsNameChargestate := AAXX+CC. Example: 72Ge+35, 1H+1, 238U+92...
+    `filep`: Read list of particles to simulate. LISE file or something else.

#### Secondary Arguments

+    `harmonics`: Harmonics to simulate.

#### Arguments for Each Mode (Exclusive)

+    `brho`: Brho value of the reference nucleus at ESR (isochronous mode).
+    `kenergy`: Kinetic energy of reference nucleus at ESR (isochronous mode).
+    `gamma`: Lorentz factor gamma of the reference particle.
+    `fref`: Revolution frequency of the reference particle (standard mode).

#### Arguments for Visualization

+    `ndivs`: Number of divisions in the display.
+    `amplitude`: Display of srf data options. 0 -> constant height, else->scaled.

#### Actions

+    `log`: Set the logging level.
+    `show`: Show display. If not, save root file and close display.
+    `outdir`: Output directory.
+    `correct`: Correct simulated spectrum following a polynomial fit with paremeters given here.

#### Example Usage: Dummy example

```python
    python __main__.py datafile.txt -f 11.2452 -r 209Bi+83 -psim datafile.psim -b 5.5 -d 8 -am 1 -s -o output_folder -c 1 2 3
```

This command would run `rionid` on the `datafile.txt` input file, using the standard mode with a `reference frequency` of 11.2452, a `reference ion` of `209Bi+83`, a particle input file of `datafile.psim`, a `brho` value of `5.5`, and displaying the data with `8 divisions`, `scaled amplitude`, and showing the display. The output files would be saved in the `output_folder directory`, and the `simulated spectrum` would be `corrected` using the polynomial fit parameters 1, 2, and 3.

#### Acknowledgements:
We acknowledge Dr. RuiJiu Chen (@chenruijiu) for providing a c++ code for the simulation of ToF which we used as inspiration for the backbone of this code.

We acknowledge Dr. Shahab Sanajri (@xaratustrah) for the guiding our software coding, specially in the initial stages.
