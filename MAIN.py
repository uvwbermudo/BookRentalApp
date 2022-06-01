from ast import While
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





class RentBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/rent_form.ui', self) 


class EditBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/admin_editbook.ui', self) 


class AddBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/admin_addbook.ui', self) 


class RegisterWindow(QMainWindow):                  #Reggie

    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/user_register.ui', self) 
        


user_role = 'None'
def change_usertype(user_type):
    global user_role
    user_role = user_type

class LoginWindow(QMainWindow):         #Reggie

    def __init__(self):
        super().__init__()
        self.register_window = RegisterWindow()
        uic.loadUi(f'{sys.path[0]}/user_login.ui', self)
        self.user_reg.pressed.connect(self.open_register)
        self.user_login.pressed.connect(self.get_usertype) #testing only, change function

    def get_usertype(self):     #login validation
        change_usertype('Admin') #test func 
        self.close()

    def open_register(self):
        self.register_window.show()
        


class MainWindow (QMainWindow):
    
    def __init__(self):
        self.user_type = user_role
        super().__init__()        
        self.addbook_window = AddBook()

        if self.user_type == 'Admin':
            uic.loadUi(f'{sys.path[0]}/admin.ui', self)
        elif self.user_type == 'Clerk':        
            uic.loadUi(f'{sys.path[0]}/clerk.ui', self)

        self.book_addbutton.pressed.connect(self.open_addbook)

    def open_addbook(self):
        self.addbook_window.show()
            

    
        




if __name__ == '__main__':
    app = QApplication(sys.argv) 
    login = LoginWindow()
    login.show()
    try:
        sys.exit(app.exec_())
    except (SystemExit):
        print("Closing window...")
    
    main = MainWindow()
    main.show()
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
#sophiaaaaa