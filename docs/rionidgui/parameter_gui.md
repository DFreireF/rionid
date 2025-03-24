# Parameter GUI Module

The `parameter_gui.py` module defines the `RionID_GUI` class, which provides the user interface for configuring simulation parameters in the RionID+ application. It also includes the `CollapsibleGroupBox` class for organizing optional features in a collapsible layout.

## Classes

### `RionID_GUI`

The `RionID_GUI` class is a PyQt5 widget that allows users to input and configure simulation parameters. It includes features for saving and loading parameters, browsing files, and running the simulation.

#### Signals:
- `visualization_signal`: Emitted when the simulation is complete, passing the resulting data to the visualization panel.

#### Constructor: `__init__(self)`
Initializes the GUI and loads cached parameters from a TOML file.

---

#### Methods:

##### `initUI(self)`
Initializes the user interface by setting up the layout and loading parameters.

##### `load_parameters(self, filepath='parameters_cache.toml')`
Loads previously saved parameters from a TOML file.

##### `save_parameters(self, filepath='parameters_cache.toml')`
Saves the current parameters to a TOML file for future use.

##### `setup_layout(self)`
Sets up the main layout of the GUI, including file selection, parameter input, and control buttons.

##### `setup_file_selection(self)`
Creates the file selection section for browsing and selecting input files.

##### `setup_parameters(self)`
Creates the parameter input section, including fields for:
- **Alpha or Gamma (`alphap`)**
- **Harmonics**
- **Reference Ion**
- **Mode and Value**
- **Circumference**
- **Number of Ions**
- **Second-Order Correction**

##### `setup_controls(self)`
Creates the control buttons for running the simulation and exiting the application.

##### `browse_datafile(self)`
Opens a file dialog to select the experimental data file.

##### `browse_lppfile(self)`
Opens a file dialog to select the `.lpp` file.

##### `run_script(self)`
Executes the simulation by calling the `import_controller` function with the configured parameters. Emits the `visualization_signal` with the resulting data.

---

### `CollapsibleGroupBox`

The `CollapsibleGroupBox` class provides a collapsible container for organizing optional features in the GUI.

#### Constructor: `__init__(self, title="", parent=None)`
Initializes the collapsible group box with a toggle button and a content area.

#### Methods:
- `on_pressed(self)`: Toggles the visibility of the content area.
- `addWidget(self, widget)`: Adds a widget to the content area.

---

## GUI Layout

### File Selection
- **Experimental Data File**: Browse and select the experimental data file.
- **.lpp File**: Browse and select the `.lpp` file.

### Parameter Input
- **Alpha or Gamma (`alphap`)**: Input field for the alpha or gamma parameter.
- **Harmonics**: Input field for harmonic numbers.
- **Reference Ion**: Input field for the reference ion.
- **Mode and Value**: Dropdown for selecting the mode (`Frequency`, `Bρ`, `Kinetic Energy`) and input field for the corresponding value.
- **Circumference**: Input field for the circumference of the accelerator.
- **Number of Ions**: Input field for the number of ions to display.
- **Second-Order Correction**: Input field for specifying a correction formula.

### Controls
- **Run Button**: Executes the simulation with the configured parameters.
- **Exit Button**: Closes the application.

---

## Example Usage

The `RionID_GUI` class is typically used as part of the main application. Below is an example of how to integrate it:

```python
from PyQt5.QtWidgets import QApplication
from rionidgui.parameter_gui import RionID_GUI

if __name__ == "__main__":
    app = QApplication([])
    gui = RionID_GUI()
    gui.show()
    app.exec_()
```