import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QGroupBox, QGridLayout
from PyQt5.QtCore import Qt, QLoggingCategory, QThread, pyqtSignal, QTimer
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
        QLoggingCategory.setFilterRules('*.warning=false\n*.critical=false') #logging annoying messages
        self.thread = None
        self.initUI()
        

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

        self.harmonics_label = QLabel('Harmonics:')
        self.harmonics_edit = QLineEdit()

        self.refion_label = QLabel('Reference Ion:')
        self.refion_edit = QLineEdit()

        self.mode_label = QLabel('Mode:')
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Bρ', 'Frequency', 'Kinetic Energy'])
        self.value_label = QLabel('Value:')
        self.value_edit = QLineEdit()

        self.ndivs_label = QLabel('Number of divisions:')
        self.ndivs_edit = QLineEdit()
        self.amplitude_label = QLabel('Amplitude:')
        self.amplitude_edit = QLineEdit()

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.alphap_label)
        hbox3.addWidget(self.alphap_edit)

        hboxH = QHBoxLayout()
        hboxH.addWidget(self.harmonics_label)
        hboxH.addWidget(self.harmonics_edit)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.refion_label)
        hbox4.addWidget(self.refion_edit)

        hbox_mode_value = QHBoxLayout()
        hbox_mode_value.addWidget(self.mode_label)
        hbox_mode_value.addWidget(self.mode_combo)
        hbox_mode_value.addWidget(self.value_edit)
        
        self.vbox.addLayout(hbox3)
        self.vbox.addLayout(hboxH)
        self.vbox.addLayout(hbox4)
        self.vbox.addLayout(hbox_mode_value)
        
        self.Optional_features_group = QGroupBox("Optional Features")
        self.Optional_features_group.setCheckable(True)
        self.Optional_features_group.setChecked(False)
        self.Optional_features_group.toggled.connect(self.toggle_Optional_features)
        Optional_vbox = QVBoxLayout()
        Optional_vbox.addWidget(self.ndivs_label)
        Optional_vbox.addWidget(self.ndivs_edit)
        Optional_vbox.addWidget(self.amplitude_label)
        Optional_vbox.addWidget(self.amplitude_edit)
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

        self.stop_button = QPushButton('Stop')
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #d1cc01;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.stop_button.clicked.connect(self.stop_script)
        self.stop_button.setEnabled(False)

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
        hbox_buttons.addWidget(self.stop_button)
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
        self.stop_button.setEnabled(False)
    
    def handle_error(self, error_message):
        QMessageBox.critical(None, 'Simulation Error', f'An error occurred: {error_message}')

    def run_script(self):
        if not self.thread:
            self.thread = ScriptThread(self.actual_run_script)
            self.thread.signalError.connect(self.handle_error)
            self.thread.start()
            self.thread.finished.connect(self.thread_complete)
            self.stop_button.setEnabled(True)

    def stop_script(self):
        if self.thread:
            self.thread.requestStop()
            self.thread.wait()
            self.stop_button.setEnabled(False)

    def actual_run_script(self):
        try:
            print('HOLA')
            datafile = self.datafile_edit.text()
            alphap = self.alphap_edit.text()
            refion = self.refion_edit.text()
            filep = self.filep_edit.text()
            ndivs = self.ndivs_edit.text()
            amplitude = self.amplitude_edit.text()
            mode = self.mode_combo.currentText()
            value = self.value_edit.text()

            args = argparse.Namespace(datafile=datafile, alphap=alphap, refion=refion, filep=filep, ndivs=ndivs, amplitude=amplitude, mode=mode, value=value)
            controller(args)

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            log.error(f"Failed to run script: {str(e)}")
            self.signalError.emit(str(e))

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

def controller(datafile=None, alphap=None, refion=None, filep=None, ndivs=None, amplitude=None, mode=None, value=None):
    print('HELLO!')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RionID_GUI()
    window.show()
    sys.exit(app.exec_())