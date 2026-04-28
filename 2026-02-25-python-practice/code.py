# Welcome to Day-4
# This is your coding workspace
import sys
from PyQt6.QtWidgets import *
from PyQt6 import QtSql

def show_info_messagebox(info):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setText(info)
    msg.setWindowTitle(f"Information MessageBox")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    retval = msg.exec()


class registerScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setGeometry(200,200,300,150)
        
        self.mylayout = QVBoxLayout()
        self.centralwidget = QWidget()
        self.setCentralWidget(self.centralwidget)

        self.userlbl = QLabel("usename")
        self.username = QLineEdit()

        self.passlbl = QLabel("password")
        self.password = QLineEdit()

        self.register = QPushButton("register")  
        self.login = QPushButton("login")  
        

        self.initUi()

      

  
        self.register.clicked.connect(lambda : self.register_users(self.username.text(),self.password.text()))
        # self.data = self.query.exec("select * from users")





    def register_users(self,username,password):
        if username=='' or password=='':
            show_info_messagebox("username or password is empty or invalid")
            return
        
        query.prepare(
            "INSERT INTO users (username, password) VALUES (?, ?)"
            )

        query.addBindValue(username)
        query.addBindValue(password)
        query.exec()
        self.username.clear()
        self.password.clear()
        print(f"user : {username} pass : {password} is inserted to db")



    def initUi(self):
        self.mylayout.addWidget(self.userlbl)
        self.mylayout.addWidget(self.username)
        self.mylayout.addWidget(self.passlbl)
        self.mylayout.addWidget(self.password)
        self.mylayout.addWidget(self.register)
        self.mylayout.addWidget(self.login)

        self.mylayout.setContentsMargins(20,20,20,20)
        self.mylayout.setSpacing(20)
        self.centralwidget.setLayout(self.mylayout)

class loginScreen(QWidget):
    def __init__(self,):
        super().__init__()
    def __init__(self):
        super().__init__()
        # self.setGeometry(200,200,300,150)

        self.mylayout = QVBoxLayout()

        self.userlbl = QLabel("usename")
        self.username = QLineEdit()

        self.passlbl = QLabel("password")
        self.password = QLineEdit()

        self.login = QPushButton("login")  
        self.register = QPushButton("register")  
        self.initUi()

    def initUi(self):
        self.login.clicked.connect(self.login_users)
        # self.register.clicked.connect(to_register_page())
        self.mylayout.addWidget(self.userlbl)
        self.mylayout.addWidget(self.username)
        self.mylayout.addWidget(self.passlbl)
        self.mylayout.addWidget(self.password)
        self.mylayout.addWidget(self.login)
        self.mylayout.addWidget(self.register)

        self.mylayout.setContentsMargins(20,20,20,20)
        self.mylayout.setSpacing(20)
        self.setLayout(self.mylayout)

    def login_users(self):
        username = self.username.text()
        password = self.password.text()

        if username == "" or password == "":
            show_info_messagebox("username or password is empty or invalid")
            return

        query.prepare(
            "select username from users where username = ? and password = ?"
            )

        query.addBindValue(username)
        query.addBindValue(password)

        data = query.exec()
        if (query.next()==True):
            print(f"user : {username} pass : {password} is logged in .")
            user = username
            to_home()
        else:
            print('user not found')

        self.username.clear()
        self.password.clear()

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()

        # Title
        self.title = QLabel("Home Dashboard")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # Welcome Label
        self.welcome_label = QLabel(f"Welcome, {user}")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self.profile_btn = QPushButton("Profile")
        self.settings_btn = QPushButton("Settings")
        self.logout_btn = QPushButton("Logout")

        # self.logout_btn.clicked.connect(self.logout)

        # Add widgets
        self.layout.addWidget(self.title)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.welcome_label)
        self.layout.addSpacing(20)
        self.layout.addWidget(self.profile_btn)
        self.layout.addWidget(self.settings_btn)
        self.layout.addStretch()
        self.layout.addWidget(self.logout_btn)

        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(15)

        self.setLayout(self.layout)


app = QApplication([])

user = 'harsh'
db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("users.db")
if not db.open():
    show_info_messagebox("db is unable to connect")
else:
    print("db connect successfully")

query = QtSql.QSqlQuery()
query.exec(
    "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
)


register_window = registerScreen()
login_window = loginScreen()
home_window = HomeScreen()
# Redirect logic
register_window.login.clicked.connect(
    lambda: (register_window.hide(), login_window.show())
)
def to_home():
    login_window.hide()
    home_window.show()

login_window.register.clicked.connect(
    lambda: (login_window.hide(), register_window.show())
)
home_window.logout_btn.clicked.connect(
    lambda: (home_window.hide(),login_window.show())
)

# home_window.show()
login_window.show()
app.exec()
