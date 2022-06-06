from typing import Type
import mysql 
import mysql.connector
import sys 
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QErrorMessage, QPushButton, QHBoxLayout, QMessageBox, QFileDialog
from PyQt5 import uic, QtCore, QtGui, QtWidgets
import os 
import datetime
#cursor for manipulating database

db = mysql.connector.connect(host = 'localhost', user = 'root', password = '*P@ssw0rd', database = 'book_rental') 
mydb = db.cursor(buffered=True) 

# to fix gui not displaying properly on different resolutions
QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) 

def convert_to_sql(qtimedate, alt = False):        #convert Time date from QT to SQL Format if alt is true, convert to python DateTime format instead
    qtimedate = qtimedate.split(' ')
    year = int(qtimedate[4])
    time = qtimedate[3]
    day = int(qtimedate[2])
    month =''
    if qtimedate[1] == 'Jan':
        month = 1
    elif qtimedate[1] == 'Feb':
        month = 2
    elif qtimedate[1] == 'Mar':
        month = 3
    elif qtimedate[1] == 'Apr':
        month = 4
    elif qtimedate[1] == 'May':
        month = 5 
    elif qtimedate[1] == 'Jun': 
        month = 6 
    elif qtimedate[1] == 'Jul': 
        month = 7 
    elif qtimedate[1] == 'Aug': 
        month = 8 
    elif qtimedate[1] == 'Sep': 
        month = 9 
    elif qtimedate[1] == 'Oct': 
        month = 10 
    elif qtimedate[1] == 'Nov': 
        month = 11 
    elif qtimedate[1] == 'Dec': 
        month = 12 

    if alt == True:
        time = time.split(':')
        hour = int(time[0])
        minutes = int(time[1])
        secs = int(time[2])
        secs = int(secs)
        return [(year), month, day, hour, minutes, secs, 0]

    return f"{year}-{month}-{day} {time}" 

#Sat Jan 1 00:00:00 2000 Q FORMAT 
#1999-07-22 12:00:00 SQL RETURN 
#'1999-07-24 12:00:00' SQL INSERT 

class ImageView(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/id_image.ui', self)
        self.image_path = ''

    def load_image(self):
        self.pix = QtGui.QPixmap(self.image_path)
        self.pix = self.pix.scaledToWidth(self.image_view.width()-100)
        self.pix = self.pix.scaledToHeight(self.image_view.height()-100)
        self.item = QtWidgets.QGraphicsPixmapItem(self.pix)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.scene.addItem(self.item)
        self.image_view.setScene(self.scene)


class RentBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/rent_form.ui', self) 
        self.cust_complete.pressed.connect(self.complete)
        self.cust_id.editingFinished.connect(self.autofill_cust)
        self.cust_due.editingFinished.connect(self.getprice)
        self.cust_id.setValidator(QtGui.QIntValidator())
        self.cust_phone.setValidator(QtGui.QIntValidator())
        self.cust_house.setValidator(QtGui.QIntValidator())
        self.cust_bookrent_id.setValidator(QtGui.QIntValidator())
        self.id_select.pressed.connect(self.get_id)
        self.cust_idpicture = ''
        self.cust_startdate = '' 
        self.cust_duedate = '' 
        self.book_title = '' 
        self.book_price = '' 
        self.book_cpyno = '' 
        self.customer_id = ''
        self.cust_alrexist = False
        self.errorDialog = QErrorMessage()
        self.errorDialog.setWindowTitle("Error")
        self.errorDialog.setWindowModality(QtCore.Qt.ApplicationModal)

    def get_id(self):
        image_path = QFileDialog.getOpenFileName(self, 'Select Image', os.getenv('HOME'), 'Images(*.csv *.xpm *.jpg)')[0]
        self.cust_idpic.setText(image_path)

    def complete(self):
        if self.checkempty():
            self.errorDialog.showMessage("Invalid input, check for missing/incorrect fields.")
            return
        reply = QMessageBox.question(self, 'Confirmation', 'Confirm Action')
        if reply == QMessageBox.Yes:
            pass
        else:
            return
        customer_name = self.cust_name.text()
        phone_no = self.cust_phone.text()
        street_add = self.cust_street.text()
        brgy_add = self.cust_barangay.text()
        house_add = self.cust_house.text()
        self.customer_id = self.cust_id.text()
        self.cust_idpicture = self.cust_idpic.text()
        self.cust_startdate = self.cust_start.dateTime().toString()
        self.cust_duedate = self.cust_due.dateTime().toString()
        start_date = convert_to_sql(self.cust_startdate)
        due_date = convert_to_sql(self.cust_duedate)
        self.cust_startdate = convert_to_sql(self.cust_start.dateTime().toString())
        self.cust_duedate = convert_to_sql(self.cust_due.dateTime().toString())
        self.book_cpyno = self.cust_bookrent_id.text()
        book_price = self.cust_price.text()
        mydb.execute(f"SELECT COUNT(*) FROM book_copy WHERE copy_number ={self.book_cpyno} AND book_status = 'Available'")
        count = mydb.fetchone()
        if count[0] == 0:
            self.errorDialog.showMessage("Book with this copy number is not available.")
            return
        if self.cust_alrexist == False:
            mydb.execute(f"INSERT INTO customer VALUES({self.customer_id},'{customer_name}', '{self.cust_idpicture}', '{phone_no}', '{street_add}', '{brgy_add}', {house_add})")
            db.commit()
        mydb.execute(f"INSERT INTO rents VALUES({self.customer_id}, {self.book_cpyno}, {book_price},'{start_date}', NULL , '{due_date}', DEFAULT)")
        db.commit() 
        mydb.execute(f"UPDATE book_copy SET book_status = 'Rented' WHERE copy_number = {self.book_cpyno}")
        db.commit()
        self.close() 
    
    def autofill_cust(self): 
        self.customer_id = self.cust_id.text() 
        mydb.execute(f"SELECT customer_id, full_name, id_image, phone_number, street, barangay, house_no FROM customer WHERE customer_id = '{self.customer_id}'")
        rows = mydb.fetchone()
        if rows == None:
            self.cust_alrexist = False
            self.cust_name.setReadOnly(False)
            self.cust_idpic.setReadOnly(False)
            self.cust_phone.setReadOnly(False)
            self.cust_street.setReadOnly(False)
            self.cust_barangay.setReadOnly(False)
            self.cust_house.setReadOnly(False)
            self.cust_name.clear()
            self.cust_idpic.clear()
            self.cust_phone.clear()
            self.cust_street.clear()
            self.cust_barangay.clear()
            self.cust_house.clear()

            return
        
        self.cust_alrexist = True
        self.cust_name.setReadOnly(True)
        self.cust_idpic.setReadOnly(True)
        self.cust_phone.setReadOnly(True)
        self.cust_street.setReadOnly(True)
        self.cust_barangay.setReadOnly(True)
        self.cust_house.setReadOnly(True)
        self.cust_name.setText(rows[1])
        self.cust_idpic.setText(rows[2])
        self.cust_phone.setText(rows[3])
        self.cust_street.setText(rows[4])
        self.cust_barangay.setText(rows[5])
        self.cust_house.setText(str(rows[6]))
        

    def autofill_book(self):
        self.cust_price.setText(str(self.book_price))
        self.cust_bookrent_title.setText(str(self.book_title))
    
    def getprice(self):
        self.cust_startdate = self.cust_start.dateTime().toString()
        self.cust_duedate = self.cust_due.dateTime().toString()
        start_time = convert_to_sql(self.cust_startdate, True)
        start_time = datetime.datetime(start_time[0], start_time[1], start_time[2], start_time[3], start_time[4], start_time[5], start_time[6])
        due_time = convert_to_sql(self.cust_duedate, True)
        due_time = datetime.datetime(due_time[0], due_time[1], due_time[2], due_time[3], due_time[4], due_time[5], due_time[6])
        rent_days = str((due_time - start_time))
        rent_days = int(rent_days.split()[0])
        rent_price = rent_days*self.book_price
        self.cust_price.setText(str(rent_price))
    
    def checkempty(self):
        if len(self.cust_id.text()) == 0:
            return True
        elif len(self.cust_name.text()) == 0:
            return True
        elif len(self.cust_phone.text()) == 0:
            return True
        elif len(self.cust_street.text()) == 0:
            return True
        elif len(self.cust_barangay.text()) == 0:
            return True
        elif len(self.cust_house.text()) == 0:
            return True
        elif len(self.cust_bookrent_id.text()) == 0:
            return True
        elif len(self.cust_idpic.text()) == 0:
            return True
        return False
        
    def clear_fields(self):
        self.cust_id.clear()
        self.cust_name.clear()
        self.cust_phone.clear()
        self.cust_idpic.clear()
        self.cust_street.clear()
        self.cust_barangay.clear()
        self.cust_house.clear()
        self.cust_bookrent_id.clear()
        

class EditBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/admin_editbook.ui', self) 
        self.error_dialog=QErrorMessage()
        self.error_dialog.setWindowTitle("Error")
        self.success_dialog=QErrorMessage() 
        self.success_dialog.setWindowTitle("SUCCESS") 
        self.done_add.pressed.connect(self.inputBook)

    def getBook(self, row, searchfor): #Get book data in database
        self.getisbn = ''
        if searchfor == None:
            mydb.execute(f"SELECT * FROM book LIMIT {row}, 1")
        else:
            mydb.execute(f"SELECT * from book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%' LIMIT {row}, 1")
        rows = mydb.fetchone()
        self.getisbn = rows[0]
        self.autofill(rows)

    def checkEmpty(self, book): #Check if text line is empty
        for data in book:
            if not data:
                return True
        
    def inputBook(self): #Function for updating book data to database
        book = []
        book.append(self.book_isbn.text())
        book.append(self.book_genre.text())
        book.append(self.book_author.text())
        book.append(self.book_date.text()[6:]+'-'+self.book_date.text()[3:5]+'-'+self.book_date.text()[0:2])
        book.append(self.book_title.text())
        book.append(self.book_price.text())
        book.append(self.getisbn)
        if self.checkEmpty(book):
            self.error_dialog.showMessage('You have entered invalid information.')
        else:
            reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to edit this book?') 
            if reply == QMessageBox.Yes:
                try: #Check if isbn exists
                    sqlUpdate = "UPDATE book SET isbn = %s, genre = %s, author = %s, publish_date = %s, book_title = %s, price = %s where isbn = %s"
                    mydb.execute(sqlUpdate,book)
                    db.commit()
                    self.book_isbn.clear()
                    self.book_title.clear()
                    self.book_author.clear()
                    self.book_genre.clear()
                    self.book_date.setDateTime(QtCore.QDateTime(2000,1,1,1,0,0))
                    self.book_price.clear()
                    self.close()
                    self.success_dialog.showMessage('Book edited successfully!')
                except:
                    self.error_dialog.showMessage('ISBN exists. Enter a new one')
                    self.book_isbn.clear()
            else:
                return
        
    def autofill(self, rows): #autofill
        self.book_isbn.setText(str(rows[0]))
        self.book_title.setText(rows[4])
        self.book_author.setText(rows[2])
        self.book_genre.setText(rows[1])
        self.book_date.setDateTime(QtCore.QDateTime(rows[3]))
        self.book_price.setText(str(rows[5])) 

class AddBook(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/admin_addbook.ui', self)
        self.error_dialog=QErrorMessage()
        self.error_dialog.setWindowTitle("Error")
        self.success_dialog=QErrorMessage()
        self.success_dialog.setWindowTitle("SUCCESS") 
        self.done_add.pressed.connect(self.inputBook)
        self.book_isbnsearch.pressed.connect(self.searchisbn)
        
    def clearInfo(self): #Clear Text Line
        self.book_copynum.clear()
        self.book_title.clear()
        self.book_author.clear()
        self.book_genre.clear()
        self.book_date.setDateTime(QtCore.QDateTime(2000,1,1,1,0,0))
        self.book_price.clear()
        
    def inputBook(self): #Function for inserting book data to database
        book = []
        try: #check if isbn is int
            book.append(int(self.book_isbn.text()))
        except:
            self.error_dialog.showMessage('Invalid ISBN.')
            return
        book.append(self.book_genre.text())
        book.append(self.book_author.text())
        book.append(self.book_date.text()[6:]+'-'+self.book_date.text()[3:5]+'-'+self.book_date.text()[0:2])
        book.append(self.book_title.text())
        book.append(self.book_price.text())
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to add this book?') 
        if reply == QMessageBox.Yes:
            if self.search():
                try: #Check if copy_number exists in database
                    mydb.execute(f"INSERT INTO book_copy VALUES({self.book_copynum.text()}, 'Available', {self.book_isbn.text()})")
                    db.commit()
                except:
                    self.error_dialog.showMessage('Enter a new copy number')
                    self.book_copynum.clear()
                    return
            else:
                try: #Check if ocrrect info given
                    sqlInsert = "INSERT INTO book VALUES (%s, %s, %s, %s, %s, %s)"
                    mydb.execute(sqlInsert, book)
                    db.commit()

                    mydb.execute(f"INSERT INTO book_copy VALUES({self.book_copynum.text()}, 'Available', {self.book_isbn.text()})")
                    db.commit()
                except:
                    self.error_dialog.showMessage('You have entered invalid information.')
                    return
            self.close()
            self.success_dialog.showMessage('Book added successfully!')
            self.book_title.setReadOnly(False)
            self.book_author.setReadOnly(False)
            self.book_genre.setReadOnly(False)
            self.book_date.setReadOnly(False)
            self.book_price.setReadOnly(False)
        else:
            return
        
    def search(self): #Search isbn in database
        mydb.execute(f"SELECT * FROM book WHERE isbn = {self.book_isbn.text()}")
        rows = mydb.fetchall()
        if rows:
            return rows
        else:
            return 0
        
    def searchisbn(self): #Search isbn
        if not self.book_isbn.text():
            self.error_dialog.showMessage('You have entered invalid information.')
            return
        rows = self.search()
        if rows:
            self.autofill(rows)
            self.book_title.setReadOnly(True)
            self.book_author.setReadOnly(True)
            self.book_genre.setReadOnly(True)
            self.book_date.setReadOnly(True)
            self.book_price.setReadOnly(True)
            return 1
        else:
            self.error_dialog.showMessage('No ISBN found.')
            self.clearInfo()
            self.book_title.setReadOnly(False)
            self.book_author.setReadOnly(False)
            self.book_genre.setReadOnly(False)
            self.book_date.setReadOnly(False)
            self.book_price.setReadOnly(False)
            return 0

    def autofill(self, rows): #Autofill
        self.book_title.setText(rows[0][4])
        self.book_author.setText(rows[0][2])
        self.book_genre.setText(rows[0][1])
        self.book_date.setDateTime(QtCore.QDateTime(rows[0][3]))
        self.book_price.setText(str(rows[0][5]))




class RegisterWindow(QMainWindow):                  #Reggie

    def __init__(self):
        super().__init__()
        uic.loadUi(f'{sys.path[0]}/user_register.ui', self)
        self.pushButton.pressed.connect(self.entry)
        self.error_dialog=QErrorMessage()
        self.error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.error_dialog.setWindowTitle("Error") 
        self.success_dialog=QErrorMessage()
        self.success_dialog.setWindowTitle("SUCCESS")
        self.success_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.lineEdit.returnPressed.connect(self.entry)
        self.lineEdit_2.returnPressed.connect(self.entry)
        self.lineEdit_3.returnPressed.connect(self.entry)

    def entry(self):
        self.username = self.lineEdit.text()
        self.password = self.lineEdit_2.text()
        self.con_pass = self.lineEdit_3.text()
        self.role= self.comboBox.currentText()
        mydb.execute(f"SELECT COUNT(*) FROM app_user WHERE username='{self.username}'")
        username=mydb.fetchone()
        if username[0]==1:
            self.error_dialog.showMessage('User already exists')
            return
        if (len(self.password)==0):
            self.error_dialog.showMessage('Please Input Password')
            return
        if self.password != self.con_pass:
            self.error_dialog.showMessage("Password Incorrect")
            return
        print (f"{self.username}, {self.password}, {self.con_pass}, {self.role}")
        mydb.execute(f"INSERT INTO app_user VALUES ('{self.password}','{self.username}','{self.role}')")
        db.commit()
        self.success_dialog.showMessage("Successfully Registered!")
        self.close()




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
        self.user_login.pressed.connect(self.get_usertype)
        self.lineEdit.returnPressed.connect(self.get_usertype)
        self.lineEdit_2.returnPressed.connect(self.get_usertype)

        self.error_dialog=QErrorMessage()
        self.error_dialog.setWindowTitle("Error")
        self.error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)


    def get_usertype(self):     #login validation
        self.username=self.lineEdit.text()
        self.password=self.lineEdit_2.text()
        mydb.execute(f"SELECT COUNT(*) FROM app_user WHERE username='{self.username}'")
        username=mydb.fetchone()
        if username[0]==0:
            self.error_dialog.showMessage("No User found")             #NO USER
            return
        mydb.execute(f"SELECT user_password FROM app_user WHERE username='{self.username}' ")
        userpass=mydb.fetchone()
        userpass=userpass[0]
        if self.password != userpass:
            self.error_dialog.showMessage("Incorrect Password")         #INCORRECT PASSWORD
            return
        mydb.execute(f"SELECT role FROM app_user WHERE username='{self.username}'")
        role=mydb.fetchone()
        change_usertype(*role) 
        make_window(self)

        self.close()
        
    def open_register(self):
        self.register_window.show()
        


class MainWindow (QMainWindow):
    
    def __init__(self):
        self.user_type = user_role
        super().__init__()        
        self.addbook_window = AddBook()
        self.editbook_window = EditBook()
        self.rent_window = RentBook()
        self.image_view = ImageView()
        self.headerlabels = ['ISBN','Genre','Author','Publish Date','Book Title','Rent Price', 'Status','Action']
        self.headerlabels2 = ['Customer ID', 'Book Copy', 'Customer Name','Phone Number','Book Title', 'Rent Price','Start Date','Due Date','Penalizations','Actions']
        self.error_dialog=QErrorMessage()
        self.error_dialog.setWindowTitle("Error")
        self.success_dialog=QErrorMessage()
        self.success_dialog.setWindowTitle("SUCCESS")
        self.error_dialog.setWindowModality(QtCore.Qt.ApplicationModal)




        if self.user_type == 'Admin':
            uic.loadUi(f'{sys.path[0]}/admin.ui', self)
            self.book_addbutton.pressed.connect(self.open_addbook)
            self.hist_clear.pressed.connect(self.delete_history)
        elif self.user_type == 'Clerk': 
            uic.loadUi(f'{sys.path[0]}/clerk.ui', self) 


        self.book_refresh.pressed.connect(lambda: self.display_books())
        self.book_searchbutton.pressed.connect(self.search_book)
        self.cust_refresh.pressed.connect(self.display_monitoring)
        self.cust_searchbutton.pressed.connect(self.search_cust)
        self.hist_refresh.pressed.connect(self.display_history)
        self.switch_user.triggered.connect(self.close)
        self.cust_searchbar.returnPressed.connect(self.search_cust)
        self.book_searchbar.returnPressed.connect(self.search_book)
        self.display_monitoring()
        self.display_books()
        self.display_history()

    def delete_history(self):
        reply = QMessageBox.question(self, 'Confirmation', 'Delete history? This action cannot be undone.')
        if reply == QMessageBox.No:
            return
        else:
            pass
        mydb.execute("TRUNCATE rents")
        db.commit()
        self.display_history
        

    def open_rentbook(self, row, searchfor = None):
        if searchfor == None:
            mydb.execute("SELECT isbn, genre, author, publish_date, book_title from book")
        else:
            mydb.execute(f"SELECT isbn, genre, author, publish_date, book_title from book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%'")
        rows = mydb.fetchall()
        rows = rows[row]
        isbn = rows[0]
        mydb.execute(f"SELECT book.book_title, book.price FROM book INNER JOIN book_copy ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Available' AND book.isbn = {isbn}")
        rows = mydb.fetchone()
        if rows == None:
            print('No Available Books')
            return
        book_title = rows[0]
        book_price = rows[1]
        self.rent_window.clear_fields()
        self.rent_window.book_price = book_price
        self.rent_window.book_title = book_title
        self.rent_window.cust_alrexist = False
        self.rent_window.autofill_book()
        self.rent_window.cust_start.setMinimumDateTime(QtCore.QDateTime.currentDateTime())
        self.rent_window.cust_due.setMinimumDateTime(QtCore.QDateTime.currentDateTime().addDays(1))
        self.rent_window.cust_start.setDateTime(QtCore.QDateTime.currentDateTime())
        self.rent_window.cust_due.setDateTime(QtCore.QDateTime.currentDateTime().addDays(1))
        self.rent_window.show()
    
    def open_addbook(self):                                             #! PA IMPLEMENT KO SOPHIA
        self.addbook_window.book_isbn.clear()
        self.addbook_window.clearInfo()
        self.addbook_window.show()

    def open_editbook(self, row, searchfor):
        self.editbook_window.getBook(row, searchfor)
        self.editbook_window.show()

    def delete_book(self, row, searchfor):
        if searchfor == None:
            mydb.execute(f"SELECT * FROM book LIMIT {row}, 1")
        else:
            mydb.execute(f"SELECT * from book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%' LIMIT {row}, 1")
        rows = mydb.fetchone()
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to delete this book? This action cannot be undone.')
        if reply == QMessageBox.Yes:
            mydb.execute(f"DELETE FROM book WHERE isbn = {rows[0]}")
            db.commit()
            self.success_dialog.showMessage("Book deleted successfully!")
            self.display_books()
        else:
            return
    
    def testrow(self, row, searchfor = None):                         #!TEST FUNCTION DO NOT DELETE
        print('Row selected is ---- ', row)
        if searchfor != None:
            mydb.execute(f"SELECT isbn, genre, author, publish_date, book_title from book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%'")
        else:
            mydb.execute("SELECT isbn, genre, author, publish_date, book_title from book") 
        rows = mydb.fetchall()
        isbn = rows[row][0]
        print(isbn)
        isbn += 1
        mydb.execute(f"UPDATE book SET isbn = {isbn} WHERE book_title = '{rows[row][4]}'")
        db.commit() 


    def make_buttons(self, row, searchfor = None):                               #passes the row number of selected row on the table displayed to the buttons
        if user_role == 'Admin':
            self.editButton = QPushButton('Edit')
            self.deleteButton = QPushButton('Delete') 
            if searchfor == None: 
                self.editButton.pressed.connect(lambda:self.open_editbook(row, searchfor))
                self.deleteButton.pressed.connect(lambda:self.delete_book(row, searchfor))

            else:
                self.editButton.pressed.connect(lambda: self.open_editbook(row, searchfor))
                self.deleteButton.pressed.connect(lambda:self.delete_book(row, searchfor)) 

            self.actionLayout = QHBoxLayout() 
            self.actionLayout.addWidget(self.deleteButton,5) 
            self.actionLayout.addWidget(self.editButton,5) 
            self.actionWidget = QWidget() 
            self.actionWidget.setLayout(self.actionLayout) 
            return self.actionWidget 
        
        elif user_role == 'Clerk': 
            self.rentButton = QPushButton('Rent Out') 
            if searchfor == None: 
                self.rentButton.pressed.connect(lambda: self.open_rentbook(row))                        #! urel 
            else: 
                self.rentButton.pressed.connect(lambda: self.open_rentbook(row, searchfor))            

            self.actionLayout = QHBoxLayout() 
            self.actionLayout.addWidget(self.rentButton,5) 
            self.actionWidget = QWidget() 
            self.actionWidget.setLayout(self.actionLayout) 
            return self.actionWidget 

    def overduecheck(self, c_id, cpy_no, start_date):
        mydb.execute(f"SELECT due_date FROM rents WHERE c_id = {c_id} and cpy_no={cpy_no} and start_date='{start_date}'")
        rows = mydb.fetchone()
        due_date = rows[0] 
        mydb.execute(f"SELECT book.price FROM book INNER JOIN book_copy on book.isbn = book_copy.copy_isbn WHERE book_copy.copy_number ={cpy_no}")
        book_price = mydb.fetchone()[0]
        time_now = datetime.datetime.now()
        overdue = int((str(time_now - due_date)).split()[0])
        overdue_fee = int((int(book_price)*.20))
        overdue_total = int(overdue_fee*overdue)
        if overdue <= 0:
            return False
        else:
            mydb.execute(f"UPDATE rents rents SET penalizations = {overdue_total} WHERE c_id = {c_id} and cpy_no={cpy_no} and start_date='{start_date}' ")
            db.commit()
            return(overdue, overdue_fee, overdue_total)

    def view_id(self, row, searchfor = None):

        query_order = ' ORDER BY rents.due_date ASC'
        query = ("SELECT customer.id_image "
                "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                "INNER JOIN customer ON rents.c_id = customer.customer_id "
                "INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND rents.return_date is NULL")
        query_search = query + f" AND customer.full_name LIKE '%{searchfor}%'" + query_order
        query = query + query_order

        if searchfor != None:
            mydb.execute(query_search)
        elif searchfor == None:   
            mydb.execute(query)
        rows = mydb.fetchall()
        rows = (rows[row][0])
        image_path = rows
        self.image_view.image_path = image_path
        self.image_view.load_image()
        self.image_view.show()

    def return_book(self, row, searchfor = None):
        reply = QMessageBox.question(self, 'Confirmation', 'Confirm Action')
        if reply == QMessageBox.Yes:
            pass
        else:
            return
        
        query_order = " ORDER BY rents.due_date ASC"
        query = ("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                "INNER JOIN customer ON rents.c_id = customer.customer_id "
                "INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND rents.return_date is NULL")
        query_search = query + f" AND customer.full_name LIKE '%{searchfor}%'" + query_order
        query = query + query_order

        if searchfor != None:
            mydb.execute(query_search)
        elif searchfor == None:   
            mydb.execute(query)

        rows = mydb.fetchall()
        rows = list(rows[row])
        mydb.execute(f"UPDATE rents SET return_date = NOW() where c_id = {rows[0]} and cpy_no = {rows[1]} and start_date = '{rows[6]}'")
        mydb.execute(f"UPDATE book_copy SET book_status = 'Available' WHERE copy_number = {rows[1]}")
        db.commit()
        self.display_monitoring()

                

    def make_buttons2(self, row, searchfor = None):                               
        self.returnButton = QPushButton('Return')
        self.view_idButton = QPushButton('View ID') 
        if searchfor == None: 
            self.returnButton.pressed.connect(lambda: self.return_book(row))              
            self.view_idButton.pressed.connect(lambda:self.view_id(row))             

        else:
            self.returnButton.pressed.connect(lambda: self.return_book(row,searchfor))            
            self.view_idButton.pressed.connect(lambda:self.view_id(row,searchfor))         

        self.actionLayout = QHBoxLayout() 
        self.actionLayout.addWidget(self.view_idButton,5) 
        self.actionLayout.addWidget(self.returnButton,5) 
        self.actionWidget = QWidget() 
        self.actionWidget.setLayout(self.actionLayout) 
        return self.actionWidget 
            

    def display_monitoring(self, search = False, searchfor = None):
        hheader = self.cust_table.horizontalHeader()          
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.cust_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)        
        vheader.setDefaultSectionSize(50)
        numColumn = 9

        query_order = ' ORDER BY rents.due_date ASC'
        query = ("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                "INNER JOIN customer ON rents.c_id = customer.customer_id "
                "INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND rents.return_date is NULL")
        query_search = query + f" AND customer.full_name LIKE '%{searchfor}%'" + query_order
        query = query + query_order
    
        if search == True and searchfor != None:                        #if displaying a search
            mydb.execute(query_search)
        
        elif search == False and searchfor == None:
            mydb.execute(query)
    
        rows = mydb.fetchall()
        numRows = len(rows)
        self.cust_table.setColumnCount(numColumn+1)
        self.cust_table.setRowCount(numRows)
        self.cust_table.setHorizontalHeaderLabels(self.headerlabels2)
    
        for i in range(numRows):
            for j in range(numColumn):
                try:
                    if j == 8:
                        penalization = self.overduecheck(rows[i][0], rows[i][1], rows[i][6])
                        if penalization == False:
                            pass
                        else:
                            penalization_text = f"Penalization: {penalization[1]} per day \nOverdue: {penalization[0]} days\nTotal:{penalization[2]}"
                            self.cust_table.setItem(i, j, QTableWidgetItem(str(penalization_text)))
                            continue
                    self.cust_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                except TypeError:
                    self.tableWidget.setItem(i, j, QTableWidgetItem("Deleted"))
            actionWidget = self.make_buttons2(i, searchfor)                    #REFER TO makebuttons function for details
            self.cust_table.setCellWidget(i, 9, actionWidget)

        #'Customer ID', 'Book Copy', 'Customer Name','Book Title', 'Rent Price','Start Date','Due Date','Penalizations','Actions'


    def display_history(self):
        hheader = self.hist_table.horizontalHeader()          
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.hist_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)        
        vheader.setDefaultSectionSize(50)
        numColumn = 10
        tempheader = self.headerlabels2[:-1]
        tempheader.append('Date Returned')

        mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations, rents.return_date "
                    "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                    "INNER JOIN customer ON rents.c_id = customer.customer_id "
                    "INNER JOIN book ON book.isbn = book_copy.copy_isbn ORDER BY rents.start_date DESC")

        rows = mydb.fetchall()
        numRows = len(rows)
        self.hist_table.setColumnCount(numColumn)
        self.hist_table.setRowCount(numRows)
        self.hist_table.setHorizontalHeaderLabels(tempheader)
        
        
        for i in range(numRows):
            for j in range(numColumn):
                try:
                    if j == 9 and rows[i][9] == None:
                        self.hist_table.setItem(i, j, QTableWidgetItem(str('To be returned')))
                        continue
                    self.hist_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                except TypeError:
                    self.tableWidget.setItem(i, j, QTableWidgetItem("Deleted"))

    def display_books(self, search = False, searchfor = None):          #SEARCH == TRUE - MEANING DISPLAYING FOR A SEARCH, SEARCHFOR = SEARCHED KEYWORD
        hheader = self.book_table.horizontalHeader()          
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.book_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.ResizeToContents)        
        vheader.setDefaultSectionSize(50)
        numColumn = 7

        query = "SELECT isbn, genre, author, publish_date, book_title, price from book"
        query_search = query + f" WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%'"
    
        if search == True and searchfor != None:                        #if displaying a search
            mydb.execute(query_search)
        elif search == False and searchfor == None:
            mydb.execute(query)
        
        rows = mydb.fetchall()
        numRows = len(rows)
        self.book_table.setColumnCount(numColumn+1)
        self.book_table.setRowCount(numRows)
        self.book_table.setHorizontalHeaderLabels(self.headerlabels)

            
        for i in range(numRows):
            for j in range(numColumn):
                    if j == 6:
                        mydb.execute("SELECT * FROM book_copy INNER JOIN book ON book_copy.copy_isbn = book.isbn " 
                                    f"WHERE book_copy.book_status = 'Available' AND book.isbn = {rows[i][0]}")
                        available = mydb.fetchall()
                        available = len(available)
                        mydb.execute("SELECT * FROM book_copy INNER JOIN book ON book_copy.copy_isbn = book.isbn " 
                                    f"WHERE book_copy.book_status = 'Rented' AND book.isbn = {rows[i][0]}")
                        rented = mydb.fetchall()
                        rented = len(rented)
                        mydb.execute("SELECT * FROM book_copy INNER JOIN book ON book_copy.copy_isbn = book.isbn " 
                                    f"AND book.isbn = {rows[i][0]}")
                        total = mydb.fetchall()
                        total = len(total)                            
                        availability = f"Available: {available} \nRented: {rented}\nTotal: {total}"

                        self.book_table.setItem(i, j, QTableWidgetItem(str(availability)))
                        continue
                    self.book_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                
            actionWidget = self.make_buttons(i,searchfor)            #REFER TO makebuttons function for details    
            self.book_table.setCellWidget(i, 7, actionWidget)


    def search_cust(self):
        search_this = self.cust_searchbar.text()
        self.display_monitoring(True, search_this)
        
    def search_book(self):
        search_this = self.book_searchbar.text()
        self.display_books(True, search_this)



def make_window(loginwindow):
    mainWindow = MainWindow()
    mainWindow.showMaximized()
    mainWindow.switch_user.triggered.connect(loginwindow.show)
    mainWindow.switch_user.triggered.connect(lambda: loginwindow.user_login.setEnabled(True))
    loginwindow.user_login.setEnabled(False)                                                        #IDK WHY BUT THIS FIXED DOUBLE CLICKING LOL    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)


    login = LoginWindow()
    login.show()

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
