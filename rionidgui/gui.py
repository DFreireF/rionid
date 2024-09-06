import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QGroupBox, QGridLayout, QDesktopWidget,  QCheckBox
from PyQt5.QtCore import Qt, QLoggingCategory, QThread, pyqtSignal, QTimer, QEvent
import argparse
import os
import logging as log
from loguru import logger
from numpy import argsort, where, append, shape 
from rionid.importdata import ImportData
from rionid.pyqtgraphgui import CreatePyGUI
import toml
from barion.amedata import AMEData

log.basicConfig(level=log.DEBUG)
class RionID_GUI(QWidget):
    visualization_signal = pyqtSignal(object)
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RionID Controller')
        width = QDesktopWidget().screenGeometry(-1).width()
        height = QDesktopWidget().screenGeometry(-1).height()
        self.setGeometry(100, 100, width, height)  # Set window size
        self.setStyleSheet("""
            background-color: #f0f0f0;
            font-size: 18pt;
            font-family = Times;
        """)
        QLoggingCategory.setFilterRules('*.warning=false\n*.critical=false') #logging annoying messages
        self.thread = None
        self.initUI()
        self.load_parameters()  # Load parameters after initializing UI
        self.visualization_window = None
        self.visualization_signal.connect(self.launch_visualization)
        
    def load_parameters(self, filepath='parameters_cache.toml'):
        try:
            with open(filepath, 'r') as f:
                parameters = toml.load(f)
                self.datafile_edit.setText(parameters.get('datafile', ''))
                self.filep_edit.setText(parameters.get('filep', ''))
                self.alphap_edit.setText(parameters.get('alphap', ''))
                self.harmonics_edit.setText(parameters.get('harmonics', ''))
                self.refion_edit.setText(parameters.get('refion', ''))
                self.circumference_edit.setText(parameters.get('circumference', ''))
                self.mode_combo.setCurrentText(parameters.get('mode', 'Frequency'))
                self.value_edit.setText(parameters.get('value', ''))
                self.reload_data_checkbox.setChecked(parameters.get('reload_data', True))
                self.nions_edit.setText(parameters.get('nions', ''))
        except FileNotFoundError:
            pass  # No parameters file exists yet
        
    def save_parameters(self, filepath='parameters_cache.toml'):
        parameters ={
            'datafile': self.datafile_edit.text(),
            'filep': self.filep_edit.text(),
            'alphap': self.alphap_edit.text(),
            'harmonics': self.harmonics_edit.text(),
            'refion': self.refion_edit.text(),
            'circumference': self.circumference_edit.text(),
            'mode': self.mode_combo.currentText(),
            'value': self.value_edit.text(),
            'reload_data': self.reload_data_checkbox.isChecked(),
            'nions': self.nions_edit.text()
        }
        with open(filepath, 'w') as f:
            toml.dump(parameters, f)
            
    def initUI(self):
        self.setup_layout()
        self.setLayout(self.vbox)

    def setup_layout(self):
        self.vbox = QVBoxLayout()
        self.setup_file_selection()
        self.setup_parameters()
        self.setup_controls()
    
    def setup_file_selection(self):
        self.datafile_label = QLabel('Experimental Data File:')
        self.datafile_edit = QLineEdit()
        self.datafile_button = QPushButton('Browse')
        self.datafile_button.clicked.connect(self.browse_datafile)

        self.filep_label = QLabel('.lpp File:')
        self.filep_edit = QLineEdit()
        self.filep_button = QPushButton('Browse')
        self.filep_button.clicked.connect(self.browse_lppfile)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.datafile_label)
        hbox1.addWidget(self.datafile_edit)
        hbox1.addWidget(self.datafile_button)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.filep_label)
        hbox2.addWidget(self.filep_edit)
        hbox2.addWidget(self.filep_button)

        self.vbox.addLayout(hbox1)
        self.vbox.addLayout(hbox2)

    def setup_parameters(self):
        self.alphap_label = QLabel('<i>&alpha;<sub>p</sub> or &gamma;<sub>t</sub> :</i>')
        self.alphap_edit = QLineEdit()
        
        self.harmonics_label = QLabel('Harmonics (e.g 124 125 126):')
        self.harmonics_edit = QLineEdit()

        self.refion_label = QLabel('Reference Ion with format AAEl+QQ (e.g. 72Ge+32):')
        self.refion_edit = QLineEdit()

        self.mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Frequency', 'Bρ', 'Kinetic Energy'])
        self.value_label = QLabel('Value:')
        self.value_edit = QLineEdit()
        
        self.reload_data_checkbox = QCheckBox('Reload Experimental Data')
        self.reload_data_checkbox.setChecked(True)  # Default is to reload data

        self.circumference_label = QLabel('Circumference (m):')  # Add label for orbit length
        self.circumference_edit = QLineEdit()  # Add QLineEdit for orbit length        
        
        self.nions_label = QLabel('Number of ions to display (e.g. if 5, it will display the 5 most expected fragments):')
        self.nions_edit = QLineEdit()
        self.correction_label = QLabel('Add second order correction to the simulated frequencies with the form: <i>a<sub>0</sub> &middot; x<sup>2</sup> + a<sub>1</sub> &middot; x<sup>1</sup> + a<sub>2</sub> &middot; x<sup>0</sup>:</i>')        
        self.correction_edit = QLineEdit()
        #self.ndivs_label = QLabel('Number of divisions:')
        #self.ndivs_edit = QLineEdit()
        #self.amplitude_label = QLabel('Scale amplitude of the simulated peaks:')
        #self.amplitude_edit = QLineEdit()
        
        hbox_alphap = QHBoxLayout()
        hbox_alphap.addWidget(self.alphap_label)
        hbox_alphap.addWidget(self.alphap_edit)

        hbox_harmonics = QHBoxLayout()
        hbox_harmonics.addWidget(self.harmonics_label)
        hbox_harmonics.addWidget(self.harmonics_edit)
        
        hbox_refion = QHBoxLayout()
        hbox_refion.addWidget(self.refion_label)
        hbox_refion.addWidget(self.refion_edit)

        hbox_circumference = QHBoxLayout()  # Add layout for orbit length
        hbox_circumference.addWidget(self.circumference_label)
        hbox_circumference.addWidget(self.circumference_edit)
        
        hbox_mode_value = QHBoxLayout()
        hbox_mode_value.addWidget(self.mode_label)
        hbox_mode_value.addWidget(self.mode_combo)
        hbox_mode_value.addWidget(self.value_edit)
        
        self.vbox.addWidget(self.reload_data_checkbox)
        self.vbox.addLayout(hbox_circumference)  # Add orbit length layout to the main layout
        self.vbox.addLayout(hbox_alphap)
        self.vbox.addLayout(hbox_harmonics)
        self.vbox.addLayout(hbox_refion)
        self.vbox.addLayout(hbox_mode_value)
        
        self.Optional_features_group = QGroupBox("Optional Features")
        self.Optional_features_group.setCheckable(True)
        self.Optional_features_group.setChecked(False)
        #self.Optional_features_group.toggled.connect(self.toggle_Optional_features)
        Optional_vbox = QVBoxLayout()
        
        Optional_vbox.addWidget(self.nions_label)
        Optional_vbox.addWidget(self.nions_edit)
        Optional_vbox.addWidget(self.correction_label)
        Optional_vbox.addWidget(self.correction_edit)
        #Optional_vbox.addWidget(self.ndivs_label)
        #Optional_vbox.addWidget(self.ndivs_edit)
        #Optional_vbox.addWidget(self.amplitude_label)
        #Optional_vbox.addWidget(self.amplitude_edit)
        self.Optional_features_group.setLayout(Optional_vbox)
        
        self.vbox.addWidget(self.Optional_features_group)

    def setup_controls(self):
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

        hbox_buttons = QHBoxLayout()
        hbox_buttons.addWidget(self.run_button)
        hbox_buttons.addWidget(self.exit_button)
        self.vbox.addLayout(hbox_buttons)

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

    def thread_complete(self):
        self.thread = None
        #self.stop_button.setEnabled(False)
    
    def handle_error(self, error_message):
        QMessageBox.critical(None, 'Simulation Error', f'An error occurred: {error_message}')

    def run_script(self):
        if not self.thread:
            self.thread = ScriptThread(self.actual_run_script)
            self.thread.signalError.connect(self.handle_error)
            self.thread.start()
            self.thread.finished.connect(self.thread_complete)

    def stop_script(self):
        if self.thread:
            self.thread.requestStop()
            self.thread.wait()
            #self.stop_button.setEnabled(False)

    def actual_run_script(self):
        try:
            print("Running script...")
            datafile = self.datafile_edit.text()
            filep = self.filep_edit.text()
            alphap = float(self.alphap_edit.text())
            harmonics = self.harmonics_edit.text()
            refion = self.refion_edit.text()
            circumference = float(self.circumference_edit.text())
            mode = self.mode_combo.currentText()
            value = self.value_edit.text()
            reload_data = self.reload_data_checkbox.isChecked()
            nions = self.nions_edit.text()
            
            args = argparse.Namespace(datafile=datafile or None,
                                      filep=filep or None,
                                      alphap=alphap or None,
                                      harmonics=harmonics or None,
                                      refion=refion or None,
                                      nions=nions or None,
                                      circumference=circumference or None,
                                      mode=mode or None,
                                      value=value or None,
                                      reload_data=reload_data or None)

            # Save parameters before running the script
            self.save_parameters()
            
            data = controller_pyqt(**vars(args))
            if data:
                print("Data generated successfully, posting event...")
                event = CustomEvent(data)
                QApplication.postEvent(self, event)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            log.error("Processing failed", exc_info=True)
            self.signalError.emit(str(e))

    def customEvent(self, event):
        if event.type() == CustomEvent.EventType:
            print("Data is present. Launching visualization...")
            self.launch_visualization(event.data)

    def launch_visualization(self, data):
        # Check for an existing QApplication instance
        if not self.visualization_window:
            self.visualization_window = CreatePyGUI(data)
            self.visualization_window.show()
        else:
            self.visualization_window.updateData(data)
            
class ScriptThread(QThread):
    signalError = pyqtSignal(str)

    def __init__(self, function):
        super().__init__()
        self.function = function
        self._stop_requested = False

    def run(self):
        try:
            if not self._stop_requested:
                self.function()
        except Exception as e:
            self.signalError.emit(str(e))

    def requestStop(self):
        self._stop_requested = True
    
class CustomEvent(QEvent):
    EventType = QEvent.Type(QEvent.registerEventType())

    def __init__(self, data):
        super().__init__(CustomEvent.EventType)
        self.data = data

def controller_pyqt(datafile=None, filep=None, alphap=None, refion=None, harmonics = None, ndivs=None, nions = None, amplitude=None, circumference = None, mode=None, value=None, reload_data=None):
    try:
        # Calculations
        if float(alphap) > 1: alphap = 1/float(alphap)**2 # handling alphap and gammat
        mydata = ImportData(refion, float(alphap), filename = datafile, reload_data = reload_data, circumference = circumference)

        mydata._set_particles_to_simulate_from_file(filep)

        fref = brho = ke = gam = None
        if mode == 'Frequency':
            fref = float(value)
        elif mode == 'Bρ':
            brho = float(value)
        elif mode == 'Kinetic Energy':
            ke = float(value)
        elif mode == 'Gamma':
            gam = float(value)

        mydata._calculate_moqs()
        
        mydata._calculate_srrf(fref = fref, brho = brho, ke = ke, gam = gam, correct = False)
        
        harmonics = [float(h) for h in harmonics.split()]
        mydata._simulated_data(harmonics = harmonics, mode = mode) # -> simulated frecs
        
        if nions:
            display_nions(int(nions), mydata.yield_data, mydata.nuclei_names, mydata.simulated_data_dict, refion, harmonics)
        
        logger.info(f'Simulation results (ordered by frequency) = ')
        sort_index = argsort(mydata.srrf)

        # Save the results to a file with the specified format
        with open('simulation_result.out', 'w') as file:
            for harmonic in harmonics:
                brho = mydata.brho
                header0 = f'Harmonic: {harmonic} , Bp: {brho:.6f} [Tm]'
                #file.write(f'Harmonic: {harmonic} , Bp: {brho:.6f} [Tm]\n')
                logger.info(header0)
                file.write(header0 + '\n')
                
            #header1 = f"{'ion':<15}{'fre[Hz]':<30}{'yield [pps]':<15}"
            header1 = f"{'ion':<15}{'fre[Hz]':<30}{'yield [pps]':<15}{'m/q [u]':<15}{'m [eV]':<15}"
            file.write(header1 + '\n')
            file.write('-' * len(header1) + '\n')
            logger.info(header1)
            for i in sort_index:
                ion = mydata.nuclei_names[i]
                fre = mydata.srrf[i] * mydata.ref_frequency
                yield_ = mydata.yield_data[i]
                moq = mydata.moq[ion]
                mass_u = mydata.total_mass[ion]
                mass = AMEData.to_mev(mass_u)*1e6
                #result_line = f"{ion:<15}{fre:<30.10f}{yield_:<15.4e}"
                result_line = f"{ion:<15}{fre:<30.10f}{yield_:<15.4e}{moq:<15.12f}{mass:<15.3f}"
                logger.info(result_line)
                file.write(result_line + '\n')
        return mydata
    
    except Exception as e:
        print(f"Error during calculations: {str(e)}")
        return None

def display_nions(nions, yield_data, nuclei_names, simulated_data_dict, ref_ion, harmonics):
    sorted_indices = argsort(yield_data)[::-1][:nions]
    ref_index = where(nuclei_names == ref_ion)[0]
    if ref_index not in sorted_indices:
        sorted_indices = append(sorted_indices, ref_index)
    nuclei_names = nuclei_names[sorted_indices]
    
    for harmonic in harmonics: # for each harmonic
        name = f'{harmonic}'
        simulated_data_dict[name] = simulated_data_dict[name][sorted_indices]
