#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ligma Browser — A modern PyQt5 web browser.
Single-file implementation with calculator, password tester, and clean UI.
"""

import re
import ast
import sys
from urllib.parse import quote_plus

from PyQt5.QtCore import QUrl, Qt, QSize, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QLineEdit, QToolBar, QAction, QToolButton, QSizePolicy,
    QDialog, QGridLayout, QPushButton, QLabel, QTextEdit,
    QDialogButtonBox, QMessageBox, QProgressBar, QFrame,
    QMenu, QShortcut, QListWidget, QListWidgetItem, QHBoxLayout,
    QStatusBar, QInputDialog, QStyle, QCheckBox, QFileDialog,
    QRadioButton, QButtonGroup,
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
LIGMA_HOME_URL = "https://liamliamliam123.github.io/Ligma-Home-Page/"
HOME_URL = LIGMA_HOME_URL
GOOGLE_SEARCH_URL = "https://www.google.com/search?q={}"
DUCKDUCKGO_SEARCH_URL = "https://duckduckgo.com/?q={}"

# (display name, home URL, search URL template for address bar)
SEARCH_ENGINES = [
    ("Ligma Home Page", LIGMA_HOME_URL, GOOGLE_SEARCH_URL),
    ("Google", "https://www.google.com", GOOGLE_SEARCH_URL),
    ("DuckDuckGo", "https://duckduckgo.com", DUCKDUCKGO_SEARCH_URL),
]

MIN_TAB_COUNT = 1
ADDRESS_BAR_MIN_HEIGHT = 36
TOOLBAR_ICON_SIZE = 24
BUTTON_MIN_SIZE = 44  # Apple HIG: 44pt minimum hit target
FIND_DEBOUNCE_MS = 250

# Find flags (for PyQt5 versions that may not have all)
FindWrapsAroundDocument = getattr(QWebEnginePage, "FindWrapsAroundDocument", 0x10000)
FindBackward = getattr(QWebEnginePage, "FindBackward", 0x02)
FindCaseSensitively = getattr(QWebEnginePage, "FindCaseSensitively", 0x04)

# -----------------------------------------------------------------------------
# Styles (Apple-inspired: clean, high contrast, spacing)
# -----------------------------------------------------------------------------
DARK_STYLE = """
    QMainWindow, QWidget { background-color: #1c1c1e; }
    QToolBar {
        background-color: #2c2c2e;
        border: none;
        spacing: 8px;
        padding: 6px 10px;
        min-height: 44px;
    }
    QToolButton, QPushButton {
        background-color: transparent;
        color: #e5e5ea;
        border: none;
        border-radius: 8px;
        min-width: 44px;
        min-height: 44px;
        padding: 8px;
        font-size: 13px;
    }
    QToolButton:hover, QPushButton:hover {
        background-color: #3a3a3c;
    }
    QToolButton:pressed, QPushButton:pressed {
        background-color: #48484a;
    }
    QLineEdit {
        background-color: #3a3a3c;
        color: #e5e5ea;
        border: none;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        min-height: 36px;
        selection-background-color: #0a84ff;
    }
    QLineEdit:focus { border: 1px solid #0a84ff; }
    QTabWidget::pane {
        border: none;
        background-color: #1c1c1e;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #2c2c2e;
        color: #e5e5ea;
        padding: 10px 18px;
        margin-right: 2px;
        border-radius: 8px 8px 0 0;
        min-width: 80px;
        font-size: 13px;
    }
    QTabBar::tab:selected { background-color: #1c1c1e; }
    QTabBar::tab:hover:!selected { background-color: #3a3a3c; }
    QTabBar::close-button {
        subcontrol-origin: margin;
        subcontrol-position: right;
        padding: 4px 8px;
        min-width: 24px;
        min-height: 24px;
        border-radius: 4px;
        font-size: 16px;
        color: #e5e5ea;
    }
    QTabBar::close-button:hover { background-color: #ff3b30; color: white; }
    QDialog, QMessageBox { background-color: #2c2c2e; color: #e5e5ea; }
    QLabel { color: #e5e5ea; font-size: 13px; }
    QTextEdit {
        background-color: #3a3a3c;
        color: #e5e5ea;
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
    }
    QProgressBar {
        border: none;
        border-radius: 6px;
        background-color: #3a3a3c;
        text-align: center;
        min-height: 8px;
    }
    QProgressBar::chunk { background-color: #0a84ff; border-radius: 6px; }
    QFrame { background-color: #2c2c2e; border-radius: 12px; }
    QListWidget {
        background-color: #3a3a3c;
        color: #e5e5ea;
        border-radius: 8px;
        padding: 6px;
    }
    QListWidget::item:hover { background-color: #48484a; }
    QListWidget::item:selected { background-color: #0a84ff; }
"""

LIGHT_STYLE = """
    QMainWindow, QWidget { background-color: #f5f5f7; }
    QToolBar {
        background-color: #ffffff;
        border: none;
        border-bottom: 1px solid #d1d1d6;
        spacing: 8px;
        padding: 6px 10px;
        min-height: 44px;
    }
    QToolButton, QPushButton {
        background-color: transparent;
        color: #1d1d1f;
        border: none;
        border-radius: 8px;
        min-width: 44px;
        min-height: 44px;
        padding: 8px;
        font-size: 13px;
    }
    QToolButton:hover, QPushButton:hover { background-color: #e5e5ea; }
    QToolButton:pressed, QPushButton:pressed { background-color: #d1d1d6; }
    QLineEdit {
        background-color: #e5e5ea;
        color: #1d1d1f;
        border: none;
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 14px;
        min-height: 36px;
        selection-background-color: #007aff;
    }
    QLineEdit:focus { border: 1px solid #007aff; }
    QTabWidget::pane {
        border: none;
        background-color: #f5f5f7;
        top: -1px;
    }
    QTabBar::tab {
        background-color: #e5e5ea;
        color: #1d1d1f;
        padding: 10px 18px;
        margin-right: 2px;
        border-radius: 8px 8px 0 0;
        min-width: 80px;
        font-size: 13px;
    }
    QTabBar::tab:selected { background-color: #f5f5f7; }
    QTabBar::tab:hover:!selected { background-color: #d1d1d6; }
    QTabBar::close-button {
        subcontrol-origin: margin;
        subcontrol-position: right;
        padding: 4px 8px;
        min-width: 24px;
        min-height: 24px;
        border-radius: 4px;
        font-size: 16px;
        color: #1d1d1f;
    }
    QTabBar::close-button:hover { background-color: #ff3b30; color: white; }
    QDialog, QMessageBox { background-color: #ffffff; color: #1d1d1f; }
    QLabel { color: #1d1d1f; font-size: 13px; }
    QTextEdit {
        background-color: #f5f5f7;
        color: #1d1d1f;
        border-radius: 10px;
        padding: 12px;
        font-size: 13px;
    }
    QProgressBar {
        border: none;
        border-radius: 6px;
        background-color: #e5e5ea;
        min-height: 8px;
    }
    QProgressBar::chunk { background-color: #007aff; border-radius: 6px; }
    QFrame { background-color: #ffffff; border-radius: 12px; border: 1px solid #d1d1d6; }
    QListWidget {
        background-color: #f5f5f7;
        color: #1d1d1f;
        border-radius: 8px;
        padding: 6px;
    }
    QListWidget::item:hover { background-color: #e5e5ea; }
    QListWidget::item:selected { background-color: #007aff; color: white; }
"""


# -----------------------------------------------------------------------------
# URL parsing
# -----------------------------------------------------------------------------
def parse_url_input(text, home_url=None, search_url_template=None):
    """Return URL to load: direct URL or search. Uses home_url for empty, search_url_template for queries."""
    if home_url is None:
        home_url = HOME_URL
    if search_url_template is None:
        search_url_template = GOOGLE_SEARCH_URL
    if not text or not str(text).strip():
        return home_url
    raw = str(text).strip()
    lower = raw.lower()
    if lower.startswith("http://") or lower.startswith("https://"):
        return raw
    if "." in raw and " " not in raw:
        return "https://" + raw
    return search_url_template.format(quote_plus(raw))


# -----------------------------------------------------------------------------
# Safe calculator (no eval of arbitrary code)
# -----------------------------------------------------------------------------
def safe_calculate(expr):
    """Evaluate a simple math expression safely. Returns (success, result_or_error)."""
    expr = re.sub(r"\s+", "", expr)
    if not expr:
        return False, "Empty"
    allowed = set("0123456789+-*/().% ")
    if not all(c in allowed for c in expr):
        return False, "Invalid characters"
    try:
        # Restrict to literals and basic math
        node = ast.parse(expr, mode="eval")
        body = node.body
        allowed = (ast.BinOp, ast.UnaryOp, ast.Num, getattr(ast, "Constant", ast.Num))
        if not isinstance(body, allowed):
            return False, "Invalid expression"
        result = eval(compile(node, "<calc>", "eval"), {"__builtins__": {}}, {})
        if isinstance(result, (int, float)):
            return True, result
        return False, "Invalid result"
    except Exception as e:
        return False, str(e)


# -----------------------------------------------------------------------------
# Password cracker worker (runs in thread to avoid UI freeze)
# -----------------------------------------------------------------------------
class PasswordCrackerWorker(QThread):
    progress = pyqtSignal(int, int, str)   # current, total, attempt
    finished_signal = pyqtSignal(bool, str)  # found, result_message

    def __init__(self, password, charset, parent=None):
        super().__init__(parent)
        self._password = password
        self._charset = charset
        self._abort = False

    def abort(self):
        self._abort = True

    def run(self):
        try:
            total = len(self._charset) ** len(self._password)
            if total <= 0 or len(self._password) == 0:
                self.finished_signal.emit(False, "Invalid input.")
                return
            total = min(total, 1000000)
            count = 0
            from itertools import product
            for length in range(1, len(self._password) + 1):
                if self._abort:
                    self.finished_signal.emit(False, "Cancelled.")
                    return
                for attempt in product(self._charset, repeat=length):
                    if self._abort:
                        self.finished_signal.emit(False, "Cancelled.")
                        return
                    count += 1
                    attempt_str = "".join(attempt)
                    self.progress.emit(count, total, attempt_str)
                    if attempt_str == self._password:
                        self.finished_signal.emit(True, f"Found: {attempt_str}")
                        return
                    if count >= total:
                        break
                if count >= total:
                    break
            self.finished_signal.emit(False, "Not found (limit reached).")
        except Exception as e:
            self.finished_signal.emit(False, f"Error: {e}")


# -----------------------------------------------------------------------------
# Calculator dialog
# -----------------------------------------------------------------------------
class CalculatorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculator")
        self.setMinimumWidth(280)
        self.setMinimumHeight(360)
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.display = QLineEdit()
        self.display.setPlaceholderText("0")
        self.display.setReadOnly(True)
        self.display.setMinimumHeight(52)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 28px;
                padding: 12px;
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.display)

        grid = QGridLayout()
        buttons = [
            ("C", 0, 0), ("±", 0, 1), ("%", 0, 2), ("/", 0, 3),
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("*", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("-", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("+", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("⌫", 4, 3),
        ]
        for label, row, col in buttons:
            btn = QPushButton(label)
            btn.setMinimumSize(BUTTON_MIN_SIZE, BUTTON_MIN_SIZE)
            btn.clicked.connect(lambda checked, l=label: self._on_button(l))
            grid.addWidget(btn, row, col)
        layout.addLayout(grid)
        self._expr = ""

    def _on_button(self, label):
        if label == "C":
            self._expr = ""
        elif label == "=":
            ok, result = safe_calculate(self._expr)
            self._expr = str(result) if ok else self._expr
        elif label == "⌫":
            self._expr = self._expr[:-1]
        elif label == "±":
            if self._expr and self._expr[0] == "-":
                self._expr = self._expr[1:]
            elif self._expr:
                self._expr = "-" + self._expr
        else:
            self._expr += label
        self.display.setText(self._expr or "0")


# -----------------------------------------------------------------------------
# Password tester dialog (cracker runs in QThread)
# -----------------------------------------------------------------------------
class PasswordTesterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Strength Tester")
        self.setMinimumSize(400, 320)
        self._worker = None
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        layout.addWidget(QLabel("Password to test:"))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(ADDRESS_BAR_MIN_HEIGHT)
        layout.addWidget(self.password_edit)

        layout.addWidget(QLabel("Character set (e.g. abc123):"))
        self.charset_edit = QLineEdit()
        self.charset_edit.setPlaceholderText("abcdefghijklmnopqrstuvwxyz0123456789")
        self.charset_edit.setText("abcdefghijklmnopqrstuvwxyz0123456789")
        layout.addWidget(self.charset_edit)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(120)
        layout.addWidget(self.log_text)

        self.run_btn = QPushButton("Start test")
        self.run_btn.setMinimumHeight(BUTTON_MIN_SIZE)
        self.run_btn.clicked.connect(self._start_test)
        layout.addWidget(self.run_btn)

    def _log(self, msg):
        self.log_text.append(msg)

    def _start_test(self):
        password = self.password_edit.text()
        charset = self.charset_edit.text() or "abc"
        if not password:
            QMessageBox.warning(self, "Password Tester", "Enter a password to test.")
            return
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            return
        self._log(f"Testing password (length {len(password)}) with charset length {len(charset)}...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.run_btn.setText("Cancel")
        self._worker = PasswordCrackerWorker(password, charset, self)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, current, total, attempt):
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(min(current, total))
        if current % 100 == 0 or current <= 3:
            self._log(f"Trying: {attempt}")

    def _on_finished(self, found, msg):
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 100)
        self.run_btn.setText("Start test")
        self._log(msg)
        QMessageBox.information(self, "Password Tester", msg)


# -----------------------------------------------------------------------------
# Web profile (shared; modern user agent for better site compatibility)
# -----------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def get_browser_profile():
    """Shared profile with modern user agent so sites load correctly."""
    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(USER_AGENT)
    return profile


# -----------------------------------------------------------------------------
# Browser tab (one QWebEngineView per tab)
# -----------------------------------------------------------------------------
class BrowserTab(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        page = QWebEnginePage(get_browser_profile(), self)
        self.setPage(page)
        self.setUrl(QUrl(HOME_URL))


# -----------------------------------------------------------------------------
# Main window
# -----------------------------------------------------------------------------
class LigmaBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ligma Browser")
        self.setMinimumSize(900, 600)
        self.resize(1200, 800)
        self._dark_mode = True
        self._apply_theme()

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        toolbar.setMinimumHeight(52)
        toolbar.setContentsMargins(10, 6, 10, 6)
        toolbar.setStyleSheet("QToolBar { spacing: 6px; }")

        back_act = QAction("← Back", self)
        back_act.triggered.connect(self._go_back)
        toolbar.addAction(back_act)

        forward_act = QAction("Forward →", self)
        forward_act.triggered.connect(self._go_forward)
        toolbar.addAction(forward_act)

        reload_icon = self.style().standardIcon(QStyle.SP_BrowserReload)
        reload_act = QAction(reload_icon, "Reload", self)
        reload_act.setToolTip("Reload")
        reload_act.triggered.connect(self._reload)
        toolbar.addAction(reload_act)

        home_act = QAction("Home", self)
        home_act.triggered.connect(self._go_home)
        toolbar.addAction(home_act)

        self._url_edit = QLineEdit()
        self._url_edit.setPlaceholderText("Search or enter URL")
        self._url_edit.setMinimumHeight(ADDRESS_BAR_MIN_HEIGHT)
        self._url_edit.returnPressed.connect(self._navigate_from_bar)
        self._url_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        toolbar.addWidget(self._url_edit)

        new_tab_act = QAction("New tab", self)
        new_tab_act.setShortcut(QKeySequence.AddTab)
        new_tab_act.triggered.connect(self._add_tab)
        toolbar.addAction(new_tab_act)

        close_tab_act = QAction("Close tab", self)
        close_tab_act.setShortcut(QKeySequence.Close)
        close_tab_act.triggered.connect(self._close_current_tab)
        toolbar.addAction(close_tab_act)

        more_menu = QMenu(self)
        find_act = QAction("Find", self)
        find_act.setShortcut(QKeySequence.Find)
        find_act.triggered.connect(self._show_find_bar)
        more_menu.addAction(find_act)
        more_menu.addSeparator()
        bookmarks_act = QAction("Bookmarks", self)
        bookmarks_act.triggered.connect(self._open_bookmarks)
        more_menu.addAction(bookmarks_act)
        add_bookmark_act = QAction("Add bookmark", self)
        add_bookmark_act.triggered.connect(self._add_current_bookmark)
        more_menu.addAction(add_bookmark_act)
        more_menu.addSeparator()
        calc_act = QAction("Calculator", self)
        calc_act.triggered.connect(self._open_calculator)
        more_menu.addAction(calc_act)
        pwd_act = QAction("Password test", self)
        pwd_act.triggered.connect(self._open_password_tester)
        more_menu.addAction(pwd_act)
        more_menu.addSeparator()
        view_src_act = QAction("View page source", self)
        view_src_act.triggered.connect(self._view_source)
        more_menu.addAction(view_src_act)
        print_act = QAction("Print...", self)
        print_act.setShortcut(QKeySequence.Print)
        print_act.triggered.connect(self._print_page)
        more_menu.addAction(print_act)
        print_pdf_act = QAction("Save as PDF...", self)
        print_pdf_act.triggered.connect(self._print_to_pdf)
        more_menu.addAction(print_pdf_act)
        more_menu.addSeparator()
        search_engine_act = QAction("Choose search engine", self)
        search_engine_act.triggered.connect(self._choose_search_engine)
        more_menu.addAction(search_engine_act)
        more_menu.addSeparator()
        history_act = QAction("History", self)
        history_act.triggered.connect(self._open_history)
        more_menu.addAction(history_act)
        more_menu.addSeparator()
        theme_act = QAction("Dark/Light", self)
        theme_act.triggered.connect(self._toggle_theme)
        more_menu.addAction(theme_act)

        more_btn = QToolButton()
        more_btn.setToolTip("More tools")
        more_btn.setText("⋮")
        more_btn.setPopupMode(QToolButton.InstantPopup)
        more_btn.setMenu(more_menu)
        more_btn.setStyleSheet("""
            QToolButton { font-size: 18px; font-weight: bold; padding: 4px 10px; }
            QToolButton::menu-indicator { image: none; }
        """)
        toolbar.addWidget(more_btn)

        layout.addWidget(toolbar)

        self._find_bar = QWidget()
        find_layout = QHBoxLayout(self._find_bar)
        find_layout.setContentsMargins(8, 6, 8, 6)
        self._find_edit = QLineEdit()
        self._find_edit.setPlaceholderText("Find in page...")
        self._find_edit.setMinimumHeight(32)
        self._find_edit.textChanged.connect(self._find_schedule)
        find_layout.addWidget(self._find_edit)
        self._find_result_label = QLabel("")
        self._find_result_label.setMinimumWidth(80)
        self._find_result_label.setStyleSheet("color: gray; font-size: 12px;")
        find_layout.addWidget(self._find_result_label)
        self._find_case_cb = QCheckBox("Match case")
        self._find_case_cb.stateChanged.connect(self._find_run_now)
        find_layout.addWidget(self._find_case_cb)
        self._find_prev_btn = QPushButton("Previous")
        self._find_prev_btn.clicked.connect(self._find_prev)
        find_layout.addWidget(self._find_prev_btn)
        self._find_next_btn = QPushButton("Next")
        self._find_next_btn.clicked.connect(self._find_next)
        find_layout.addWidget(self._find_next_btn)
        self._find_close_btn = QPushButton("Close")
        self._find_close_btn.clicked.connect(self._hide_find_bar)
        find_layout.addWidget(self._find_close_btn)
        self._find_bar.setVisible(False)
        layout.addWidget(self._find_bar)
        self._find_timer = QTimer(self)
        self._find_timer.setSingleShot(True)
        self._find_timer.timeout.connect(self._find_run_now)

        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.setDocumentMode(True)
        self._tabs.tabCloseRequested.connect(self._close_tab_at)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._tabs.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tabs.customContextMenuRequested.connect(self._show_tab_context_menu)
        layout.addWidget(self._tabs)

        self._status = QStatusBar()
        self._status.setStyleSheet("padding: 4px; font-size: 12px;")
        self.setStatusBar(self._status)

        self._bookmarks = []
        self._history = []
        self._home_url = LIGMA_HOME_URL
        self._search_url_template = GOOGLE_SEARCH_URL
        self._add_tab()
        self._update_url_bar()
        self._setup_shortcuts()

    def _apply_theme(self):
        if self._dark_mode:
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()

    def _current_tab(self):
        return self._tabs.currentWidget()

    def _add_tab(self, url=None):
        tab = BrowserTab(self)
        url_to_load = url if url else self._home_url
        if isinstance(url_to_load, str):
            tab.setUrl(QUrl(url_to_load))
        else:
            tab.setUrl(QUrl(self._home_url))
        idx = self._tabs.addTab(tab, "New tab")
        self._tabs.setCurrentIndex(idx)
        tab.titleChanged.connect(lambda t: self._on_tab_title_changed(tab, t))
        tab.iconChanged.connect(lambda ic: self._on_tab_icon_changed(tab, ic))
        tab.urlChanged.connect(lambda u: self._on_tab_url_changed(tab, u))
        tab.loadStarted.connect(self._on_load_started)
        tab.loadFinished.connect(self._on_load_finished)
        self._update_url_bar()
        return tab

    def _on_tab_title_changed(self, tab, title):
        idx = self._tabs.indexOf(tab)
        if idx >= 0:
            self._tabs.setTabText(idx, title[:20] + "…" if len(title) > 20 else title or "New tab")

    def _on_tab_icon_changed(self, tab, icon):
        idx = self._tabs.indexOf(tab)
        if idx >= 0 and not icon.isNull():
            self._tabs.setTabIcon(idx, icon)

    def _on_tab_url_changed(self, tab, url):
        try:
            if tab == self._current_tab():
                self._update_url_bar(url)
        except Exception:
            pass

    def _on_tab_changed(self, index):
        try:
            self._update_url_bar()
            self._update_status()
            if self._find_bar.isVisible():
                self._connect_find_result()
                self._find_run_now()
        except Exception:
            pass

    def _on_load_started(self):
        self._status.showMessage("Loading...")

    def _on_load_finished(self, ok):
        try:
            self._update_status()
            if ok:
                tab = self._current_tab()
                if tab and isinstance(tab, BrowserTab):
                    url = tab.url()
                    if url.isValid() and url.scheme() in ("http", "https"):
                        title = tab.title() or url.toString()
                        self._history.append((title, url.toString()))
        except Exception:
            pass

    def _update_status(self):
        try:
            tab = self._current_tab()
            if tab:
                url = tab.url()
                if url.isValid():
                    self._status.showMessage(url.toString(), 0)
                else:
                    self._status.clearMessage()
            else:
                self._status.clearMessage()
        except Exception:
            pass

    def _update_url_bar(self, url=None):
        try:
            if url is None:
                tab = self._current_tab()
                if tab:
                    url = tab.url()
                else:
                    url = QUrl()
            self._url_edit.blockSignals(True)
            self._url_edit.setText(url.toString() if url.isValid() else "")
            self._url_edit.blockSignals(False)
        except Exception:
            pass

    def _close_tab_at(self, index):
        if self._tabs.count() <= MIN_TAB_COUNT:
            self._add_tab()
            return
        self._tabs.removeTab(index)

    def _close_current_tab(self):
        idx = self._tabs.currentIndex()
        if idx >= 0:
            self._close_tab_at(idx)

    def _show_find_bar(self):
        self._find_bar.setVisible(True)
        self._find_edit.clear()
        self._find_result_label.setText("")
        self._find_edit.setFocus(Qt.ShortcutFocusReason)
        self._connect_find_result()

    def _hide_find_bar(self):
        try:
            self._find_bar.setVisible(False)
            self._find_timer.stop()
            tab = self._current_tab()
            if tab and isinstance(tab, BrowserTab):
                tab.findText("", FindWrapsAroundDocument)
        except Exception:
            pass

    def _connect_find_result(self):
        try:
            tab = self._current_tab()
            if not tab or not isinstance(tab, BrowserTab):
                return
            page = tab.page()
            if page and hasattr(page, "findTextFinished"):
                try:
                    page.findTextFinished.disconnect(self._on_find_result)
                except (TypeError, RuntimeError):
                    pass
                page.findTextFinished.connect(self._on_find_result)
        except Exception:
            pass

    def _on_find_result(self, result):
        try:
            if hasattr(result, "numberOfMatches") and hasattr(result, "activeMatch"):
                total = result.numberOfMatches()
                active = result.activeMatch()
                if total > 0:
                    self._find_result_label.setText(f"{active} of {total}")
                else:
                    self._find_result_label.setText("No matches")
            else:
                self._find_result_label.setText("")
        except Exception:
            self._find_result_label.setText("")

    def _find_schedule(self):
        self._find_timer.stop()
        self._find_timer.start(FIND_DEBOUNCE_MS)

    def _find_run_now(self):
        self._find_timer.stop()
        try:
            self._do_find(self._find_edit.text(), 0)
        except Exception:
            pass

    def _find_prev(self):
        try:
            self._do_find(self._find_edit.text(), FindBackward)
        except Exception:
            pass

    def _find_next(self):
        try:
            self._do_find(self._find_edit.text(), 0)
        except Exception:
            pass

    def _do_find(self, text, options=0):
        try:
            tab = self._current_tab()
            if not tab or not isinstance(tab, BrowserTab):
                return
            search_str = str(text).strip() if text else ""
            if self._find_case_cb.isChecked():
                options = options | FindCaseSensitively
            opts = options | FindWrapsAroundDocument
            tab.findText(search_str, opts)
            if not search_str:
                self._find_result_label.setText("")
        except Exception:
            self._find_result_label.setText("")

    def _show_tab_context_menu(self, pos):
        idx = self._tabs.tabBar().tabAt(pos)
        if idx < 0:
            return
        menu = QMenu(self)
        close_act = menu.addAction("Close tab")
        close_act.triggered.connect(lambda: self._close_tab_at(idx))
        close_others_act = menu.addAction("Close other tabs")
        close_others_act.triggered.connect(lambda: self._close_other_tabs(idx))
        menu.addSeparator()
        dup_act = menu.addAction("Duplicate tab")
        dup_act.triggered.connect(lambda: self._duplicate_tab_at(idx))
        new_act = menu.addAction("New tab")
        new_act.triggered.connect(self._add_tab)
        menu.exec_(self._tabs.mapToGlobal(pos))

    def _close_other_tabs(self, keep_index):
        for i in range(self._tabs.count() - 1, -1, -1):
            if i != keep_index:
                self._tabs.removeTab(i)

    def _duplicate_tab_at(self, index):
        tab = self._tabs.widget(index)
        if tab and isinstance(tab, BrowserTab):
            url = tab.url()
            self._add_tab(url.toString() if url.isValid() else None)

    def _open_bookmarks(self):
        d = QDialog(self)
        d.setWindowTitle("Bookmarks")
        d.setMinimumSize(400, 300)
        layout = QVBoxLayout(d)
        list_w = QListWidget()
        for title, url in self._bookmarks:
            list_w.addItem(f"{title} — {url}")
        layout.addWidget(list_w)

        def open_selected():
            row = list_w.currentRow()
            if 0 <= row < len(self._bookmarks):
                _, url = self._bookmarks[row]
                self._current_tab().setUrl(QUrl(url))
                d.accept()

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(open_selected)
        btn_layout.addWidget(open_btn)
        remove_btn = QPushButton("Remove")
        def remove_selected():
            row = list_w.currentRow()
            if 0 <= row < len(self._bookmarks):
                self._bookmarks.pop(row)
                list_w.takeItem(row)
        remove_btn.clicked.connect(remove_selected)
        btn_layout.addWidget(remove_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(d.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        list_w.itemDoubleClicked.connect(open_selected)
        d.exec_()

    def _add_current_bookmark(self):
        tab = self._current_tab()
        if not tab:
            return
        url = tab.url()
        if not url.isValid():
            QMessageBox.information(self, "Bookmarks", "No page to bookmark.")
            return
        title = tab.title() or url.toString()
        self._bookmarks.append((title, url.toString()))
        self._status.showMessage(f"Bookmarked: {title}", 3000)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence.ZoomIn, self, self._zoom_in)
        QShortcut(QKeySequence.ZoomOut, self, self._zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self._zoom_reset)
        esc_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        esc_shortcut.activated.connect(self._escape_pressed)

    def _escape_pressed(self):
        if self._find_bar.isVisible():
            self._hide_find_bar()
        else:
            self._find_edit.clearFocus()

    def _zoom_in(self):
        tab = self._current_tab()
        if tab:
            tab.setZoomFactor(min(3.0, tab.zoomFactor() + 0.25))

    def _zoom_out(self):
        tab = self._current_tab()
        if tab:
            tab.setZoomFactor(max(0.25, tab.zoomFactor() - 0.25))

    def _zoom_reset(self):
        tab = self._current_tab()
        if tab:
            tab.setZoomFactor(1.0)

    def _navigate_from_bar(self):
        try:
            text = self._url_edit.text()
            if hasattr(text, "strip"):
                text = text.strip()
            else:
                text = str(text).strip()
            url_str = parse_url_input(text, self._home_url, self._search_url_template)
            tab = self._current_tab()
            if tab and isinstance(tab, BrowserTab):
                tab.setUrl(QUrl(url_str))
            else:
                self._add_tab(url_str)
        except Exception:
            pass

    def _go_back(self):
        tab = self._current_tab()
        if tab and tab.history().canGoBack():
            tab.back()

    def _go_forward(self):
        tab = self._current_tab()
        if tab and tab.history().canGoForward():
            tab.forward()

    def _reload(self):
        tab = self._current_tab()
        if tab:
            tab.reload()

    def _go_home(self):
        tab = self._current_tab()
        if tab:
            tab.setUrl(QUrl(self._home_url))
        self._url_edit.setText(self._home_url)

    def _choose_search_engine(self):
        d = QDialog(self)
        d.setWindowTitle("Choose search engine")
        d.setMinimumWidth(320)
        layout = QVBoxLayout(d)
        layout.addWidget(QLabel("Home page and address-bar search (resets when you close the browser):"))
        group = QButtonGroup(d)
        self._search_engine_radios = []
        for i, (name, home_url, search_tpl) in enumerate(SEARCH_ENGINES):
            rb = QRadioButton(name)
            if home_url == self._home_url:
                rb.setChecked(True)
            group.addButton(rb)
            layout.addWidget(rb)
            self._search_engine_radios.append((rb, home_url, search_tpl))
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(d.accept)
        btn_box.rejected.connect(d.reject)
        layout.addWidget(btn_box)
        if d.exec_() != QDialog.Accepted:
            return
        for rb, home_url, search_tpl in self._search_engine_radios:
            if rb.isChecked():
                self._home_url = home_url
                self._search_url_template = search_tpl
                self._status.showMessage(f"Home & search: {home_url}", 3000)
                break
        self._search_engine_radios = []

    def _view_source(self):
        try:
            tab = self._current_tab()
            if not tab or not isinstance(tab, BrowserTab):
                return
            url = tab.url()
            if not url.isValid():
                return
            src_url = "view-source:" + url.toString()
            self._add_tab(src_url)
        except Exception:
            pass

    def _print_page(self):
        try:
            tab = self._current_tab()
            if not tab or not isinstance(tab, BrowserTab):
                return
            printer = QPrinter(QPrinter.HighResolution)
            dlg = QPrintDialog(printer, self)
            if dlg.exec_() != QDialog.Accepted:
                return
            tab.page().print(printer, lambda ok: None)
        except Exception:
            QMessageBox.warning(self, "Print", "Could not print the page.")

    def _print_to_pdf(self):
        try:
            tab = self._current_tab()
            if not tab or not isinstance(tab, BrowserTab):
                return
            path, _ = QFileDialog.getSaveFileName(
                self, "Save as PDF", "", "PDF (*.pdf)"
            )
            if not path:
                return
            if not path.endswith(".pdf"):
                path += ".pdf"
            page = tab.page()
            if not hasattr(page, "printToPdf"):
                QMessageBox.information(
                    self, "Save as PDF",
                    "PDF export not supported in this Qt version."
                )
                return

            def on_pdf_ready(data):
                try:
                    with open(path, "wb") as f:
                        f.write(data.data() if hasattr(data, "data") else bytes(data))
                    self._status.showMessage(f"Saved PDF: {path}", 4000)
                except Exception as e:
                    QMessageBox.warning(self, "Save as PDF", str(e))

            page.printToPdf(on_pdf_ready)
        except Exception as e:
            QMessageBox.warning(
                self, "Save as PDF",
                f"Could not save PDF: {e}"
            )

    def _open_history(self):
        d = QDialog(self)
        d.setWindowTitle("History")
        d.setMinimumSize(450, 350)
        layout = QVBoxLayout(d)
        list_w = QListWidget()
        for title, url in reversed(self._history[-200:]):
            t = (title[:50] + "…") if len(title) > 50 else title
            u = (url[:60] + "…") if len(url) > 60 else url
            list_w.addItem(f"{t} — {u}")
        layout.addWidget(list_w)

        def open_selected():
            row = list_w.currentRow()
            items = list(reversed(self._history[-200:]))
            if 0 <= row < len(items):
                _, url = items[row]
                tab = self._current_tab()
                if tab and isinstance(tab, BrowserTab):
                    tab.setUrl(QUrl(url))
                d.accept()

        btn_layout = QHBoxLayout()
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(open_selected)
        btn_layout.addWidget(open_btn)
        clear_btn = QPushButton("Clear history")
        def clear_history():
            self._history.clear()
            list_w.clear()
        clear_btn.clicked.connect(clear_history)
        btn_layout.addWidget(clear_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(d.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        list_w.itemDoubleClicked.connect(open_selected)
        d.exec_()

    def _open_calculator(self):
        d = CalculatorDialog(self)
        d.exec_()

    def _open_password_tester(self):
        d = PasswordTesterDialog(self)
        d.exec_()


# -----------------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------------
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Ligma Browser")
    app.setStyle("Fusion")
    font = QFont()
    font.setPointSize(13)
    app.setFont(font)
    window = LigmaBrowser()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
