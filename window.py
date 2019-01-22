import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore

from data_manager import DataStore


class MainWindow(QtWidgets.QMainWindow):
    closing_event = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Lol-Highlights-Enhancer')

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu('file')

        self.status = self.statusBar()

        self.setCentralWidget(QtWidgets.QWidget(self))

        geometry = QtWidgets.QApplication.desktop().availableGeometry(self)
        self.setMinimumSize(geometry.width() * 0.4, geometry.height() * 0.5)

    def init_UI(self):
        hbox = QtWidgets.QHBoxLayout()

        self.highlights_list = QtWidgets.QListWidget()
        self.highlights_list.addItems(DataStore.get_highlight_names())

        self.highlight_details = QtWidgets.QListWidget()
        for i in range(10):
            self.highlight_details.addItem('Item %s' % (i + 1))

        hbox.addWidget(self.highlights_list)
        hbox.addWidget(self.highlight_details)

        self.centralWidget().setLayout(hbox)

    def closeEvent(self, event):
        self.closing_event.emit()
