from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models 123
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Integer, default=1)
    available = db.Column(db.Integer, default=1)
    transactions = db.relationship('Transaction', backref='book', lazy=True)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Active')
    transactions = db.relationship('Transaction', backref='member', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(15), unique=True, nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='Active')

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books', methods=['GET'])
def books():
    search = request.args.get('search', '')
    if search:
        books = Book.query.filter(
            (Book.title.contains(search)) |
            (Book.author.contains(search)) |
            (Book.isbn.contains(search))
        ).all()
    else:
        books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        book = Book(
            isbn=request.form['isbn'],
            title=request.form['title'],
            author=request.form['author'],
            category=request.form['category'],
            quantity=1,
            available=1
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!', 'success')
    except Exception as e:
        flash('Error adding book: ' + str(e), 'danger')
    return redirect(url_for('books'))

@app.route('/edit_book/<int:book_id>', methods=['POST'])
def edit_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        book.isbn = request.form['isbn']
        book.title = request.form['title']
        book.author = request.form['author']
        book.category = request.form['category']
        db.session.commit()
        flash('Book updated successfully!', 'success')
    except Exception as e:
        flash('Error updating book: ' + str(e), 'danger')
    return redirect(url_for('books'))

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        if book.transactions:
            flash('Cannot delete book with associated transactions!', 'danger')
        else:
            db.session.delete(book)
            db.session.commit()
            flash('Book deleted successfully!', 'success')
    except Exception as e:
        flash('Error deleting book: ' + str(e), 'danger')
    return redirect(url_for('books'))

@app.route('/members', methods=['GET'])
def members():
    search = request.args.get('search', '')
    if search:
        members = Member.query.filter(
            (Member.name.contains(search)) |
            (Member.email.contains(search)) |
            (Member.member_id.contains(search))
        ).all()
    else:
        members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['POST'])
def add_member():
    try:
        member = Member(
            member_id=f"M{datetime.now().strftime('%Y%m%d%H%M%S')}",
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone']
        )
        db.session.add(member)
        db.session.commit()
        flash('Member added successfully!', 'success')
    except Exception as e:
        flash('Error adding member: ' + str(e), 'danger')
    return redirect(url_for('members'))

@app.route('/transactions', methods=['GET'])
def transactions():
    search = request.args.get('search', '')
    type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    
    query = Transaction.query
    
    if search:
        query = query.join(Member).join(Book).filter(
            (Member.name.contains(search)) |
            (Book.title.contains(search))
        )
    
    if type_filter:
        query = query.filter(Transaction.type == type_filter)
    
    if status_filter:
        query = query.filter(Transaction.status == status_filter)
    
    transactions = query.order_by(Transaction.issue_date.desc()).all()
    members = Member.query.filter_by(status='Active').all()
    available_books = Book.query.filter(Book.available > 0).all()
    
    return render_template('transactions.html', 
                         transactions=transactions,
                         members=members,
                         available_books=available_books)

@app.route('/view_transaction/<int:transaction_id>')
def view_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template('view_transaction.html', transaction=transaction)

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    try:
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
        
        book = Book.query.get(book_id)
        if book.available <= 0:
            flash('Book is not available for borrowing!', 'danger')
            return redirect(url_for('transactions'))
        
        transaction = Transaction(
            transaction_id=f"T{datetime.now().strftime('%Y%m%d%H%M%S')}",
            book_id=book_id,
            member_id=member_id,
            due_date=due_date
        )
        
        book.available -= 1
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction created successfully!', 'success')
    except Exception as e:
        flash('Error creating transaction: ' + str(e), 'danger')
    return redirect(url_for('transactions'))

@app.route('/return_book/<int:transaction_id>', methods=['POST'])
def return_book(transaction_id):
    try:
        transaction = Transaction.query.get(transaction_id)
        if transaction and transaction.status == 'Active':
            transaction.status = 'Completed'
            transaction.return_date = datetime.utcnow()
            transaction.book.available += 1
            db.session.commit()
            flash('Book returned successfully!', 'success')
        else:
            flash('Invalid transaction or book already returned!', 'danger')
    except Exception as e:
        flash('Error returning book: ' + str(e), 'danger')
    return redirect(url_for('transactions'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 