import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont


class CreatePyGUI(QMainWindow):
    '''
    PyView (MVC)
    '''
    def __init__(self, exp_data, simulated_data_dict):
        super().__init__()
        self.setWindowTitle('Schottky Signals Identifier')
        self.setGeometry(100, 100, 800, 600)

        #self.exp_data = exp_data
        self.simulated_data = simulated_data_dict
        self.simulated_items = []

        # Create the main widget for the plot
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        main_layout = QVBoxLayout(self.main_widget)

        # Create the plot widget
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)

        # Plot experimental data
        self.x_exp, self.z_exp = exp_data[:, 0], exp_data[:, 1]
        self.plot_widget.plot(self.x_exp, self.z_exp, pen=pg.mkPen('white', width=3))

        # Adding simulated data
        self.add_simulated_data()

        # Add control buttons
        self.add_buttons(main_layout)

    def add_simulated_data(self):
        max_z = self.z_exp.max()
        for i, (harmonic, data) in enumerate(self.simulated_data.items()):
            color = pg.intColor(int(float(harmonic))+i, hues=len(self.simulated_data))
            for entry in data:
                freq = float(entry[0])
                label = entry[2]
                # Vertical line
                line = self.plot_widget.plot([freq, freq], [10, max_z], pen=pg.mkPen(color=color, width=2))
                # Text label at top
                text = pg.TextItem(text=label, color=color, anchor=(0.5, 0))
                self.plot_widget.addItem(text)
                text.setPos(freq, max_z*1.05)
                self.simulated_items.extend([line, text])

    def toggle_simulated_data(self):
        for item in self.simulated_items:
            item.setVisible(not item.isVisible())

    def toggle_y_scale(self):
        axis = self.plot_widget.getPlotItem().getAxis('left')
        is_log_scale = axis.logMode
        if not is_log_scale:
            # Switch to log scale
            axis.setLogMode(True)
            self.plot_widget.getPlotItem().setYRange(1, np.log10(self.z_exp.max()), padding=0.1)
        else:
            # Switch back to linear scale
            axis.setLogMode(False)
            self.plot_widget.getPlotItem().setYRange(self.z_exp.min()+1, self.z_exp.max(), padding=0.1)

    def save_selected_data(self):
        selected_range = self.plot_widget.getViewBox().viewRange()[0]
        mask = (self.x_exp >= selected_range[0]) & (self.x_exp <= selected_range[1])
        selected_data = self.z_exp[mask]
        selected_x = self.x_exp[mask]
        filename = 'selected_data.npz'
        np.savez(filename, x=selected_x, z=selected_data)
        print(f"Data saved to {filename}")

    def add_buttons(self, main_layout):
        button_layout = QHBoxLayout()

        font = QFont("EB Garamond", 20)

        toggle_button = QPushButton("Toggle Simulated Data")
        toggle_button.clicked.connect(self.toggle_simulated_data)
        toggle_button.setFont(font)
        button_layout.addWidget(toggle_button)

        save_button = QPushButton("Save Selected Data")
        save_button.clicked.connect(self.save_selected_data)
        save_button.setFont(font)
        button_layout.addWidget(save_button)

        zoom_in_button = QPushButton("Zoom In")
        zoom_in_button.clicked.connect(lambda: self.plot_widget.getViewBox().scaleBy((0.5, 0.5)))
        zoom_in_button.setFont(font)
        button_layout.addWidget(zoom_in_button)

        zoom_out_button = QPushButton("Zoom Out")
        zoom_out_button.clicked.connect(lambda: self.plot_widget.getViewBox().scaleBy((2, 2)))
        zoom_out_button.setFont(font)
        button_layout.addWidget(zoom_out_button)

        toggle_y_scale_button = QPushButton("Toggle Y Scale")
        toggle_y_scale_button.clicked.connect(self.toggle_y_scale)
        toggle_y_scale_button.setFont(font)
        button_layout.addWidget(toggle_y_scale_button)

        main_layout.addLayout(button_layout)


# Example Usage:
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Example data
    experimental_data = np.array([[2.35000019e+08, 9.04612897e-02],
                                  [2.35000057e+08, 9.07298288e-02],
                                  [2.35000095e+08, 9.01448335e-02],
                                  [2.54999905e+08, 9.01264557e-02],
                                  [2.54999943e+08, 9.01772547e-02],
                                  [2.54999981e+08, 9.03425368e-02]])

    simulated_data = {
        '1.0': np.array([['241127381.22165576', '0.00054777', '80Kr+35'],
                         ['242703150.0762615', '0.0048654', '79Br+35']])
    }

    sa = SpectrumAnalyzer(experimental_data, simulated_data)
    sa.show()
    sys.exit(app.exec_())