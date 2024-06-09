import sys
from PyQt5.QtWidgets import QApplication
from rionidgui.gui import RionID_GUI

def main():
    app = QApplication(sys.argv)
    window = RionID_GUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()