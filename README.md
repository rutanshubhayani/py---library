# Library Management System

A modern and user-friendly Library Management System built with Python, featuring a graphical user interface and SQLite database integration.

## Features

- Book Management (Add, Search, View)
- Member Management (Add, View)
- Borrowing System (Borrow, Return)
- Report Generation (PDF)
- Modern UI with Themed Interface
- Real-time Search Functionality

## Requirements

- Python 3.6 or higher
- Required Python packages (install using pip):
  ```
  ttkthemes==3.2.2
  Pillow==10.0.0
  reportlab==4.0.4
  ```

## Installation

1. Clone or download this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. The application will open with four main tabs:
   - Books Management: Add and manage books
   - Members Management: Add and manage library members
   - Borrowing Management: Handle book borrowing and returns
   - Reports: Generate PDF reports for books, members, and borrowings

## Database

The system uses SQLite as its database, which is automatically created when you first run the application. The database file (`library.db`) will be created in the same directory as the application.

## Features in Detail

### Books Management
- Add new books with title, author, ISBN, and quantity
- Search books by title, author, or ISBN
- View all books in a table format
- Track available copies

### Members Management
- Add new members with name, email, and phone
- View all members in a table format
- Track member join dates

### Borrowing Management
- Borrow books to members
- Return books
- View currently borrowed books
- Automatic due date calculation (14 days from borrow date)

### Reports
- Generate PDF reports for:
  - All books in the library
  - All members
  - Current borrowings

## Error Handling

The system includes comprehensive error handling for:
- Duplicate ISBNs
- Duplicate member emails
- Invalid book/member IDs
- Required field validation
- Book availability checks

## Contributing

Feel free to submit issues and enhancement requests! 