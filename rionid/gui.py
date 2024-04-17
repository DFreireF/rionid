import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QGroupBox, QGridLayout
from PyQt5.QtCore import Qt, QLoggingCategory
import argparse
import os
import logging as log
from rionid.importdata import ImportData
from rionid.creategui import CreateGUI

class RionID_GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RionID Controller')
        self.setGeometry(100, 100, 600, 400)  # Set window size
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 18pt;
            font-family = Times;
        """)
        #logging annoying messages
        QLoggingCategory.setFilterRules('*.warning=false\n*.critical=false')
        self.initUI()

    def initUI(self):
        self.datafile_label = QLabel('Experimental Data File:')
        self.datafile_edit = QLineEdit()
        self.datafile_button = QPushButton('Browse')
        self.datafile_button.clicked.connect(self.browse_datafile)

        self.alphap_label = QLabel('<i>&alpha;<sub>p</sub> or &gamma;<sub>t</sub> :</i>')
        self.alphap_edit = QLineEdit()

        self.harmonics_label = QLabel('Harmonics:')
        self.harmonics_edit = QLineEdit()

        self.refion_label = QLabel('Reference Ion:')
        self.refion_edit = QLineEdit()

        self.filep_label = QLabel('.lpp File:')
        self.filep_edit = QLineEdit()
        self.filep_button = QPushButton('Browse')
        self.filep_button.clicked.connect(self.browse_lppfile)

        self.mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Bρ', 'Frequency', 'Kinetic Energy'])
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)
        self.value_label = QLabel('Value:')
        self.value_edit = QLineEdit()

        self.ndivs_label = QLabel('Number of divisions:')
        self.ndivs_edit = QLineEdit()

        self.amplitude_label = QLabel('Amplitude:')
        self.amplitude_edit = QLineEdit()

        self.show_checkbox = QPushButton('Show Display')
        self.show_checkbox.setCheckable(True)

        self.run_button = QPushButton('Run')
        self.run_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.run_button.clicked.connect(self.run_script)

        self.exit_button = QPushButton('Exit')
        self.exit_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.exit_button.clicked.connect(self.close)

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.datafile_label)
        hbox1.addWidget(self.datafile_edit)
        hbox1.addWidget(self.datafile_button)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.filep_label)
        hbox2.addWidget(self.filep_edit)
        hbox2.addWidget(self.filep_button)
        vbox.addLayout(hbox2)

        hbox_mode_value = QHBoxLayout()
        hbox_mode_value.addWidget(self.mode_label)
        hbox_mode_value.addWidget(self.mode_combo)
        hbox_mode_value.addWidget(self.value_edit)
        vbox.addLayout(hbox_mode_value)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.alphap_label)
        hbox3.addWidget(self.alphap_edit)
        vbox.addLayout(hbox3)

        hboxH = QHBoxLayout()
        hboxH.addWidget(self.harmonics_label)
        hboxH.addWidget(self.harmonics_edit)
        vbox.addLayout(hboxH)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.refion_label)
        hbox4.addWidget(self.refion_edit)
        vbox.addLayout(hbox4)

        # Collapsible Optional Features
        self.Optional_features_group = QGroupBox("Optional Features")
        self.Optional_features_group.setCheckable(True)
        self.Optional_features_group.setChecked(False)
        self.Optional_features_group.toggled.connect(self.toggle_Optional_features)

        Optional_vbox = QVBoxLayout()
        self.ndivs_label = QLabel('Number of divisions:')
        self.ndivs_edit = QLineEdit()
        self.amplitude_label = QLabel('Amplitude:')
        self.amplitude_edit = QLineEdit()
        Optional_vbox.addWidget(self.ndivs_label)
        Optional_vbox.addWidget(self.ndivs_edit)
        Optional_vbox.addWidget(self.amplitude_label)
        Optional_vbox.addWidget(self.amplitude_edit)
        self.Optional_features_group.setLayout(Optional_vbox)
        vbox.addWidget(self.Optional_features_group)

        vbox.addWidget(self.show_checkbox)

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.run_button)
        hbox_buttons.addWidget(self.exit_button)
        vbox.addLayout(hbox_buttons)

        self.setLayout(vbox)

    def browse_datafile(self):
        options = QFileDialog.Options()
        datafile, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "All Files (*);;Text Files (*.txt)", options=options)
        if datafile:
            self.datafile_edit.setText(datafile)

    def browse_lppfile(self):
        options = QFileDialog.Options()
        lppfile, _ = QFileDialog.getOpenFileName(self, "Select .lpp File", "", "All Files (*);;LPP Files (*.lpp)", options=options)
        if lppfile:
            self.filep_edit.setText(lppfile)

    def mode_changed(self, index):
        if index != -1:
            mode = self.mode_combo.currentText()
            self.value_label.setText(f'{mode}:')

    def toggle_Optional_features(self, checked):
        self.ndivs_label.setVisible(checked)
        self.ndivs_edit.setVisible(checked)
        self.amplitude_label.setVisible(checked)
        self.amplitude_edit.setVisible(checked)

    def run_script(self):
        try:
            datafile = self.datafile_edit.text()
            alphap = self.alphap_edit.text()
            refion = self.refion_edit.text()
            filep = self.filep_edit.text()
            ndivs = self.ndivs_edit.text()
            amplitude = self.amplitude_edit.text()
            show = self.show_checkbox.isChecked()
            mode = self.mode_combo.currentText()
            value = self.value_edit.text()

            args = argparse.Namespace(datafile=datafile, alphap=alphap, refion=refion, filep=filep, ndivs=ndivs, amplitude=amplitude,   show=show, mode=mode, value=value)
            controller(args)
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            log.error(f"Failed to run script: {str(e)}")

def controller(data_file, particles_to_simulate, alphap, ref_ion, ndivs, amplitude, show, brho = None, fref = None, ke = None, out = None, harmonics = None, gam = None, correct = None, ods = False, nions = None):
    
    log.debug(f'Tracking of variables introduced:\n {data_file} = data_file, {particles_to_simulate} = particles_to_simulate, {harmonics} = harmonics, {alphap} = alphap, {ref_ion} = ref_ion, {ndivs} = ndivs, {amplitude} = amplitude, {show} = show, {brho} = brho, {fref} = fref, {ke} = ke')
    # Calculations
    mydata = ImportData(ref_ion, alphap, filename = data_file)
    log.debug(f'Experimental data = {mydata.experimental_data}')
    mydata._set_particles_to_simulate_from_file(particles_to_simulate)
    
    mydata._calculate_moqs()
    log.debug(f'moqs = {mydata.moq}')
    mydata._calculate_srrf(fref = fref, brho = brho, ke = ke, gam = gam, correct = correct)
    log.debug(f'Revolution (or meassured) frequency of {ref_ion} = {mydata.ref_frequency}')
    mydata._simulated_data(harmonics = harmonics) # -> simulated frecs

    log.debug(f'Simulation results (ordered by frequency) = ')
    sort_index = argsort(mydata.srrf)
    for i in sort_index:
        log.debug(f'{mydata.nuclei_names[i]} with simulated rev freq: {mydata.srrf[i] * mydata.ref_frequency} and yield: {mydata.yield_data[i]}')
    if ods: write_arrays_to_ods('Data_simulated_RionID', 'Data', ['Name', 'freq', 'yield'], (mydata.nuclei_names)[sort_index], (mydata.srrf)[sort_index] * mydata.ref_frequency, (mydata.yield_data)[sort_index] )
    log.info(f'Simulation performed. Now we are going to start the display.')

    # View

    # Some extra controlling
    # displaying specified amount of ions, sorted by yield
    if nions:
        # sort by yield (greatest first)
        sorted_indices = argsort(mydata.yield_data)[::-1][:nions]
        ref_index = where(mydata.nuclei_names == ref_ion)[0]
        sorted_indices = append(sorted_indices, ref_index)
        mydata.nuclei_names = mydata.nuclei_names[sorted_indices]
        if harmonics:
            for harmonic in harmonics: # for each harmonic
                name = f'{harmonic}'
                mydata.simulated_data_dict[name] = mydata.simulated_data_dict[name][sorted_indices]
        else:
            mydata.simulated_data_dict['Meassured'] = mydata.simulated_data_dict['Meassured'][sorted_indices]

    mycanvas = CreateGUI(ref_ion, mydata.nuclei_names, ndivs, amplitude, show)
    mycanvas._view(mydata.experimental_data, mydata.simulated_data_dict, filename = data_file, out = out)

    log.debug(f'Plotted labels = {mycanvas.labels},{mycanvas.ref_ion}')
    log.info(f'Program has ended. I hope you have found what you were looking for. :)')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RionID_GUI()
    window.show()
    sys.exit(app.exec_())