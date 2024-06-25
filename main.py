import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import *
from pharmacyAdmin import PharmacyDisplayApp

def main():
    app = QApplication(sys.argv)

    style_file = QFile(r'D:\PharmacyQueue\PharmacyQueue\pharmacy.qss')
    style_file.open(QFile.ReadOnly | QFile.Text)
    app.setStyleSheet(style_file.readAll().data().decode("utf-8"))

    # app.setStyleSheet(Path(r'D:\PharmacyQueue\PharmacyQueue\pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
