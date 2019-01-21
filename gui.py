import sys

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import system_tray


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    icon = QtGui.QIcon('resources\\logo.ico')
    tray = system_tray.SystemTrayIcon(icon)
    tray.show()
    sys.exit(app.exec_())
