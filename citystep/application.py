import os
import time
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///citystep.db")


# Display people on user's homepage
@app.route("/")
@login_required
def index():
    print("IM HERE")
    info = db.execute("SELECT activity FROM history WHERE user_id = :user_id", user_id = session['user_id'])
    print("query worked")
    a =[]
    for i in range(len(info)):
        a.append(info[i]['activity'])

    print(a)
    return render_template("index.html", info = info)

# Allow user to edit profile of person
@app.route("/edit/<name>", methods=["GET", "POST"])
@login_required
def edit(name):
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Update profile based on information
        name = request.form.get("first") + " " + request.form.get("last")
        age = request.form.get("age")
        gender = request.form.get("Gender")
        price_min = request.form.get("min")
        price_max = request.form.get("max")
        relation = request.form.get("relation")
        occasion = request.form.get("occasion")
        user_id = session["user_id"]
        ti = time.strftime('%Y-%m-%d %H:%M:%S')

        db.execute("UPDATE people SET gender = :gender, age = :age, price_min = :price_min, price_max = :price_max, relation = :relation, occasion = :occasion, modified = :ti WHERE name = :name",
                    gender=gender, age=age, price_min=price_min, price_max=price_max, relation = relation, occasion = occasion, ti = ti, name = name)

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Pass in information to form for default values
        info = db.execute("SELECT occasion, relation, price_min, price_max, age, gender FROM people WHERE name = :name", name = name)
        a={}
        a['occasion'] = info[0]['occasion']
        a['first'] = name.split(" ")[0]
        a['last'] = name.split(" ")[1]
        a['relation'] = info[0]['relation']
        a['price_min'] = info[0]['price_min']
        a['price_max'] = info[0]['price_max']
        a['age'] = info[0]['age']
        a['gender'] = info[0]['gender']
        return render_template("edit.html", a = a)

# Display list of appropriate gifts when name is clicked
@app.route('/profile', methods=['POST'])
@login_required
def profile():
    print("yea buddy")
    activity = request.form.get("activity")
    user_id = session["user_id"]
    db.execute("INSERT INTO history (user_id, activity) VALUES (?, ?)", user_id, activity)

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
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        print("IM HERE")

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

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

# Add a new person profile
@app.route("/chooseactivity", methods=["GET", "POST"])
@login_required
def addact():

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        print('this is working 1')
        #Check for appropriate inputs
        if not request.form.get("Size"):
            return apology("must provide group size", 403)

        if not request.form.get("Value"):
            return apology("must provide a Core Value", 403)

        if not request.form.get("Type"):
            return apology("must provide an activity type", 403)

        a = []
        size = request.form.get("Size")
        value = request.form.get("Value")
        typeA = request.form.get("Type")

        user_id = session["user_id"]
        ti = time.strftime('%Y-%m-%d %H:%M:%S')

        activities = db.execute("SELECT act_id FROM activities")
        b = {}
        for activity in activities:
            score = 0
            act_id = activity['act_id']
            one = db.execute("SELECT Size FROM activities WHERE act_id = :act_id", act_id = act_id)
            print("first", one[0]['Size'])
            print("second", size)
            if one[0]['Size'] == size:
                score+=1
            print("score after size ", score)
            two = db.execute("SELECT Corevalue FROM activities WHERE act_id = :act_id", act_id = act_id)
            if two[0]['Corevalue'] == value:
                score+=1
            print("score after value ", score)

            three = db.execute("SELECT Type FROM activities WHERE act_id = :act_id", act_id = act_id)
            if three[0]['Type'] == typeA:
                score+=1

            print("score after type ", score)

            four = db.execute("SELECT Name FROM activities WHERE act_id = :act_id", act_id = act_id)
            if score == 3:
                b = {}
                b['name'] = four[0]['Name']
                a.append(b)

        b = {}
        b['name'] = 'test'
        a.append(b)

        print('this is working 2')
        return render_template("profile.html", a = a)


    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("addact.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 403)

        # Ensure passwords are equal
        elif (request.form.get("password") != request.form.get("confirmation")):
            return apology("passwords must match", 403)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists
        if len(rows) > 0:
            return apology("username is taken", 403)


        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), generate_password_hash(request.form.get("password")))

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

def isNotValid(password):
    haveDig = False
    haveSpecial = False
    if len(password) < 8:
        return True
    for i in range(len(password)):
        if (password[i].isdigit()):
            haveDig = True
        elif (password[i] == "!" or password[i] == "?" or password[i] == "."):
            haveSpecial = True
    if (haveDig and haveSpecial):
        return False
    else:
        return True

#Deletes person's profile
@app.route("/delete/<name>", methods=["GET"])
@login_required
def delete(name):
    db.execute("DELETE FROM people WHERE name = :name", name = name)
    return redirect("/")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
