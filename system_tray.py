import PySide2.QtWidgets as QtWidgets

from data_manager import DataStore
from watch_highlights import HighlightsWatchThread
import league
import window
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

        self.window = window.MainWindow()
        self.window.show()
        self.window.closing_event.connect(self.handle_exit)

    def setup_context_menu(self):
        context_menu = QtWidgets.QMenu()

        quit_action = context_menu.addAction('Quit')
        quit_action.triggered.connect(self.handle_exit)
        quit_action.triggered.connect(QtWidgets.qApp.quit)

        self.setContextMenu(context_menu)

    def icon_activated(self, reason):
        print(reason)

    def handle_exit(self):
        self.show_notification('The application is closing.')
        self.checker_thread.exit()

        if self.ws_is_running:
            self.websocket_thread.exit()

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
        if status == 'not_running':
            if not self.notification_shown:
                self.show_notification(
                    'The League of Legends Client is not running.')
                self.notification_shown = True
        elif status == 'running' and not self.ws_is_running:
            self.websocket_thread = ws.WebSocketThread()
            self.websocket_thread.start()
            self.websocket_thread.api_event.connect(self.handle_api_events)

            self.ws_is_running = True

            self.preferences = DataStore.get_preferences()
            if self.preferences['first_time']:
                DataStore.setup()
