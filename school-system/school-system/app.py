from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "schoolsecret"

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =========================
# USER TABLE
# =========================
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

# =========================
# TIMETABLE TABLE
# =========================
class Timetable(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100))

    period = db.Column(db.String(10))

    subject = db.Column(db.String(100))

    room = db.Column(db.String(100))

    teacher = db.Column(db.String(100))

# =========================
# CREATE DATABASE + TEST USER
# =========================
with app.app_context():

    db.create_all()

    existing_user = User.query.filter_by(
        username="student"
    ).first()

    if not existing_user:

        user = User(
            username="student",
            password="1234"
        )

        db.session.add(user)

        timetable_data = [

            Timetable(
                username="student",
                period="1",
                subject="English Standard Y12",
                room="E13",
                teacher="Miss K. Waters"
            ),

            Timetable(
                username="student",
                period="2",
                subject="Software Engineering Y12",
                room="C04",
                teacher="Mr A. Zhukov"
            ),

            Timetable(
                username="student",
                period="3",
                subject="Industrial Technology: Multimedia",
                room="G1MAC",
                teacher="Miss S. El Tantawy"
            ),

            Timetable(
                username="student",
                period="4",
                subject="Math Standard ATAR Pathway Yr12",
                room="HP01",
                teacher="Mr A. Miao"
            ),

            Timetable(
                username="student",
                period="5",
                subject="Enterprise Computing Y12",
                room="C04",
                teacher="Mr C. Kumar"
            ),

            Timetable(
                username="student",
                period="6",
                subject="Study",
                room="STUDY_LIB",
                teacher="Ms D. Hatzimanolis . STUDYROSTER",
            )
        ]

        for item in timetable_data:
            db.session.add(item)

        db.session.commit()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user"] = username

            return redirect(url_for("dashboard"))

        else:

            return "Invalid login"

    return render_template("login.html")

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

# =========================
# TIMETABLE
# =========================
@app.route("/timetable")
def timetable():

    if "user" not in session:
        return redirect(url_for("login"))

    user_timetable = Timetable.query.filter_by(
        username=session["user"]
    ).all()

    return render_template(
        "timetable.html",
        timetable=user_timetable
    )

# =========================
# EVENTS
# =========================
@app.route("/events")
def events():

    return render_template("events.html")

# =========================
# CANTEEN
# =========================
@app.route("/canteen")
def canteen():

    return render_template("canteen.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))

# =========================
# RUN APP
# =========================
if __name__ == "__main__":

    app.run(debug=True)