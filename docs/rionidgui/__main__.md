# Main Module

The `__main__.py` module serves as the entry point for the RionID+ application. It initializes the PyQt5 application and launches the main window.

## Function

### `main()`

The `main()` function initializes the application and displays the main GUI window.

#### Workflow:
1. Creates a `QApplication` instance.
2. Instantiates the `MainWindow` class from the `gui.py` module.
3. Displays the main window using `show()`.
4. Starts the PyQt5 event loop using `app.exec_()`.

---

## Example Usage

The `__main__.py` module is executed directly to start the application. Below is an example of how it works:

```bash
python -m rionidgui
```