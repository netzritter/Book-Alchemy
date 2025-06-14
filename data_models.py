from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'library.sqlite')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)
    books = db.relationship('Book', back_populates='author')

    def __repr__(self):
        return f"<Author {self.id}: {self.name}>"

    def __str__(self):
        return f"{self.name} (Born: {self.birth_date}, Died: {self.date_of_death or 'N/A'})"

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20))
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', back_populates='books')

    def __repr__(self):
        return f"<Book {self.id}: {self.title}>"

    def __str__(self):
        return f"'{self.title}' by Author ID {self.author_id} ({self.publication_year})"

# ✅ Run this ONCE to create the tables
with app.app_context():
    db.create_all()
