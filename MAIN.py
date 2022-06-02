from ast import While
from tracemalloc import start
import mysql 
import mysql.connector 
import sys 
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QTableWidgetItem, QHeaderView, QErrorMessage, QPushButton, QHBoxLayout, QMessageBox
from PyQt5 import uic, QtCore, QtGui
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
        self.cust_startdate = '' 
        self.cust_duedate = '' 
        self.book_title = '' 
        self.book_price = '' 
        self.book_cpyno = '' 
        self.customer_id = ''
        self.cust_alrexist = False

    #def check_filled(self):
        


    def complete(self):
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
        self.cust_startdate = self.cust_start.dateTime().toString()
        self.cust_duedate = self.cust_due.dateTime().toString()
        start_date = convert_to_sql(self.cust_startdate)
        due_date = convert_to_sql(self.cust_duedate)
        self.cust_startdate = convert_to_sql(self.cust_start.dateTime().toString())
        self.cust_duedate = convert_to_sql(self.cust_due.dateTime().toString())
        self.book_cpyno = self.cust_bookrent_id.text()
        book_price = self.cust_price.text()
        if self.cust_alrexist == False:
            mydb.execute(f"INSERT INTO customer VALUES({self.customer_id},'{customer_name}', 'None', '{phone_no}', '{street_add}', '{brgy_add}', {house_add})")
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
            return
        self.cust_alrexist = True
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
        self.rent_window = RentBook()
        self.headerlabels = ['ISBN','Genre','Author','Publish Date','Book Title','Rent Price', 'Status','Action']
        self.headerlabels2 = ['Customer ID', 'Book Copy', 'Customer Name','Phone Number','Book Title', 'Rent Price','Start Date','Due Date','Penalizations','Actions']

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
        self.rent_window.cust_id.clear()
        self.rent_window.cust_name.clear()
        self.rent_window.cust_phone.clear()
        self.rent_window.cust_idpic.clear()
        self.rent_window.cust_street.clear()
        self.rent_window.cust_barangay.clear()
        self.rent_window.cust_house.clear()
        self.rent_window.cust_bookrent_id.clear()
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
        self.addbook_window.show()

    
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
                self.editButton.pressed.connect(lambda: self.testrow(row))              #! sophia dire i connect imong function for editing 
                self.deleteButton.pressed.connect(lambda:self.testrow(row))             #! sophia dire sa pag delete 

            else:
                self.editButton.pressed.connect(lambda: self.testrow(row,searchfor))            #! sophia 
                self.deleteButton.pressed.connect(lambda:self.testrow(row,searchfor))           #! sophia 

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

    def testfunc(self, row):
        print(row)

    def return_book(self, row, searchfor = None):
        reply = QMessageBox.question(self, 'Confirmation', 'Confirm Action')
        if reply == QMessageBox.Yes:
            pass
        else:
            return
        
        if searchfor != None:
            mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                        "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                        "INNER JOIN customer ON rents.c_id = customer.customer_id "
                        f"INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND customer.full_name LIKE '%{searchfor}%' AND rents.return_date is NULL ORDER BY rents.due_date ASC")
        else:   
            mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                        "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                        "INNER JOIN customer ON rents.c_id = customer.customer_id "
                        "INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND rents.return_date is NULL ORDER BY rents.due_date ASC")
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
            self.view_idButton.pressed.connect(lambda:self.testfunc(row))             

        else:
            self.returnButton.pressed.connect(lambda: self.return_book(row,searchfor))            
            self.view_idButton.pressed.connect(lambda:self.testfunc(row,searchfor))         

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
        vheader.setSectionResizeMode(QHeaderView.Fixed)        
        vheader.setDefaultSectionSize(40)
        numColumn = 9

        if search == True and searchfor != None:                        #if displaying a search
            mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                        "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                        "INNER JOIN customer ON rents.c_id = customer.customer_id "
                        f"INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND customer.full_name LIKE '%{searchfor}%' AND rents.return_date is NULL ORDER BY rents.due_date ASC ")
            rows = mydb.fetchall()
            numRows = len(rows)
            print("TESTING HERE", rows)
            self.cust_table.setColumnCount(numColumn+1)
            self.cust_table.setRowCount(numRows)
            self.cust_table.setHorizontalHeaderLabels(self.headerlabels2)
            
            for i in range(numRows):
                for j in range(numColumn):
                    self.cust_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
    
                actionWidget = self.make_buttons2(i,searchfor)            #REFER TO makebuttons function for details    
                self.cust_table.setCellWidget(i, 9, actionWidget)

        
        elif search == False and searchfor == None:     #default display
            mydb.execute("SELECT COUNT(*) FROM rents INNER JOIN book_copy on rents.cpy_no = book_copy.copy_number where book_copy.book_status = 'Rented' and rents.return_date is NULL")
            numRows = mydb.fetchone()
            numRows = numRows[0]
            self.cust_table.setColumnCount(numColumn+1)
            self.cust_table.setRowCount(numRows)
            self.cust_table.setHorizontalHeaderLabels(self.headerlabels2)
            
            mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                        "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                        "INNER JOIN customer ON rents.c_id = customer.customer_id "
                        "INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented' AND rents.return_date is NULL ORDER BY rents.due_date ASC")
    
            rows = mydb.fetchall()
            for i in range(numRows):
                for j in range(numColumn):
                    self.cust_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                actionWidget = self.make_buttons2(i)                    #REFER TO makebuttons function for details
                self.cust_table.setCellWidget(i, 9, actionWidget)

            #'Customer ID', 'Book Copy', 'Customer Name','Book Title', 'Rent Price','Start Date','Due Date','Penalizations','Actions'


    def display_history(self):
        hheader = self.hist_table.horizontalHeader()          
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.hist_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.Fixed)        
        vheader.setDefaultSectionSize(40)
        numColumn = 10
        tempheader = self.headerlabels2[:-1]
        tempheader.append('Date Returned')

        mydb.execute("SELECT COUNT(*) FROM rents INNER JOIN book_copy on rents.cpy_no = book_copy.copy_number")
        numRows = mydb.fetchone()
        numRows = numRows[0]
        self.hist_table.setColumnCount(numColumn)
        self.hist_table.setRowCount(numRows)
        self.hist_table.setHorizontalHeaderLabels(tempheader)
        
        mydb.execute("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations, rents.return_date "
                    "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                    "INNER JOIN customer ON rents.c_id = customer.customer_id "
                    "INNER JOIN book ON book.isbn = book_copy.copy_isbn ORDER BY rents.start_date DESC")

        rows = mydb.fetchall()
        for i in range(numRows):
            for j in range(numColumn):
                if j == 9 and rows[i][9] == None:
                    self.hist_table.setItem(i, j, QTableWidgetItem(str('To be returned')))
                    continue
                self.hist_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))

    def display_books(self, search = False, searchfor = None):          #SEARCH == TRUE - MEANING DISPLAYING FOR A SEARCH, SEARCHFOR = SEARCHED KEYWORD
        hheader = self.book_table.horizontalHeader()          
        hheader.setSectionResizeMode(QHeaderView.Stretch)
        vheader = self.book_table.verticalHeader()
        vheader.setSectionResizeMode(QHeaderView.Fixed)        
        vheader.setDefaultSectionSize(50)
        numColumn = 7

        if search == True and searchfor != None:                        #if displaying a search
            mydb.execute(f"SELECT COUNT(*) FROM book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%'")
            numRows = mydb.fetchone()
            numRows = numRows[0]
            self.book_table.setColumnCount(numColumn+1)
            self.book_table.setRowCount(numRows)
            self.book_table.setHorizontalHeaderLabels(self.headerlabels)
            
            mydb.execute(f"SELECT isbn, genre, author, publish_date, book_title, price from book WHERE book_title LIKE '%{searchfor}%' OR author LIKE '%{searchfor}%'")
            rows = mydb.fetchall()
            
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

        
        elif search == False and searchfor == None:     #default display
            mydb.execute("SELECT COUNT(*) FROM book")
            numRows = mydb.fetchone()
            numRows = numRows[0]
            self.book_table.setColumnCount(numColumn+1)
            self.book_table.setRowCount(numRows)
            self.book_table.setHorizontalHeaderLabels(self.headerlabels)
            
            mydb.execute("SELECT isbn, genre, author, publish_date, book_title, price from book")
            rows = mydb.fetchall()
    
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
                            print("I GOT HERE TOO")

                            continue
                        self.book_table.setItem(i, j, QTableWidgetItem(str(rows[i][j])))
                    
                actionWidget = self.make_buttons(i)            #REFER TO makebuttons function for details
                self.book_table.setCellWidget(i, 7, actionWidget)
            print("I GOT HERE")

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
    login.user_login.pressed.connect(lambda: make_window(login))

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