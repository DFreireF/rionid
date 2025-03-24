# GUI Module

The `gui.py` module defines the main graphical user interface (GUI) for the RionID+ application. It uses PyQt5 to create a split-panel interface for input and visualization.

## Classes

### `MainWindow`

The `MainWindow` class is the main window of the application. It provides a split-panel layout with an input panel on the left and a visualization panel on the right.

#### Constructor: `__init__(self)`

Initializes the main window and its components.

#### Key Features:
- **Window Title**: Sets the title to "RionID+".
- **Dynamic Sizing**: Automatically adjusts the window size to fit the screen dimensions.
- **Splitter Layout**: Divides the window into two panels:
  - **Left Panel**: Contains the input widget (`RionID_GUI`).
  - **Right Panel**: Contains the visualization widget (`CreatePyGUI`).

#### Signals:
- Connects the `visualization_signal` from the `RionID_GUI` input panel to the `update_visualization` method to dynamically update the visualization panel.

---

### `update_visualization(self, data)`

Updates the visualization panel with new data.

#### Parameters:
- `data`: The data to be visualized, passed from the input panel.

#### Workflow:
1. Receives the data from the `RionID_GUI` input panel.
2. Calls the `updateData` method of the `CreatePyGUI` visualization widget to refresh the displayed content.

---

## Dependencies

The `gui.py` module relies on the following libraries and modules:
- **PyQt5**: Provides the GUI framework.
  - Widgets: `QApplication`, `QWidget`, `QSplitter`, etc.
  - Core: `Qt`, `pyqtSignal`, etc.
- **Loguru**: For logging.
- **Numpy**: For numerical operations.
- **RionID Modules**:
  - `rionid.importdata`: Handles data import and processing.
  - `rionid.pyqtgraphgui`: Provides the visualization widget (`CreatePyGUI`).
  - `rionidgui.parameter_gui`: Provides the input widget (`RionID_GUI`).
- **Barion Module**:
  - `barion.amedata`: Handles mass-energy conversions.

---

## Example Usage

The `MainWindow` class is typically instantiated and executed as part of the main application. Below is an example of how to use it:

```python
import sys
from PyQt5.QtWidgets import QApplication
from rionidgui.gui import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
```