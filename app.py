from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = 'database.db'


# ---------------- DATABASE CONNECTION ----------------
def get_db():
    if '_database' not in g:
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('_database', None)
    if db is not None:
        db.close()


# ---------------- ROUTES ----------------

@app.route('/')
def index_route():
    return redirect(url_for('login'))


# --------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            db.commit()
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists!", "danger")
            return redirect(url_for('signup'))

    return render_template('signup.html')


# --------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message', '')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin'] if 'is_admin' in user.keys() else 0

            if session['is_admin']:
                return redirect(url_for('home'))
            else:
                return redirect(url_for('bulosan'))
        else:
            message = "Invalid username or password!"

    return render_template('login.html', message=message)


# --------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login', message='You have successfully logged out.'))


# --------- ADMIN HOME ----------
@app.route('/home')
def home():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    db = get_db()
    houses = db.execute("SELECT * FROM houses").fetchall()
    return render_template('index.html', houses=houses, is_admin=True)


# --------- BULOSAN PAGE 1 ----------
@app.route('/bulosan')
def bulosan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    houses = db.execute("SELECT * FROM houses ORDER BY id LIMIT 4").fetchall()
    return render_template('Bulosan.html', username=session.get('username'), houses=houses)


# --------- BULOSAN PAGE 2 ----------
@app.route('/bulosan2')
def bulosan2():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    houses = db.execute("SELECT * FROM houses WHERE id > 4 AND id <= 8 ORDER BY id").fetchall()
    return render_template('Bulosan2.html', houses=houses)


# --------- BULOSAN PAGE 3 ----------
@app.route('/bulosan3')
def bulosan3():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('Bulosan3.html')


# --------- BULOSAN PAGE 4 ----------
@app.route('/bulosan4')
def bulosan4():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('Bulosan4.html')


# --------- BULOSAN PAGE 5 ----------
@app.route('/bulosan5')
def bulosan5():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('Bulosan5.html')


# --------- BULOSAN PAGE 6 ----------
@app.route('/bulosan6')
def bulosan6():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('Bulosan6.html')


# --------- RENT HOUSE ----------
@app.route('/rent/<int:house_id>', methods=['POST'])
def rent_house(house_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = get_db()
    house = db.execute("SELECT * FROM houses WHERE id=?", (house_id,)).fetchone()

    if not house:
        flash("House not found.", "danger")
        return redirect(url_for('bulosan2'))

    if house['status'] == 'Rented':
        flash("This house is already rented.", "danger")
        return redirect(url_for('bulosan2'))

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    movein = request.form['movein']
    message = request.form.get('message', '')

    # Update house status
    db.execute("UPDATE houses SET status='Rented' WHERE id=?", (house_id,))
    db.commit()

    # Save rental record
    db.execute(
        "INSERT INTO rentals (house_id, user_name, email, phone, movein, message) VALUES (?, ?, ?, ?, ?, ?)",
        (house_id, name, email, phone, movein, message)
    )
    db.commit()

    flash("Your rental application has been submitted successfully!", "success")

    # Redirect to the correct Bulosan page
    if house_id <= 4:
        return redirect(url_for('bulosan'))
    elif house_id <= 8:
        return redirect(url_for('bulosan2'))
    elif house_id <= 12:
        return redirect(url_for('bulosan3'))
    elif house_id <= 16:
        return redirect(url_for('bulosan4'))
    elif house_id <= 20:
        return redirect(url_for('bulosan5'))
    else:
        return redirect(url_for('bulosan6'))


# --------- ADMIN: UPDATE HOUSE STATUS ----------
@app.route('/update_status/<int:house_id>')
def update_status(house_id):
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    db = get_db()
    house = db.execute("SELECT * FROM houses WHERE id=?", (house_id,)).fetchone()

    if house:
        new_status = 'Rented' if house['status'] == 'For Rent' else 'For Rent'
        db.execute("UPDATE houses SET status=? WHERE id=?", (new_status, house_id))
        db.commit()

    return redirect(url_for('home'))


# ---------------- RUN APP ----------------
if __name__ == '__main__':
    app.run(debug=True)
