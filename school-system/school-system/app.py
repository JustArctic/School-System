# Import Flask modules for web pages, forms, redirects and sessions
from flask import Flask, render_template, request, redirect, url_for, session

# Import SQLAlchemy for database management
from flask_sqlalchemy import SQLAlchemy

# Create Flask application
app = Flask(__name__)

# Secret key used to manage user login sessions
app.secret_key = "schoolsecret"

# =========================
# DATABASE CONFIGURATION
# =========================

# Create SQLite database called school.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'

# Disable unnecessary tracking to improve performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise database
db = SQLAlchemy(app)

# =========================
# USER TABLE
# Stores login accounts
# =========================

class User(db.Model):

    # Unique user ID
    id = db.Column(db.Integer, primary_key=True)

    # Login username
    username = db.Column(db.String(100))

    # Login password
    password = db.Column(db.String(100))

    # User role (student/admin)
    role = db.Column(db.String(20))

# =========================
# TIMETABLE TABLE
# Stores student timetable data
# =========================

class Timetable(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # Student username linked to timetable
    username = db.Column(db.String(100))

    # School period
    period = db.Column(db.String(10))

    # Subject name
    subject = db.Column(db.String(100))

    # Classroom location
    room = db.Column(db.String(100))

    # Teacher name
    teacher = db.Column(db.String(100))

# =========================
# EVENT TABLE
# Stores school event information
# =========================

class Event(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    # Event date
    date = db.Column(db.String(50))

    # Event title
    title = db.Column(db.String(100))

    # Event location
    location = db.Column(db.String(100))

    # Event status (Upcoming, Completed etc.)
    status = db.Column(db.String(50))

    # Detailed event description
    description = db.Column(db.Text)

    # Event category
    category = db.Column(db.String(50))

# =========================
# DATABASE INITIALISATION
# Creates default users and data
# =========================

with app.app_context():

    # Create tables if they don't exist
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

    # Create administrator account
    if User.query.filter_by(username="admin").first() is None:

        db.session.add(
            User(
                username="admin",
                password="admin123",
                role="admin"
            )
        )

    # Add default timetable records once
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

        # Insert timetable records into database
        for item in timetable_data:
            db.session.add(item)

    # Create default school events
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

        # Insert events into database
        for event in default_events:
            db.session.add(event)

    # Save all changes
    db.session.commit()

# =========================
# LOGIN PAGE
# Authenticates users
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Check login credentials
        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            # Store user information in session
            session["user"] = username
            session["role"] = user.role

            return redirect(url_for("dashboard"))

        else:

            return "Invalid login"

    return render_template("login.html")

# =========================
# MAIN DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    # Prevent unauthorised access
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user=session["user"]
    )

# =========================
# TIMETABLE PAGE
# =========================

@app.route("/timetable")
def timetable():

    if "user" not in session:
        return redirect(url_for("login"))

    # Retrieve timetable for logged-in user
    user_timetable = Timetable.query.filter_by(
        username=session["user"]
    ).all()

    return render_template(
        "timetable.html",
        timetable=user_timetable
    )

# =========================
# EVENTS PAGE
# =========================

@app.route("/events")
def events():

    # Retrieve all school events
    all_events = Event.query.all()

    return render_template(
        "events.html",
        events=all_events
    )

# =========================
# CANTEEN PAGE
# =========================

@app.route("/canteen")
def canteen():

    return render_template("canteen.html")

# =========================
# LOGOUT
# Clears session data
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# =========================
# ADMIN DASHBOARD
# Allows event management
# =========================

@app.route("/admin")
def admin():

    # Check user is logged in
    if "user" not in session:
        return redirect(url_for("login"))

    # Restrict access to administrators
    if session.get("role") != "admin":
        return "Access Denied"

    events = Event.query.all()

    return render_template(
        "admin.html",
        events=events
    )

# =========================
# ADD NEW EVENT
# =========================

@app.route("/admin/add_event", methods=["POST"])
def add_event():

    if session.get("role") != "admin":
        return "Access Denied"

    # Create event from form data
    event = Event(

        title=request.form["title"],
        date=request.form["date"],
        location=request.form["location"],
        status=request.form["status"],
        category=request.form["category"],
        description=request.form["description"]
    )

    db.session.add(event)
    db.session.commit()

    return redirect("/admin")

# =========================
# DELETE EVENT
# =========================

@app.route("/admin/delete_event/<int:event_id>")
def delete_event(event_id):

    if session.get("role") != "admin":
        return "Access Denied"

    event = Event.query.get_or_404(event_id)

    db.session.delete(event)
    db.session.commit()

    return redirect(url_for("admin"))

# =========================
# EDIT EVENT
# =========================

@app.route("/admin/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):

    if session.get("role") != "admin":
        return "Access Denied"

    event = Event.query.get_or_404(event_id)

    if request.method == "POST":

        # Update event information
        event.title = request.form["title"]
        event.date = request.form["date"]
        event.location = request.form["location"]
        event.status = request.form["status"]
        event.category = request.form["category"]
        event.description = request.form["description"]

        db.session.commit()

        return redirect("/admin")

    return render_template(
        "edit_event.html",
        event=event
    )

# =========================
# START APPLICATION
# =========================

if __name__ == "__main__":

    # Run Flask development server
    app.run(debug=True)