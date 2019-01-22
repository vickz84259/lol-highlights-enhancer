import PySide2.QtWidgets as QtWidgets

from data_manager import DataStore
from watch_highlights import HighlightsWatchThread
import league
import setup_thread
import window
import ws


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self, icon):
        super().__init__(icon)

        self.notification_shown = False
        self.ws_is_running = False

        self.threads = []

        self.init()

    def init(self):
        self.setToolTip('Lol-highlights-enhancer')
        self.activated.connect(self.icon_activated)

        self.checker_thread = league.ProcessCheckerThread()
        self.checker_thread.start()
        self.checker_thread.status.connect(self.process_status)
        self.threads.append(self.checker_thread)

        self.setup_context_menu()

        self.window = window.MainWindow()
        self.window.show()
        self.window.closing_event.connect(self.handle_exit)

        self.preferences = DataStore.get_preferences()
        is_first_time = self.preferences['first_time']

        if not is_first_time:
            self.window.init_UI()

    def setup_context_menu(self):
        context_menu = QtWidgets.QMenu()

        quit_action = context_menu.addAction('Quit')
        quit_action.triggered.connect(self.handle_exit)
        quit_action.triggered.connect(QtWidgets.qApp.quit)

        self.minimize_action = context_menu.addAction('Minimize')
        self.minimize_action.triggered.connect(self.hide_window)

        self.setContextMenu(context_menu)

    def icon_activated(self, reason):
        print(reason)

    def show_window(self):
        context_menu = self.contextMenu()
        context_menu.removeAction(self.show_action)
        context_menu.addAction(self.minimize_action)

        self.window.show()

    def hide_window(self):
        context_menu = self.contextMenu()
        context_menu.removeAction(self.minimize_action)
        self.show_action = context_menu.addAction('Show window')
        self.show_action.triggered.connect(self.show_window)

        self.window.hide()

    def handle_exit(self):
        self.show_notification('The application is closing.')
        for thread in self.threads:
            if thread is not None:
                thread.exit()

    def handle_api_events(self, message):
        uri = message[2]['uri']
        data = message[2]['data']

        if uri == '/lol-gameflow/v1/watch':
            if data == 'WatchInProgress':
                higlights_path = self.preferences['current-highlights-folder']
                self.highlights_thread = HighlightsWatchThread(higlights_path)
                self.highlights_thread.start()

                self.highlights_thread.highlight_created.connect(
                    self.highlight_created)
            else:
                self.highlights_thread.exit()

    def show_notification(self, message):
        self.showMessage('Lol-Highlights-Enhancer', message, self.NoIcon)

    def process_status(self, status):
        self.preferences = DataStore.get_preferences()
        is_first_time = self.preferences['first_time']

        if status == 'not_running':
            if is_first_time and not self.notification_shown:
                msg = 'The League of Legends Client is not running.'
                self.show_notification(msg)
                self.window.status.showMessage(msg)
                self.notification_shown = True
        elif status == 'running' and not self.ws_is_running:
            self.websocket_thread = ws.WebSocketThread()
            self.websocket_thread.start()
            self.websocket_thread.api_event.connect(self.handle_api_events)
            self.threads.append(self.websocket_thread)

            self.ws_is_running = True

            self.setup_thread = setup_thread.Thread(is_first_time)
            self.setup_thread.start()

            self.setup_thread.done_setup.connect(self.window.init_UI)
            self.setup_thread.login_status.connect(
                self.window.status.showMessage)

            self.threads.append(self.setup_thread)
