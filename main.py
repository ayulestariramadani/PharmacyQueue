import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from pharmacyAdmin import PharmacyDisplayApp

def main():
    app = QApplication(sys.argv)

    style_file = QFile('pharmacy.qss')
    style_file.open(QFile.ReadOnly | QFile.Text)
    app.setStyleSheet(style_file.readAll().data().decode("utf-8"))

    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
