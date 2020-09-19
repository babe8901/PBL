import os

from flask import Flask, session, request, render_template
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods = ["POST"])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    Mobile_No = request.form.get('Mobile_No')
    DOB = request.form.get('DOB')
    gender = request.form.get('gender')
    password = request.form.get('password')
    password_check = request.form.get('password_check')

    if (password != password_check):
        return render_template("error.html", message = "Passwords do not match!")
    
    # db.execute('''
    # DROP TABLE IF EXISTS Users;
    # DROP TABLE IF EXISTS Password;
    # DROP TABLE IF EXISTS Contact;

    # CREATE TABLE Users(
    # id SERIAL PRIMARY KEY,
    # firstname TEXT NOT NULL,
    # lastname TEXT NOT NULL,
    # DOB TEXT NOT NULL,
    # Contact_id INT,
    # Password_id INT
    # );

    # CREATE TABLE Contact(
    # id SERIAL PRIMARY KEY,
    # email TEXT NOT NULL UNIQUE,
    # Mobile_No TEXT NOT NULL UNIQUE
    # );

    # CREATE TABLE Password(
    # id SERIAL PRIMARY KEY,
    # password TEXT NOT NULL
    # )
    # ''')

    x = db.execute("SELECT * FROM Contact WHERE email = :email OR Mobile_No = :Mobile_No", {"email" : email, "Mobile_No" : Mobile_No}).fetchone()
    if x is not None:
        return render_template("error.html", message = "Email or Mobile no. or both already in use for another account.")
    db.execute("INSERT INTO Contact(email, Mobile_No) VALUES(:email, :Mobile_No) ON CONFLICT DO NOTHING", {"email" : email, "Mobile_No" : Mobile_No})
    Contact_id = db.execute("SELECT id FROM Contact WHERE email = :email", {"email" : email}).fetchone()
    if Contact_id is None:
        return render_template("error.html", message = "Email or Mobile no. already registered")

    db.execute("INSERT INTO Password(password) VALUES(:password)", {"password" : password})
    Password_id = db.execute("SELECT id FROM Password WHERE password = :password", {"password" : password}).fetchone()

    db.execute("INSERT INTO Users(firstname, lastname, DOB, Contact_id, Password_id) VALUES(:firstname, :lastname, :DOB, :Contact_id, :Password_id)",
            {"firstname" : firstname, "lastname" : lastname, "DOB" : DOB, "Contact_id" : Contact_id[0], "Password_id" : Password_id[0]})

    db.commit()

    return render_template("success.html", message = "Registration Successful.")

@app.route("/login", methods = ["POST", "GET"])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    x = db.execute("SELECT * FROM Users, Contact, Password WHERE Contact_id = Contact.id AND Password_id = Password.id AND password = :password AND email = :email", {"password" : password, "email" : email}).fetchone()
    if x is None:
        return render_template("error.html", message = "Wrong Credentials.")
    print(x)
    newline  = '\n'
    s = f"Hello {x[1]} {x[2]}.{newline}Welcome to our Transportation portal."
    return render_template("welcome.html", message = s)

@app.route("/x", methods = ["GET"])
def x():
    return render_template("login.html")

@app.route("/y", methods = ["GET"])
def y():
    return render_template("register.html")