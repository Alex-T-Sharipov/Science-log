from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///labs.db")

# Ensure responses aren't cached

@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    return render_template("about.html")

@app.route("/addlab", methods=["GET", "POST"])
@login_required
def addlab():
    return render_template("addlab.html")

@app.route("/addproject", methods=["GET", "POST"])
@login_required
def addproject():
    return render_template("addproject.html")

@app.route("/addexperiments", methods=["GET", "POST"])
@login_required
def addtemplate():
    return render_template("addexperiment.html")

@app.route("/addcontributor", methods=["GET", "POST"])
@login_required
def addcontributor():
    return render_template("addcontributor.html")

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    #show the current labs
    if request.method == "GET":
        rows=db.execute("SELECT * FROM lab WHERE user_id = ?", session["user_id"])
        l = []
        for row in rows:
            l.append(
                {"name": row["name"],
                "address": row["address"],
                "pi": row["pi"],
                "email": row["email"],
                "phone": row["phone"]}
                )
        if len(l) == 0:
            return render_template("nolabs.html")
        return render_template("index.html", l = l)
    if request.method == "POST":
        name = request.form.get("lab_name")
        address = request.form.get("lab_address")
        pi = request.form.get("pi")
        email = request.form.get("lab_email")
        phone = request.form.get("lab_phone")
        
        if not name or not address or not pi or not email or not phone:
            return(apology("Please fill out all of the fields"))
        if not phone.isnumeric():
            return(apology("Please only enter numbers in the phone field"))
            
        lab_id = db.execute("SELECT id FROM lab WHERE(user_id = ? AND name = ?)", session["user_id"], name)
        
        if len(lab_id) > 0:
            return(apology("Lab with the specified name already exists"))
        
        
        db.execute("INSERT INTO lab (user_id, name, address, pi, email, phone) VALUES(?, ?, ?, ?, ?, ?)", session["user_id"], name, address, pi, email, phone)
        return redirect("/")
        

@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    #show the current labs
    if request.method == "GET":
        rows=db.execute("SELECT * FROM projects WHERE lab_id = (SELECT id FROM lab WHERE user_id = ?)", session["user_id"])
        l = []
        for row in rows:
            l.append(
                {"name": row["name"],
                "timeline": row["timeline"],
                "status": row["status"],
                "objectives": row["objectives"]}
                )
        if len(l) == 0:
            return render_template("noprojects.html")
        
        return render_template("projects.html", l = l)
    
    if request.method == "POST":
        name = request.form.get("project_name")
        timeline = request.form.get("timeline")
        status = request.form.get("status")
        objectives = request.form.get("objectives")
        lab = request.form.get("labname")
        
        if not name or not timeline or not status or not objectives:
            return(apology("Please fill out all of the fields"))
        
        lab_id = db.execute("SELECT id FROM lab WHERE(user_id = ? AND name = ?)", session["user_id"], lab)
        
        if len(lab_id) == 0:
            return(apology("The lab with the specified name doesn't seem to exist"))
        
        project_id = db.execute("SELECT id FROM projects WHERE(name = ? AND lab_id in(SELECT id FROM lab WHERE(user_id=?)))", lab, session["user_id"])
        
        if len(project_id) > 0:
            return(apology("The project with the specified name already exists"))
        
        db.execute("INSERT INTO projects (lab_id, name, timeline, status, objectives) VALUES(?, ?, ?, ?, ?)", lab_id[0]["id"], name, timeline, status, objectives)
        return redirect("/projects")

@app.route("/experiments", methods=["GET", "POST"])
@login_required
def experiments():
    #show the current labs
    if request.method == "GET":
        rows=db.execute("SELECT * FROM experiments WHERE project_id = (SELECT id FROM lab WHERE user_id = ?)", session["user_id"])
        l = []
        for row in rows:
            l.append(
                {"date": row["date"],
                "description": row["description"],
                "name": row["name"]
                })
        if len(l) == 0:
            return render_template("noexperiments.html")
        
        return render_template("experiments.html", l = l)
    if request.method == "POST":
        name = request.form.get("experiment_name")
        date = request.form.get("date")
        description = request.form.get("description")
        projectname = request.form.get("projectname")
        
        if not name or not date or not description or not projectname:
            return(apology("Please fill out all of the fields"))
        
        project_id = db.execute("SELECT id FROM projects WHERE(name = ? AND lab_id in(SELECT id FROM lab WHERE(user_id=?)))", projectname, session["user_id"])
        if len(project_id)==0:
            return apology("The project with the specified name doesn't seem to exist")
        experiment_id = db.execute("SELECT id FROM experiments WHERE(name=? AND project_id in(SELECT id FROM projects WHERE(lab_id in (SELECT id FROM lab WHERE(user_id=?)))))", name, session["user_id"])
        
        if len(experiment_id)>0:
            return apology("Experiment with the specified name already exists")

        db.execute("INSERT INTO experiments (project_id, date, name, description) VALUES(?, ?, ?, ?)", project_id[0]["id"], date, name, description)
        return redirect("/experiments")

@app.route("/contributors", methods=["GET", "POST"])
@login_required
def contributors():
    #show the current labs
    if request.method == "GET":
        rows=db.execute("SELECT * FROM contributors WHERE project_id = (SELECT id FROM lab WHERE user_id = ?)", session["user_id"])
        l = []
        for row in rows:
            l.append(
                {"phone": row["phone"],
                "email": row["email"],
                "name": row["name"]
                })
        if len(l) == 0:
            return render_template("nocontributors.html")
        
        return render_template("contributors.html", l = l)
    if request.method == "POST":
        name = request.form.get("contributor_name")
        email = request.form.get("contributor_email")
        phone = request.form.get("contributor_phone")
        projectname = request.form.get("projectname")
        
        if not name or not email or not phone or not projectname:
            return(apology("Please fill out all of the fields"))
        if not phone.isnumeric():
            return(apology("Please only enter numbers in the phone field"))
        
        project_id = db.execute("SELECT id FROM projects WHERE(name = ? AND lab_id in(SELECT id FROM lab WHERE(user_id=?)))", projectname, session["user_id"])
        if len(project_id)==0:
            return apology("The project with the specified name doesn't seem to exist")
        contributor_id = db.execute("SELECT id FROM contributors WHERE(name=? AND project_id in(SELECT id FROM projects WHERE(lab_id in(SELECT id FROM lab WHERE(user_id=?)))))", name, session["user_id"])
        
        if len(contributor_id)>0:
            return apology("Contributor with the specified name already exists")

        db.execute("INSERT INTO contributors (project_id, name, email, phone) VALUES(?, ?, ?, ?)", project_id[0]["id"], name, email, phone)
        return redirect("/contributors")

@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    return render_template("add.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Handle 2 separate cases. 
    # (1) request.method=='POST' would mean that the user has provided some data
    # (2) request.method=='GET' would mean that the user has just clicked on the register button from login page
    
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            return apology("Please enter your username", 400)
        if not password:
            return apology("Please enter your password", 400)
        if not confirmation:
            return apology("Please enter password confirmation", 400)
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) > 0:
            return apology("This username is already taken")
        if not password == confirmation:
            return apology("Passwords don't match", 400)
        
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))
        return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/pass", methods=["GET", "POST"])
@login_required
def password():
    """Change password"""
    if request.method == "GET":
        return render_template("pass.html")
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        if not request.form.get("new_pass1") == request.form.get("confirmation"):
            return apology("passwords don't match")
        
        db.execute("UPDATE users SET hash = ? WHERE id = ?",  generate_password_hash(request.form.get("new_pass1")), session["user_id"])
        
        return redirect("/logout")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)