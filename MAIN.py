import mysql
import mysql.connector
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QErrorMessage, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic, QtCore
import os

#cursor for manipulating database
db = mysql.connector.connect(host = 'localhost', user = 'root', password = '*P@ssw0rd', database = 'student information system')
mydb = db.cursor()

# to fix gui not displaying properly on different resolutions
QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) 


class AddBook(QMainWindow):
    def __init__ (self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/admin_addbook.ui', self)
        self.book_isbn.editingFinished.connect(self.check)

    def check(self):
        self.book_author.setText('Test')
        self.book_genre.setText('Test')
        self.book_title.setText('Test')



if __name__ == '__main__':
    app = QApplication(sys.argv)

    mygui = AddBook()
    mygui.show()

    try:
        sys.exit(app.exec_())
    except (SystemExit):
        print("Closing window...")