from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

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

# ---------------- INITIALIZE DATABASE ----------------
def init_db():
    db = get_db()
    # Create users table
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    # Create houses table
    db.execute('''
        CREATE TABLE IF NOT EXISTS houses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            location TEXT,
            price TEXT,
            status TEXT DEFAULT 'For Rent'
        )
    ''')
    # Create rentals table
    db.execute('''
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_id INTEGER,
            user_name TEXT,
            email TEXT,
            phone TEXT,
            movein TEXT,
            message TEXT,
            FOREIGN KEY (house_id) REFERENCES houses(id)
        )
    ''')
    db.commit()

def seed_houses():
    db = get_db()
    count = db.execute("SELECT COUNT(*) as c FROM houses").fetchone()['c']
    if count == 0:
        houses = [
            ("Minglanilla 2-Bedroom Home", "Tunghaan, Minglanilla", "₱15,000 / month"),
            ("Bulosan 3-Bedroom Home", "Bulosan, Cebu City", "₱18,000 / month"),
            ("Minglanilla 3-Bedroom Villa", "Tunghaan, Minglanilla", "₱20,000 / month"),
            ("Bulosan 1-Bedroom Condo", "Bulosan, Cebu City", "₱12,000 / month"),
            ("Bulosan 2-Bedroom Apartment", "Bulosan, Cebu City", "₱14,000 / month"),
            ("Minglanilla 1-Bedroom Home", "Tunghaan, Minglanilla", "₱10,000 / month"),
            ("Bulosan 2-Bedroom Townhouse", "Bulosan, Cebu City", "₱16,000 / month"),
            ("Minglanilla 4-Bedroom Villa", "Tunghaan, Minglanilla", "₱25,000 / month"),
        ]
        for name, location, price in houses:
            db.execute("INSERT INTO houses (name, location, price) VALUES (?, ?, ?)", (name, location, price))
        db.commit()

# Initialize database and seed houses
with app.app_context():
    init_db()
    seed_houses()

# ---------------- ROUTES ----------------
@app.route('/')
def index_route():
    return redirect(url_for('login'))

# --------- SIGNUP ----------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for('signup'))
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, password))
            db.commit()
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or email already exists!", "danger")
            return redirect(url_for('signup'))
    return render_template('signup.html')

# --------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = request.args.get('message', '')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (username, password)).fetchone()
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

# --------- BULOSAN PAGES ----------
def get_bulosan_houses(start_id, end_id=None):
    db = get_db()
    if end_id:
        houses = db.execute("SELECT * FROM houses WHERE id >= ? AND id <= ? ORDER BY id",
                            (start_id, end_id)).fetchall()
    else:
        houses = db.execute("SELECT * FROM houses WHERE id >= ? ORDER BY id", (start_id,)).fetchall()
    return houses

@app.route('/bulosan')
def bulosan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(1, 4)
    return render_template('Bulosan.html', username=session.get('username'), houses=houses)

@app.route('/bulosan2')
def bulosan2():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(5, 8)
    return render_template('Bulosan2.html', houses=houses)

@app.route('/bulosan3')
def bulosan3():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(9, 12)
    return render_template('Bulosan3.html', houses=houses)

@app.route('/bulosan4')
def bulosan4():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(13, 16)
    return render_template('Bulosan4.html', houses=houses)

@app.route('/bulosan5')
def bulosan5():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(17, 20)
    return render_template('Bulosan5.html', houses=houses)

@app.route('/bulosan6')
def bulosan6():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    houses = get_bulosan_houses(21, 24)
    return render_template('Bulosan6.html', houses=houses)

# --------- RENT HOUSE ----------
@app.route('/rent/<int:house_id>', methods=['POST'])
def rent_house(house_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    house = db.execute("SELECT * FROM houses WHERE id=?", (house_id,)).fetchone()
    if not house:
        flash("House not found.", "danger")
        return redirect(request.referrer)
    if house['status'] == 'Rented':
        flash("This house is already rented.", "danger")
        return redirect(request.referrer)

    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    movein = request.form.get('movein')
    message = request.form.get('message', '')

    if not name or not email or not phone or not movein:
        flash("All fields are required to rent a house.", "danger")
        return redirect(request.referrer)

    # Update house status
    db.execute("UPDATE houses SET status='Rented' WHERE id=?", (house_id,))
    db.commit()

    # Save rental record
    db.execute("INSERT INTO rentals (house_id, user_name, email, phone, movein, message) VALUES (?, ?, ?, ?, ?, ?)",
               (house_id, name, email, phone, movein, message))
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
