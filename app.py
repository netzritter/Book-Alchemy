from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from data_models import db, Author, Book
from sqlalchemy import or_
import os
import secrets
import requests  # For Google Books API

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(basedir, 'data'), exist_ok=True)
db_path = os.path.join(basedir, 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# 🔍 Helper: Get cover from Google Books
def get_google_cover_url(isbn):
    try:
        clean_isbn = isbn.replace('-', '')
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{clean_isbn}"
        response = requests.get(url)
        data = response.json()
        if 'items' in data:
            return data['items'][0]['volumeInfo']['imageLinks']['thumbnail']
    except Exception as e:
        print(f"Failed to get cover for ISBN {isbn}: {e}")
    return None

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = request.form.get('birth_date')
        date_of_death = request.form.get('date_of_death')

        try:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            date_of_death = datetime.strptime(date_of_death, '%Y-%m-%d').date() if date_of_death else None

            new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
            db.session.add(new_author)
            db.session.commit()

            flash('Author added successfully!', 'success')
            return redirect(url_for('add_author'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('add_author.html')

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        try:
            new_book = Book(
                title=title,
                isbn=isbn,
                publication_year=int(publication_year),
                author_id=int(author_id)
            )
            db.session.add(new_book)
            db.session.commit()

            flash('Book added successfully!', 'success')
            return redirect(url_for('add_book'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('add_book.html', authors=authors)

@app.route('/')
def home():
    sort_by = request.args.get('sort_by', 'title')
    search = request.args.get('search', '').strip()

    query = Book.query.join(Author)

    if search:
        query = query.filter(
            or_(
                Book.title.ilike(f"%{search}%"),
                Author.name.ilike(f"%{search}%")
            )
        )

    if sort_by == 'author':
        query = query.order_by(Author.name)
    else:
        query = query.order_by(Book.title)

    books = query.all()

    # Add cover_url for each book using Google Books API
    for book in books:
        if book.isbn:
            book.cover_url = get_google_cover_url(book.isbn)
        else:
            book.cover_url = None

    return render_template('home.html', books=books, sort_by=sort_by, search=search)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    try:
        db.session.delete(book)
        db.session.commit()

        # Check if the author has any other books
        remaining_books = Book.query.filter_by(author_id=author.id).count()
        if remaining_books == 0:
            db.session.delete(author)
            db.session.commit()

        flash(f'Book "{book.title}" was successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'danger')

    return redirect(url_for('home'))


# ✅ Run the server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5002)



