import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import PDFProcessorApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFProcessorApp()
    window.show()
    sys.exit(app.exec_())