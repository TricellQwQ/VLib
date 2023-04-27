from flask import Flask, render_template, redirect, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.users import User
from data.books import Book
from forms.user import RegisterForm, LoginForm
from forms.bookcommon import BookCommonForm
from forms.bookopenlib import BookOpenlibForm
from requests import get

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    app.run()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", methods=["GET"])
def main():
    return render_template("main.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("registration.html", title="Регистрация", form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("registration.html", title="Регистрация", form=form, message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("registration.html", title="Регистрация", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/book_common', methods=['GET', 'POST'])
@login_required
def add_book_common():
    form = BookCommonForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Book()
        book.title = form.title.data
        book.description = form.description.data
        book.content = form.content.data
        book.author = form.author.data
        db_sess.add(book)
        db_sess.commit()
        return redirect('/library')
    return render_template('bookcommon.html', title='Add book', form=form)


@app.route('/book_openlib', methods=['GET', 'POST'])
@login_required
def add_book_openlib():
    form = BookOpenlibForm()
    if form.validate_on_submit():
        data = get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{form.openlibid.data}&format=json&jscmd=data").json()
        db_sess = db_session.create_session()
        book = Book()
        book.title = data[f"ISBN:{form.openlibid.data}"]["title"]
        book.description = form.description.data
        book.content = form.content.data
        book.author = data[f"ISBN:{form.openlibid.data}"]["authors"][0]["name"]
        db_sess.add(book)
        db_sess.commit()
        return redirect('/library')
    return render_template('bookopenlib.html', title='Add book', form=form)


@app.route("/library", methods=["GET", "POST"])
def library():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).filter(Book.user_id == None)
    return render_template("library.html", books=books)


@app.route("/book_get/<int:id>", methods=["GET", "POST"])
@login_required
def book_get(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id, Book.user_id == None).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    book.user_id = current_user.id
    user.books = id
    db_sess.commit()
    return redirect("/library")


@app.route("/book_delete/<int:id>", methods=["GET", "POST"])
@login_required
def book_delete(id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == id, Book.user_id == None).first()
    if book:
        db_sess.delete(book)
        db_sess.commit()
    else:
        abort(404)
    return redirect("/library")


@app.route("/my_book", methods=["GET", "POST"])
@login_required
def my_book():
    db_sess = db_session.create_session()
    book = db_sess.query(Book).filter(Book.id == current_user.books).first()
    return render_template("my_book.html", book=book)


@app.route("/book_return", methods=["GET", "POST"])
@login_required
def book_return():
    if current_user.books:
        db_sess = db_session.create_session()
        book = db_sess.query(Book).filter(Book.user_id == current_user.id).first()
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        book.user_id = None
        user.books = None
        db_sess.commit()
        return redirect("/library")
    return redirect("library")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/lib.db")
    app.run(port=8080, host='127.0.0.1', debug=True)