import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore

from data_manager import DataStore
import utils


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
        self.highlights_list.itemClicked.connect(self.item_clicked)

        hbox.addWidget(self.highlights_list)
        hbox.addLayout(self.setup_details_layout(), 1)

        self.centralWidget().setLayout(hbox)

    def __setup_label_layout(self, name, string=None):

        layout = QtWidgets.QHBoxLayout()

        if string is None:
            string = name.capitalize()
        layout.addWidget(QtWidgets.QLabel(f'{string}:'))

        name_label = QtWidgets.QLabel('')
        layout.addWidget(name_label, 1)
        self.widgets[name] = name_label

        return layout

    def setup_details_layout(self):
        self.widgets = {}

        main_layout = QtWidgets.QVBoxLayout()

        main_layout.addLayout(self.__setup_label_layout('name'))
        main_layout.addLayout(
            self.__setup_label_layout('played_as', 'Played as'))
        main_layout.addLayout(self.__setup_label_layout('patch'))
        main_layout.addLayout(
            self.__setup_label_layout('game_mode', 'Game Mode'))
        main_layout.addLayout(self.__setup_label_layout('win', 'Outcome'))
        main_layout.addLayout(self.__setup_label_layout('size'))

        return main_layout

    def item_clicked(self, item):
        highlight_name = item.text()
        highlight_details = DataStore.get_highlight(highlight_name)

        self.widgets['name'].setText(highlight_details['name'])
        self.widgets['patch'].setText(highlight_details['patch_version'])

        size_in_bytes = highlight_details['fileSizeBytes']
        self.widgets['size'].setText(utils.get_appropriate_size(size_in_bytes))

        self.widgets['played_as'].setText(
            highlight_details.get('played_as', 'Not available'))
        self.widgets['game_mode'].setText(
            highlight_details.get('game_mode', 'Not available'))

        win_condition = highlight_details.get('win')
        if win_condition is None:
            outcome = 'Not available'
        elif win_condition:
            outcome = 'Won'
        else:
            outcome = 'Lost'
        self.widgets['win'].setText(outcome)

    def closeEvent(self, event):
        self.closing_event.emit()
