from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWebEngineWidgets import *
import sys

class MyWebBrowser(QMainWindow):

    def __init__(self):

        super().__init__()

        self.window = QWidget()
        self.window.setWindowTitle("Ligma Browser")

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

        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)
        self.horizontal.addWidget(self.back_btn)
        self.horizontal.addWidget(self.forward_btn)
        self.horizontal.addWidget(self.calc_btn)

        self.browser = QWebEngineView()

        self.go_btn.clicked.connect(lambda: self.navigate(self.url_bar.toPlainText()))
        self.back_btn.clicked.connect(self.browser.back)
        self.forward_btn.clicked.connect(self.browser.forward)
        self.calc_btn.clicked.connect(self.open_calculator)

        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.browser)

        self.browser.setUrl(QUrl("https://google.com"))

        self.window.setLayout(self.layout)
        self.window.show()

    def navigate(self, url):
        if url.startswith("https://") or url.startswith("http://"):
            self.browser.setUrl(QUrl(url))
        else:
            url = "http://" + url
            self.url_bar.setText(url)
            self.browser.setUrl(QUrl(url))

    def open_calculator(self):
        calculator = QCalculator()
        calculator.show()

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
