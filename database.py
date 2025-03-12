import sqlite3
from datetime import datetime, timedelta

class DatabaseHandler:
    def __init__(self):
        self.conn = sqlite3.connect('library.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Create Books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                quantity INTEGER NOT NULL,
                available INTEGER NOT NULL
            )
        ''')

        # Create Members table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL,
                join_date DATE NOT NULL
            )
        ''')

        # Create Borrowings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS borrowings (
                borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                member_id INTEGER,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                FOREIGN KEY (book_id) REFERENCES books (book_id),
                FOREIGN KEY (member_id) REFERENCES members (member_id)
            )
        ''')
        
        self.conn.commit()

    def add_book(self, title, author, isbn, quantity):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO books (title, author, isbn, quantity, available)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, author, isbn, quantity, quantity))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def add_member(self, name, email, phone):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO members (name, email, phone, join_date)
                VALUES (?, ?, ?, ?)
            ''', (name, email, phone, datetime.now().date()))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def borrow_book(self, book_id, member_id):
        cursor = self.conn.cursor()
        try:
            # Check if book is available
            cursor.execute('SELECT available FROM books WHERE book_id = ?', (book_id,))
            available = cursor.fetchone()[0]
            
            if available <= 0:
                return False, "Book not available"

            # Add borrowing record
            borrow_date = datetime.now().date()
            due_date = borrow_date + timedelta(days=14)  # 2 weeks lending period
            
            cursor.execute('''
                INSERT INTO borrowings (book_id, member_id, borrow_date, due_date)
                VALUES (?, ?, ?, ?)
            ''', (book_id, member_id, borrow_date, due_date))

            # Update book availability
            cursor.execute('''
                UPDATE books 
                SET available = available - 1 
                WHERE book_id = ?
            ''', (book_id,))
            
            self.conn.commit()
            return True, "Book borrowed successfully"
        except Exception as e:
            return False, str(e)

    def return_book(self, book_id, member_id):
        cursor = self.conn.cursor()
        try:
            # Update borrowing record
            cursor.execute('''
                UPDATE borrowings 
                SET return_date = ? 
                WHERE book_id = ? AND member_id = ? AND return_date IS NULL
            ''', (datetime.now().date(), book_id, member_id))

            # Update book availability
            cursor.execute('''
                UPDATE books 
                SET available = available + 1 
                WHERE book_id = ?
            ''', (book_id,))
            
            self.conn.commit()
            return True, "Book returned successfully"
        except Exception as e:
            return False, str(e)

    def get_all_books(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM books')
        return cursor.fetchall()

    def get_all_members(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM members')
        return cursor.fetchall()

    def get_borrowed_books(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT b.title, m.name, br.borrow_date, br.due_date 
            FROM borrowings br 
            JOIN books b ON br.book_id = b.book_id 
            JOIN members m ON br.member_id = m.member_id 
            WHERE br.return_date IS NULL
        ''')
        return cursor.fetchall()

    def search_books(self, query):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM books 
            WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        return cursor.fetchall()

    def close(self):
        self.conn.close() 