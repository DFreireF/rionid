# PyQtGraph GUI Module

The `pyqtgraphgui.py` module defines the `CreatePyGUI` class, which provides a graphical interface for visualizing experimental and simulated data using PyQt5 and PyQtGraph. It serves as the **View** in the Model-View-Controller (MVC) design pattern.

## Class

### `CreatePyGUI`

The `CreatePyGUI` class is a PyQt5-based GUI for visualizing Schottky signals. It uses PyQtGraph for plotting experimental and simulated data and provides interactive tools for data exploration.

#### Constructor: `__init__(self)`

Initializes the `CreatePyGUI` instance and sets up the user interface.

---

## Methods

### User Interface

#### `setup_ui(self)`
Sets up the main user interface, including the plot widget, labels, and control buttons.

---

### Data Visualization

#### `plot_all_data(self, data)`
Plots both experimental and simulated data.

#### Parameters:
- `data`: Data object containing experimental and simulated data.

---

#### `plot_experimental_data(self, data)`
Plots the experimental data on the graph.

#### Parameters:
- `data`: Data object containing experimental data.

---

#### `plot_simulated_data(self, data)`
Plots the simulated data on the graph, including vertical lines and labels for harmonics.

#### Parameters:
- `data`: Data object containing simulated data.

---

#### `updateData(self, data)`
Updates the visualization with new data.

#### Parameters:
- `data`: Data object containing experimental and simulated data.

---

### Data Clearing

#### `clear_simulated_data(self)`
Clears all simulated data from the plot.

---

#### `clear_experimental_data(self)`
Clears all experimental data from the plot.

---

### Data Interaction

#### `toggle_simulated_data(self)`
Toggles the visibility of simulated data on the plot.

---

#### `mouse_moved(self, evt)`
Tracks the mouse position on the plot and displays the cursor coordinates.

#### Parameters:
- `evt`: Mouse event.

---

#### `save_selected_data(self)`
Saves the data within the currently selected range on the plot to a `.npz` file.

---

#### `reset_view(self)`
Resets the plot view to the original X and Y ranges.

---

### Buttons and Controls

#### `add_buttons(self, main_layout)`
Adds control buttons to the GUI, including:
- **Toggle Simulated Data**: Toggles the visibility of simulated data.
- **Save Selected Data**: Saves the currently selected data range.
- **Zoom In/Out**: Zooms in or out on the plot.
- **Reset View**: Resets the plot to its original view.

---

## Features

### Plot Customization
- **Logarithmic Y-Axis**: Enables logarithmic scaling for the Y-axis.
- **Custom Labels**: Adds axis labels and adjusts font sizes for better readability.
- **Legend**: Displays a legend for experimental and simulated data.

### Interactive Tools
- **Mouse Tracking**: Displays the cursor position on the plot.
- **Zoom and Pan**: Allows zooming and panning on the plot.
- **Data Saving**: Saves selected data to a file for further analysis.

---

## Dependencies

The `pyqtgraphgui.py` module relies on the following libraries:
- **PyQt5**: For creating the graphical user interface.
- **PyQtGraph**: For plotting and visualizing data.
- **Numpy**: For numerical operations.

---

## Example Usage

### Running the GUI:
```python
from PyQt5.QtWidgets import QApplication
from rionid.pyqtgraphgui import CreatePyGUI
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CreatePyGUI()
    gui.show()
    sys.exit(app.exec_())

# Example data
experimental_data = {
    "experimental_data": [np.array([1, 2, 3]), np.array([10, 20, 30])]
}
simulated_data = {
    "simulated_data_dict": {
        "1.0": [["241.1", "0.5", "80Kr+35"], ["242.7", "0.4", "79Br+35"]]
    }
}

# Update the GUI with data
gui.updateData(experimental_data)
gui.plot_simulated_data(simulated_data)
```