import sys

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui


def icon_activated(reason):
    print(reason)


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    icon = QtGui.QIcon('resources\\logo.ico')
    system_tray = QtWidgets.QSystemTrayIcon(icon)
    system_tray.setToolTip('Lol-highlights-enhancer')
    system_tray.show()

    system_tray.activated.connect(icon_activated)

    sys.exit(app.exec_())
