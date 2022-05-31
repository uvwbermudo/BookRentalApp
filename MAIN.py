import mysql
import mysql.connector
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QErrorMessage, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic, QtCore
import os

#cursor for manipulating database
db = mysql.connector.connect(host = 'localhost', user = 'root', password = '*P@ssw0rd', database = 'book_rental')
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




# CREATE TABLE customer (
# 	customer_id INT NOT NULL,
# 	full_name VARCHAR(50) NOT NULL,
# 	id_image VARCHAR(200) NOT NULL,
# 	phone_number VARCHAR(15) NOT NULL,
# 	street VARCHAR(50) NOT NULL,
# 	barangay VARCHAR(50) NOT NULL,
# 	house_no INT NOT NULL,
# 	PRIMARY KEY (customer_id)
# );

# CREATE TABLE app_user (
# 	user_id INT NOT NULL AUTO_INCREMENT,
# 	user_password VARCHAR(20) NOT NULL,
# 	username VARCHAR(20) NOT NULL,
# 	role VARCHAR(5) NOT NULL,
# 	PRIMARY KEY (user_id)
# );

# CREATE TABLE book (
# 	isbn INT NOT NULL,
# 	genre VARCHAR(50) NOT NULL,
# 	author VARCHAR(50) NOT NULL,
# 	publish_date DATE NOT NULL,
# 	book_title VARCHAR(100) NOT NULL,
# 	PRIMARY KEY (isbn)
# );

# CREATE TABLE book_copy (
# 	copy_number INT NOT NULL AUTO_INCREMENT,
# 	book_status VARCHAR(10) NOT NULL,
# 	copy_isbn INT NOT NULL,
# 	PRIMARY KEY (copy_number),
# 	FOREIGN KEY (copy_isbn) REFERENCES book(isbn) ON DELETE CASCADE ON UPDATE CASCADE
# );

# CREATE TABLE rents (
# 	c_id INT NOT NULL,
# 	cpy_no INT NOT NULL,
# 	rent_price INT NOT NULL,
# 	start_date DATETIME NOT NULL DEFAULT (CURDATE()),
# 	return_date DATETIME NOT NULL, 
# 	due_date DATETIME NOT NULL DEFAULT (CURDATE()+1),
# 	penalizations INT DEFAULT 0,
# 	PRIMARY KEY (c_id,cpy_no),
# 	FOREIGN KEY (c_id) REFERENCES customer(customer_id) ON DELETE CASCADE ON UPDATE CASCADE,
# 	FOREIGN KEY (cpy_no) REFERENCES book_copy(copy_number)ON DELETE CASCADE ON UPDATE CASCADE
# ); 

#REGGIE
