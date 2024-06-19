import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from pharmacyAdmin import PharmacyDisplayApp

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(Path('pharmacy.qss').read_text())
    main_win = PharmacyDisplayApp()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
