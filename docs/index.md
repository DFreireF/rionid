# RionID (Ring-stored ion IDentification) Usage Guide
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://DFreireF.github.io/rionid)[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8169341.svg)](https://doi.org/10.5281/zenodo.8169341)

`RionID` is a Python code that simulates the time-of-flight/revolution-frequency spectrum of particles stored in a storage ring. Here is a guide on how to use `RionID` (for more details please check [dfreiref.github.io/rionid/](https://DFreireF.github.io/rionid/)):

<div class="center">
  <img src="https://github.com/DFreireF/rionid/raw/master/docs/img/rionid.png?raw=true" width="50%">
</div>

## Code Structure

The `RionID` code consists of three main modules:

1. **`prerionid`**: Handles preprocessing of Schottky data and file monitoring.
    - [`__main__.md`](prerionid/__main__.md): Entry point for preprocessing tasks.
    - [`datacrunch.md`](prerionid/datacrunch.md): Multithreaded file processing system.
    - [`e0018.md`](prerionid/e0018.md): Batch processing of IQ files.
    - [`psdata.md`](prerionid/psdata.md): Schottky data processing.
    - [`watcher.md`](prerionid/watcher.md): Directory monitoring for file changes.

2. **`rionid`**: Core simulation and data handling logic.
    - [`__main__.md`](rionid/__main__.md): Entry point for simulation tasks.
    - [`creategui.md`](rionid/creategui.md): Visualization using ROOT.
    - [`importdata.md`](rionid/importdata.md): Handles experimental data and simulations.
    - [`inputtools.md`](rionid/inputtools.md): Utility functions for file input/output.
    - [`pypeaks.md`](rionid/pypeaks.md): Peak detection and fitting.
    - [`pyqtgraphgui.md`](rionid/pyqtgraphgui.md): Visualization using PyQtGraph.

3. **`rionidgui`**: Graphical user interface for interacting with the simulation.
    - [`__main__.md`](rionidgui/__main__.md): Entry point for the GUI.
    - [`gui.md`](rionidgui/gui.md): Main GUI window.
    - [`gui_controller.md`](rionidgui/gui_controller.md): Manages the simulation workflow.
    - [`parameter_gui.md`](rionidgui/parameter_gui.md): GUI for configuring simulation parameters.

## Installation

+ Download and install [Barion](https://github.com/xaratustrah/barion) from [@Xaratustrah](https://github.com/xaratustrah), [LISEreader](https://github.com/gwgwhc/lisereader) from [@gwgwhc](https://github.com/gwgwhc), and [PyROOT](https://root.cern/manual/python/).

+ Download or clone the `RionID` repository:
  ```bash
  git clone https://github.com/DFreireF/rionid.git
  ```

+ Then in the cloned directory:
  ```bash
  pip install .
  ```

## Usage

Navigate to the directory containing the `RionID` code in your terminal.  
Run `python __main__.py [arguments]`, replacing `[arguments]` with the desired arguments (detailed below).

## Arguments

The following arguments are available for use with `RionID`:

#### Main Arguments

+ `datafile` (required): Name of the input file with data. Can also be a list of files in a txt file.
+ `alphap`: Momentum compaction factor of the ring.
+ `refion`: Reference ion with format NucleonsNameChargestate := AAXX+CC. Example: 72Ge+35, 1H+1, 238U+92...
+ `filep`: Read list of particles to simulate. LISE file or something else.

#### Secondary Arguments

+ `harmonics`: Harmonics to simulate.

#### Arguments for Each Mode (Exclusive)

+ `brho`: Brho value of the reference nucleus at ESR (isochronous mode).
+ `kenergy`: Kinetic energy of reference nucleus at ESR (isochronous mode).
+ `gamma`: Lorentz factor gamma of the reference particle.
+ `fref`: Revolution frequency of the reference particle (standard mode).

#### Arguments for Visualization

+ `ndivs`: Number of divisions in the display.
+ `amplitude`: Display of SRF data options. 0 -> constant height, else -> scaled.

#### Actions

+ `log`: Set the logging level.
+ `show`: Show display. If not, save root file and close display.
+ `outdir`: Output directory.
+ `correct`: Correct simulated spectrum following a polynomial fit with parameters given here.

#### Example Usage: Dummy example

```bash
python -m rionid datafile.txt -f 11.2452 -r 209Bi+83 -psim datafile.psim -b 5.5 -d 8 -am 1 -s -o output_folder -c 1 2 3
```

This command would run `RionID` on the `datafile.txt` input file, using the standard mode with a `reference frequency` of 11.2452, a `reference ion` of `209Bi+83`, a particle input file of `datafile.psim`, a `brho` value of `5.5`, and displaying the data with `8 divisions`, `scaled amplitude`, and showing the display. The output files would be saved in the `output_folder` directory, and the `simulated spectrum` would be `corrected` using the polynomial fit parameters 1, 2, and 3.

## Tutorial

[Tutorial](https://github.com/gwgwhc/schottky_analysis_tutorial.git) for introducing yourself to Schottky data analysis by G. Hudson-Chang [@gwgwhc](https://github.com/gwgwhc/).

## Acknowledgements

We acknowledge Dr. RuiJiu Chen ([@chenruijiu](https://github.com/chenruijiu/)) for providing a C++ code for the simulation of time-of-flight, which we used as inspiration for the backbone of this code.  
We acknowledge Dr. Shahab Sanjari ([@xaratustrah](https://github.com/xaratustrah/)) for guiding our software coding, especially in the initial stages.