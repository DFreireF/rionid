## CreateGUI Class Documentation

The provided Python code defines a class `CreateGUI` that implements the View component of the Model-View-Controller (MVC) design pattern. It is designed to visualize and analyze Schottky spectra data using ROOT (a data analysis framework) in combination with other Python modules (`barion.patternfinder`, `pysimtof.pypeaks`, and `pysimtof.importdata`).

### Class: CreateGUI

#### Constructor:
- `__init__(self, ref_ion, ion_names, ndivs, yield_option, show)`: Constructor to initialize the CreateGUI object.
  - Parameters:
    - `ref_ion`: A string representing the reference ion.
    - `ion_names`: A list of strings containing names of ions corresponding to the experimental data.
    - `ndivs`: An integer specifying the number of divisions for displaying histograms.
    - `yield_option`: An integer representing the yield option.
    - `show`: A boolean value indicating whether to display the GUI or save the output to a file.

#### Methods:

1. `_view(self, exp_data, simulated_data_dict, filename='Spectrum', out='')`: Visualizes the data by creating and customizing the GUI elements, such as canvas, histograms, stack, and legends.
   - Parameters:
     - `exp_data`: A numpy array representing experimental data.
     - `simulated_data_dict`: A dictionary containing simulated data for various keys.
     - `filename`: A string representing the base filename to save the output.
     - `out`: A string representing the output path.
   - Returns: None

2. `create_canvas(self)`: Creates and initializes the main and peaks canvas for plotting histograms.
   - Parameters: None
   - Returns: None

3. `create_histograms(self, exp_data, simulated_data_dict, filename)`: Creates histograms for experimental and simulated data.
   - Parameters:
     - `exp_data`: A numpy array representing experimental data.
     - `simulated_data_dict`: A dictionary containing simulated data for various keys.
     - `filename`: A string representing the base filename.
   - Returns: None

4. `histogram_fill(self)`: Fills the histograms with the corresponding data values.
   - Parameters: None
   - Returns: None

5. `set_xranges(self)`: Sets the x-axis ranges for dividing the histograms.
   - Parameters: None
   - Returns: None

6. `set_yscales(self)`: Sets the y-axis scales for the histograms and normalizes simulated data.
   - Parameters: None
   - Returns: None

7. `create_stack(self, simulated_data_dict)`: Creates a stack of histograms for simulated data.
   - Parameters:
     - `simulated_data_dict`: A dictionary containing simulated data for various keys.
   - Returns: None

8. `set_xy_ranges(self, stack, rang)`: Sets the x and y-axis ranges for the stack of histograms.
   - Parameters:
     - `stack`: The stack name.
     - `rang`: A tuple containing the minimum and maximum values for the x and y-axes.
   - Returns: None

9. `draw_histograms(self)`: Draws the histograms, stack, and labels on the canvas.
   - Parameters: None
   - Returns: None

10. `set_legend(self, legend)`: Sets the properties of the legend.
    - Parameters:
      - `legend`: The TLegend object to be configured.
    - Returns: None

11. `stack_format(self, stack)`: Sets the formatting for the stack of histograms.
    - Parameters:
      - `stack`: The stack object to be formatted.
    - Returns: None

12. `histogram_format(self, histogram, color, name)`: Sets the formatting for individual histograms.
    - Parameters:
      - `histogram`: The histogram object to be formatted.
      - `color`: An integer representing the color of the histogram.
      - `name`: A string representing the name of the histogram.
    - Returns: None

13. `create_labels(self, key, color)`: Creates labels for peaks found in the data.
    - Parameters:
      - `key`: A string representing the key for the simulated data.
      - `color`: An integer representing the color of the label.
    - Returns: None

14. `set_peaks(self, key)`: Fits peaks in the histogram data.
    - Parameters:
      - `key`: A string representing the key for the simulated data.
    - Returns: An array containing peak values.

15. `set_peak_labels(self, xpeaks, key, color)`: Sets the labels for the identified peaks.
    - Parameters:
      - `xpeaks`: An array containing peak values.
      - `key`: A string representing the key for the simulated data.
      - `color`: An integer representing the color of the label.
    - Returns: None

16. `set_peak_label(self, xpeak, key, color)`: Sets the properties of individual peak labels.
    - Parameters:
      - `xpeak`: A peak value.
      - `key`: A string representing the key for the simulated data.
      - `color`: An integer representing the color of the label.
    - Returns: None

17. `draw_label(self, label, color)`: Draws peak labels on the canvas.
    - Parameters:
      - `label`: The label to be drawn.
      - `color`: An integer representing the color of the label.
    - Returns: None

18. `canvas_cd(self, frec, index)`: Checks whether the frequency belongs to the specified range.
    - Parameters:
      - `frec`: A frequency value to be checked.
      - `index`: The index corresponding to the xrange_divs.
    - Returns: True if the frequency belongs to the specified range, False otherwise.

19. `label_format(self, label, refion, color)`: Sets the formatting for peak labels.
    - Parameters:
      - `label`: The label to be formatted.
      - `refion`: A boolean indicating whether the label belongs to the reference ion.
      - `color`: An integer representing the color of the label.
    - Returns: None

20. `add_legend(self, histogram, key)`: Adds histogram entries to the legend.
    - Parameters:
      - `histogram`: The histogram object to be added to the legend.
      - `key`: A string representing the key for the simulated data.
    - Returns: None

21. `save_pdf(self, name)`: Saves the canvas as a PDF file.
    - Parameters:
      - `name`: The filename to save the PDF.
    - Returns: None

22. `save_root(self, name)`: Saves the canvas as a ROOT file.
    - Parameters:
      - `name`: The filename to save the ROOT file.
    - Returns: None