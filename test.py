text=("SELECT rents.c_id, rents.cpy_no, customer.full_name, customer.phone_number, book.book_title, rents.rent_price, rents.start_date, rents.due_date, rents.penalizations "
                "FROM rents INNER JOIN book_copy ON book_copy.copy_number = rents.cpy_no "
                "INNER JOIN customer ON rents.c_id = customer.customer_id "
                f"INNER JOIN book ON book.isbn = book_copy.copy_isbn WHERE book_copy.book_status = 'Rented'")

x = 0
while x != 3:
    x = int(input('Enter number > '))

    if x == 1:
        print(text)
    else: 
        text = text + ' Try me'
        print(text)