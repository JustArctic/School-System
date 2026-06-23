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

    username = db.Column(db.String(100))

    password = db.Column(db.String(100))

    role = db.Column(db.String(20))

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

class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.String(50))

    title = db.Column(db.String(100))

    location = db.Column(db.String(100))

    status = db.Column(db.String(50))

# =========================
# CREATE DATABASE + DEFAULT DATA
# =========================
with app.app_context():

    db.create_all()

    # Create student account
    if User.query.filter_by(username="student").first() is None:

        db.session.add(
            User(
                username="student",
                password="1234",
                role="student"
            )
        )

    # Create admin account
    if User.query.filter_by(username="admin").first() is None:

        db.session.add(
            User(
                username="admin",
                password="admin123",
                role="admin"
            )
        )

    # Create timetable data once
    if Timetable.query.count() == 0:

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
                teacher="Ms D. Hatzimanolis"
            )
        ]

        for item in timetable_data:
            db.session.add(item)

    # Create default events once
    if Event.query.count() == 0:

        default_events = [

            Event(
                date="12 June",
                title="Athletics Carnival",
                location="School Oval",
                status="Upcoming"
            ),

            Event(
                date="18 June",
                title="Year 12 Careers Expo",
                location="Hall",
                status="Upcoming"
            ),

            Event(
                date="24 June",
                title="Parent Teacher Night",
                location="HP Block",
                status="Upcoming"
            )

        ]

        for event in default_events:
            db.session.add(event)

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
            session["role"] = user.role

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

    all_events = Event.query.all()

    return render_template(
        "events.html",
        events=all_events
    )

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

    session.clear()

    return redirect(url_for("login"))

# =========================
# ADMIN
# =========================
@app.route("/admin")
def admin():

    if "user" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access Denied"

    events = Event.query.all()

    return render_template(
        "admin.html",
        events=events
    )

@app.route("/admin/add_event", methods=["POST"])
def add_event():

    if session.get("role") != "admin":
        return "Access Denied"

    new_event = Event(

        date=request.form["date"],

        title=request.form["title"],

        location=request.form["location"],

        status=request.form["status"]
    )

    db.session.add(new_event)

    db.session.commit()

    return redirect(url_for("admin"))

@app.route("/admin/delete_event/<int:event_id>")
def delete_event(event_id):

    if session.get("role") != "admin":
        return "Access Denied"

    event = Event.query.get_or_404(event_id)

    db.session.delete(event)

    db.session.commit()

    return redirect(url_for("admin"))

# =========================
# RUN APP
# =========================
if __name__ == "__main__":

    app.run(debug=True)