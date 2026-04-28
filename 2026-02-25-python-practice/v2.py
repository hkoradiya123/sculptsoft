import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox,
)
from PyQt6.QtSql import QSqlDatabase, QSqlQuery
import os


def create_database():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("users.db")
    print("Database file location:", os.path.abspath("users.db"))

    if db.open():
        print("Database connected successfully!")
    else:
        print("Database connection failed")

    query = QSqlQuery()

    query.exec(
        """
     
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """
    )

    def insert_user(username, password):
        query.prepare("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)")
        query.addBindValue(username)
        query.addBindValue(password)
        query.exec()

    query.exec("DELETE FROM users WHERE username IN ('axit')")
    db.close()


"""   query.prepare("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)")
    query.addBindValue("admin")
    query.addBindValue("1234")
    query.exec()

    query.prepare("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)")
    query.addBindValue("axit")
    query.addBindValue("1235")
    
    
    
    
    query.exec()"""


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Form")
        self.setGeometry(200, 200, 300, 100)

        self.label_user = QLabel("Username:")
        self.input_user = QLineEdit()

        self.label_pass = QLabel("Password:")
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_login = QPushButton("Login")
        self.button_login.clicked.connect(self.check_login)

        layout = QVBoxLayout()
        layout.addWidget(self.label_user)
        layout.addWidget(self.input_user)
        layout.addWidget(self.label_pass)
        layout.addWidget(self.input_pass)
        layout.addWidget(self.button_login)

        self.setLayout(layout)

    def check_login(self):
        db = QSqlDatabase.database()

        if not db.open():
            QMessageBox.warning(self, "Error", "Database not connected")
            return

        query = QSqlQuery()
        query.prepare("SELECT * FROM users WHERE username = ? AND password = ?")
        query.addBindValue(self.input_user.text())
        query.addBindValue(self.input_pass.text())

        query.exec()

        if query.next():
            QMessageBox.information(self, "Success", "Login successful!")
        else:
            QMessageBox.warning(self, "Error", "Invalid Username or Password")

        db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    create_database()

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())
