import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import  check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
# Ensure user is logged in before continuing
@login_required
def index():
    """Show portfolio of stocks"""
    # Retrieve user id from current login session
    user = session["user_id"]
    # Define a variable called balance which represents the current user's cash balance from the users table
    balance = db.execute("SELECT cash FROM users WHERE id = ?", user)[0]['cash']
    # Repeat for stocks variable
    stocks = db.execute("SELECT symbol, SUM(shares) AS shares, price FROM portfolio WHERE user = ? GROUP BY symbol HAVING (SUM(shares)) > 0",
                        user)

    # Store stock information in an empty portfolio
    portfolio = {}
    total = 0
    for stock in stocks:
        # Use symbol, stocks & price values from stocks
        symbol = stock['symbol']
        shares = stock['shares']
        price = stock['price']
        # Calculate total value of shares from each stock
        stock = shares * price
        total += stock
        # Use lookup from helpers.py to add extra stock information to portfolio
        hence = lookup(symbol)
        name = hence['name']
        portfolio[symbol] = (name, shares, usd(price), usd(stock))
    total += balance

    return render_template("index.html", portfolio=portfolio, balance=balance, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        try_quote = get_quote(request.form, inspect.stack()[0][3])
        if try_quote[0]:
            quote = try_quote[1]
            quantity = try_quote[2]
        else:
            return apology(try_quote[1])

         # Check user has sufficient funds
        user_current_cash = db.execute("SELECT cash FROM users WHERE id = :user_id", user_id=session.get("user_id"))[0]["cash"]
        user_new_cash = user_current_cash - (quote["price"] * quantity)
        if user_new_cash < 0:
            return apology("Not enough funds")

        # Update database tables
        process_transaction(session.get("user_id"),
                            quote["symbol"],
                            quantity,
                            quote["price"],
                            user_new_cash)

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("buy_or_sell.html", buy_or_sell="buy")

@app.route("/history")
@login_required
def history():
    # Get users history
    users_transactions = db.execute('''SELECT symbol, shares, price, transaction_time
                                    FROM transactions
                                    WHERE id = :user_id
                                    ORDER BY transaction_time DESC''',
                                    user_id=session.get("user_id"))

    for row in users_transactions:
        if row["symbol"] == "Cash Deposit":
            row["name"] = "N/A"
            row["price"] = usd(row["price"])
        else:
            quote = lookup(row["symbol"])
            row["name"] = quote["name"]
            row["price"] = usd(quote["price"])

    return render_template("index.html",
                           table_type="History",
                           table_rows=users_transactions)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")

    else:
        # Input a stock's symbol
        symbol = lookup(request.form.get("Stock symbol"))

        # Ensure symbol is valid
        if symbol == None:
            return apology("Invalid symbol", 403)

    # Submit user's input via POST to /quote
    return render_template("quoted.html", symbol=symbol)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == 'POST':
        """Register user"""
        uname = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        status = True
        # check password confirmation
        if not request.form.get('password') == request.form.get('c-password'):
            status = False
            text = "Password confirmation not match"
        # check unique username
        exists_username= db.execute("SELECT username FROM users where username = :username", username = uname)
        if exists_username:
            status = False
            text = "Username already taken by another user"
        if status:
            # register
            register = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash)",
            username = uname, hash = password)
            text = "Registration Was Successful"
            # Remember which user has logged in
            session["user_id"] = register

            # Redirect user to home page
            return redirect("/")
        return apology(text)
        # return render_template('register.html', status = status, text = text)
    else:
        return render_template('register.html')



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    user = session["user_id"]

    if request.method == "POST":
        # Get the submitted symbol & shares values
        symbol = request.form.get('symbol')

        if symbol is None:
            return apology("Missing symbol", 400)

        shares = request.form.get('shares')

        # Convert shares to integer & account for error
        try:
            shares = int(shares)
            if shares < 1:
                return apology("Invalid shares", 400)
        except ValueError:
            return apology("Missing shares", 400)

        # Get stocks via symbol that the user owned_stocks
        owned_stocks = db.execute("SELECT DISTINCT(symbol) FROM portfolio WHERE user = ?", user)
        portfolio = {}
        for owned_stock in owned_stocks:
            key = owned_stock['symbol']
            portfolio[key] = (key)
        if symbol not in list(portfolio.values()):
            return apology("Symbol not owned_stocked", 400)

        # Total number of shares that a user owns in a stock
        stocks = db.execute("SELECT SUM(shares) AS shares FROM portfolio WHERE user = ? AND symbol = ?", user, symbol)[0]
        if shares > stocks['shares']:
            return apology("Too many shares", 400)
        # Lookup current price of stock
        price = lookup(symbol)['price']
        # Calculate current stock value in portfolio
        value = price * shares

        # Get user's current cash balance
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user)[0]['cash']
        cash += value

        # Update user's cash balance in database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user)
        db.execute("INSERT INTO portfolio (user, symbol, shares, price, date) values (?, ?, ?, ?, ?)",
                   user, symbol.upper(), -shares, value, datetime.now())
        flash("Sale successful!")
        return redirect("/")

    else:
        # NEED TO UPDATE WHICHEVER HTML PAGE TO RENDER
        stocks = db.execute("SELECT symbol FROM portfolio WHERE user = ? GROUP BY symbol", user)
        return render_template("?????.html", stocks=stocks)