from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from data_models import db, Author, Book

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
db.init_app(app)

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