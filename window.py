import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore


class MainWindow(QtWidgets.QMainWindow):
    closing_event = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lol-Highlights-Enhancer')

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('file')

        self.status = self.statusBar()

        geometry = QtWidgets.QApplication.desktop().availableGeometry(self)
        self.setMinimumSize(geometry.width() * 0.4, geometry.height() * 0.5)

    def closeEvent(self, event):
        self.closing_event.emit()
