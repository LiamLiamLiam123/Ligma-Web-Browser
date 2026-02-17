from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
import sys
import tkinter as tk
import random
import string

class MyWebBrowser(QMainWindow):

    def __init__(self):
        super().__init__()

        self.window = QWidget()
        self.window.setWindowTitle("Ligma Browser")

        # Set the size of the main window
        self.setGeometry(200, 100, 1200, 1000) 

        self.layout = QVBoxLayout()
        self.horizontal = QHBoxLayout()

        self.url_bar = QTextEdit()
        self.url_bar.setMaximumHeight(30)

        self.go_btn = QPushButton("Search")
        self.go_btn.setMinimumHeight(30)

        self.back_btn = QPushButton("<")
        self.back_btn.setMinimumHeight(30)

        self.forward_btn = QPushButton(">")
        self.forward_btn.setMinimumHeight(30)

        self.calc_btn = QPushButton("Calculator")
        self.calc_btn.setMinimumHeight(30)

        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setMinimumHeight(30)

        self.settings_btn = QPushButton("...")
        self.settings_btn.setMinimumHeight(30)

        self.test_password_btn = QPushButton("Test Password")
        self.test_password_btn.setMinimumHeight(30)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)  # Enable tabs to be closable
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Connect tab close signal
        self.tab_widget.currentChanged.connect(self.tab_changed)  # Connect tab change signal

        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)
        self.horizontal.addWidget(self.calc_btn)
        self.horizontal.addWidget(self.new_tab_btn)
        self.horizontal.addWidget(self.settings_btn)
        self.horizontal.addWidget(self.test_password_btn)

        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.tab_widget)

        self.window.setLayout(self.layout)
        self.window.show()

        self.go_btn.clicked.connect(self.search)
        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn.clicked.connect(self.go_forward)
        self.calc_btn.clicked.connect(self.open_calculator)
        self.new_tab_btn.clicked.connect(self.new_tab)
        self.settings_btn.clicked.connect(self.open_settings)
        self.test_password_btn.clicked.connect(self.test_password)  # Connect the button to the method

        self.create_tab("https://google.com")  # Create the first tab with Google as the homepage

    def create_tab(self, url=None):
        new_browser = QWebEngineView()
        self.tab_widget.addTab(new_browser, "New Tab")
        if url:
            new_browser.setUrl(QUrl(url))
        self.tab_widget.setCurrentWidget(new_browser)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            if widget is not None:
                widget.deleteLater()
                self.tab_widget.removeTab(index)

    def search(self):
        current_tab_index = self.tab_widget.currentIndex()
        browser = self.tab_widget.widget(current_tab_index)
        url = self.url_bar.toPlainText()
        self.navigate(url, browser)

    def navigate(self, url, browser):
        if url.startswith("https://") or url.startswith("http://"):
            browser.setUrl(QUrl(url))
        else:
            url = "https://" + url
            self.url_bar.setText(url)
            browser.setUrl(QUrl(url))

    def go_back(self):
        current_tab_index = self.tab_widget.currentIndex()
        browser = self.tab_widget.widget(current_tab_index)
        browser.back()

    def go_forward(self):
        current_tab_index = self.tab_widget.currentIndex()
        browser = self.tab_widget.widget(current_tab_index)
        browser.forward()

    def open_calculator(self):
        calculator = QCalculator()
        calculator.show()

    def new_tab(self):
        self.create_tab()

    def open_settings(self):
        dialog = QDialog()
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout()
        dialog.setLayout(layout)
        dark_mode_checkbox = QCheckBox("Dark Mode")
        layout.addWidget(dark_mode_checkbox)
        dark_mode_checkbox.stateChanged.connect(self.change_theme)
        dialog.exec_()

    def change_theme(self, state):
        if state == Qt.Checked:
            self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        else:
            self.setStyleSheet("")

    def tab_changed(self, index):
        pass

    # Define the method to test the password
    def test_password(self):
        def crack_password():
            password = password_entry.get()
            attempts = 0

            while True:
                guess = generate_random_string(len(password))
                attempts += 1

                if guess == password:
                    result_label.config(text=f"Password cracked in {attempts} attempts.\nPassword: {password}")
                    break

        def generate_random_string(length):
            charset = string.ascii_letters + string.digits
            return ''.join(random.choice(charset) for _ in range(length))

        # GUI setup
        root = tk.Tk()
        root.title("Password Cracker")

        # Labels
        title_label = tk.Label(root, text="Password Cracker")
        title_label.pack()

        password_label = tk.Label(root, text="Enter a password:")
        password_label.pack()

        # Entry field
        password_entry = tk.Entry(root, show="*")
        password_entry.pack()

        # Button
        crack_button = tk.Button(root, text="Crack Password", command=crack_password)
        crack_button.pack()

        # Result label
        result_label = tk.Label(root, text="")
        result_label.pack()

        root.mainloop()

class QCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.layout = QVBoxLayout()
        self.display = QLineEdit()
        self.layout.addWidget(self.display)

        grid = QGridLayout()
        buttons = {
            (i, j): str(i * 3 + j + 1) for i in range(3) for j in range(3)
        }
        buttons.update({(3, 0): '0', (3, 1): '.', (3, 2): '='})
        operations = {'+': (0, 3), '-': (1, 3), '*': (2, 3), '/': (3, 3), 'C': (0, 4), 'CE': (1, 4)}

        for position, text in buttons.items():
            button = QPushButton(text)
            button.clicked.connect(lambda _, text=text: self.on_click(text))
            grid.addWidget(button, *position)

        for text, position in operations.items():
            button = QPushButton(text)
            button.clicked.connect(lambda _, text=text: self.on_click(text))
            grid.addWidget(button, *position)

        self.layout.addLayout(grid)
        self.setLayout(self.layout)

    def on_click(self, key):
        if key == '=':
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except Exception as e:
                self.display.setText("Error")
        elif key == 'C':
            self.display.clear()
        elif key == 'CE':
            self.display.setText(self.display.text()[:-1])
        else:
            self.display.setText(self.display.text() + key)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWebBrowser()
    sys.exit(app.exec_())
