import sys

import PySide2.QtWidgets as QtWidgets
import PySide2.QtGui as QtGui

import league
import ws


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon):
        super().__init__(icon)

        self.notification_shown = False
        self.ws_is_running = False
        self.init()

    def init(self):
        self.setToolTip('Lol-highlights-enhancer')
        self.activated.connect(self.icon_activated)

        self.checker_thread = league.ProcessCheckerThread()
        self.checker_thread.start()
        self.checker_thread.status.connect(self.process_status)

        self.setup_context_menu()

    def setup_context_menu(self):
        context_menu = QtWidgets.QMenu()

        quit_action = context_menu.addAction('Quit')
        quit_action.triggered.connect(self.handle_exit)
        quit_action.triggered.connect(QtWidgets.qApp.quit)

        self.setContextMenu(context_menu)

    def icon_activated(self, reason):
        print(reason)

    def handle_exit(self):
        self.checker_thread.exit()
        self.websocket_thread.exit()

    def process_status(self, status):
        if status == 'not_running':
            if not self.notification_shown:
                self.showMessage(
                    'League Client Status',
                    'The League of Legends Client is not running.',
                    self.NoIcon)
                self.notification_shown = True
        elif status == 'running' and not self.ws_is_running:
            self.websocket_thread = ws.WebSocketThread()
            self.websocket_thread.start()

            self.ws_is_running = True


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    icon = QtGui.QIcon('resources\\logo.ico')
    system_tray = SystemTrayIcon(icon)
    system_tray.show()

    sys.exit(app.exec_())
