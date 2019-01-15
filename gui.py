import sys

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import league


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon):
        super().__init__(icon)

        self.notification_shown = False
        self.init()

    def init(self):
        self.setToolTip('Lol-highlights-enhancer')
        self.activated.connect(self.icon_activated)

    def icon_activated(self, reason):
        print(reason)

    def process_status(self, status):
        if status == 'not_running':
            if not self.notification_shown:
                self.showMessage(
                    'League Client Status',
                    'The League of Legends Client is not running.',
                    self.NoIcon)
                self.notification_shown = True
        elif status == 'running':
            pass


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    icon = QtGui.QIcon('resources\\logo.ico')
    system_tray = SystemTrayIcon(icon)
    system_tray.show()

    checker_thread = league.ProcessCheckerThread()
    checker_thread.start()
    checker_thread.status.connect(system_tray.process_status)

    sys.exit(app.exec_())
