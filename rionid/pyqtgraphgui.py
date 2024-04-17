import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QLoggingCategory, Qt

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

        #logging annoying messages
        QLoggingCategory.setFilterRules('*.warning=false\n*.critical=false')

        # Create the plot widget
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)

        # Add legend
        self.legend = pg.LegendItem(offset=(-10, 10))  # Adjust offset as needed
        self.legend.setParentItem(self.plot_widget.graphicsItem())

        # Plot experimental data
        self.x_exp, self.z_exp = exp_data[:, 0]*1e-6, exp_data[:, 1] # 1e-6 for having MHz
        self.exp_data_line = self.plot_widget.plot(self.x_exp, self.z_exp, pen=pg.mkPen('white', width=3))
        self.legend.addItem(self.exp_data_line, 'Experimental Data')
        self.plot_widget.setLabel(
            "left",
            '<span style="color: white; font-size: 20px">Amplitude (arb. units)</span>'
        )
        self.plot_widget.setLabel(
            "bottom",
            '<span style="color: white; font-size: 20px">Frequency (MHz)</span>'
        )
        # Set the initial X-range to encompass all experimental data
        self.initial_x_range = (min(self.x_exp), max(self.x_exp))
        self.plot_widget.setXRange(*self.initial_x_range, padding=0.05)

        # Customizing tick label font size
        font_ticks = QFont()
        font_ticks.setPixelSize(20)  # Set the desired font size here
        self.plot_widget.getAxis('bottom').setTickFont(font_ticks)
        self.plot_widget.getAxis("bottom").setStyle(tickTextOffset = 15)
        self.plot_widget.getAxis('left').setTickFont(font_ticks)
        self.plot_widget.getAxis("left").setStyle(tickTextOffset = 15)

        # Cursor position label
        font = QFont("Times", 12)
        self.cursor_pos_label = QLabel(self)
        self.cursor_pos_label.setFont(font)
        main_layout.addWidget(self.cursor_pos_label)
        self.proxy = pg.SignalProxy(self.plot_widget.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_moved)

        # Adding simulated data
        self.add_simulated_data()

        # Add control buttons
        self.add_buttons(main_layout)

    def add_simulated_data(self):
        max_z = self.z_exp.max()
        min_z = np.min(self.z_exp[self.z_exp > 0])
        for i, (harmonic, data) in enumerate(self.simulated_data.items()):
            color = pg.intColor(int(float(harmonic))+i, hues=len(self.simulated_data))
            for entry in data:
                freq = float(entry[0])*1e-6
                label = entry[2]
                # Vertical line
                line = self.plot_widget.plot([freq, freq], [min_z, max_z], pen=pg.mkPen(color=color, width=1, style = Qt.DashLine ))
                # Text label at top
                text = pg.TextItem(text=label, color=color, anchor=(0.5, 0))
                self.plot_widget.addItem(text)
                text.setPos(freq, max_z*1.05)
                self.simulated_items.extend([line, text])
            self.legend.addItem(line, f'Harmonic {harmonic}')

    def toggle_simulated_data(self):
        for item in self.simulated_items:
            item.setVisible(not item.isVisible())

    def mouse_moved(self, evt):
        pos = evt[0]  # using signal proxy turns original arguments into a tuple
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mousePoint = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            self.cursor_pos_label.setText(f"Cursor Position: x={mousePoint.x():.8f}, y={mousePoint.y():.2f}")

    def save_selected_data(self):
        selected_range = self.plot_widget.getViewBox().viewRange()[0]
        mask = (self.x_exp >= selected_range[0]) & (self.x_exp <= selected_range[1])
        selected_data = self.z_exp[mask]
        selected_x = self.x_exp[mask]
        filename = 'selected_data.npz'
        np.savez(filename, x=selected_x, z=selected_data)
        print(f"Data saved to {filename}")

    def reset_view(self):
        # Reset the plot to the original X and Y ranges
        self.plot_widget.setXRange(*self.initial_x_range, padding=0.05)
        self.plot_widget.setYRange(min(self.z_exp), max(self.z_exp), padding=0.05)

    def add_buttons(self, main_layout):
        button_layout = QHBoxLayout()

        font = QFont("Times", 15)
        font.setBold(True)

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

        # Button to reset the plot view
        reset_view_button = QPushButton("Reset View")
        reset_view_button.setFont(font)
        reset_view_button.clicked.connect(self.reset_view)
        button_layout.addWidget(reset_view_button)


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

    sa = CreatePyGUI(experimental_data, simulated_data)
    sa.show()
    sys.exit(app.exec_())