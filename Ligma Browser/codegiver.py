import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton

class MyWebBrowser(QMainWindow):

    def __init__(self):
        super().__init__()

        self.window = QWidget()
        self.window.setWindowTitle("Ligma Browser code giver")

        self.layout = QVBoxLayout()
        self.horizontal = QHBoxLayout()

        self.url_bar = QTextEdit()
        self.url_bar.setMaximumHeight(30)

        self.go_btn = QPushButton("search")
        self.go_btn.setMinimumHeight(30)

        self.horizontal.addWidget(self.url_bar)
        self.horizontal.addWidget(self.go_btn)

        self.browser_content = QTextEdit()
        self.browser_content.setReadOnly(True)

        self.go_btn.clicked.connect(self.load_website)

        self.layout.addLayout(self.horizontal)
        self.layout.addWidget(self.browser_content)

        self.window.setLayout(self.layout)
        self.setCentralWidget(self.window)

    def load_website(self):
        url = self.url_bar.toPlainText()
        if not url.startswith("https://") and not url.startswith("http://"):
            url = "https://" + url
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.browser_content.setPlainText(response.text)
        except requests.RequestException as e:
            self.browser_content.setPlainText("Error loading website: " + str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWebBrowser()
    window.show()
    sys.exit(app.exec_())
