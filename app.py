# app.py

from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, Note

app = Flask(__name__)
app.secret_key = "your-secret-key"  # needed for session
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])

    if request.method == "POST":
        if "delete" in request.form:
            Note.query.filter_by(user_id=user.id).delete()
        else:
            note_text = request.form["note"]
            new_note = Note(text=note_text, owner=user)
            db.session.add(new_note)
        db.session.commit()
        return redirect(url_for("home"))

    notes = Note.query.filter_by(user_id=user.id).all()
    return render_template("home.html", notes=notes)

@app.route("/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id == session.get("user_id"):
        db.session.delete(note)
        db.session.commit()
    return redirect(url_for("home"))

@app.route("/edit/<int:note_id>", methods=["GET", "POST"])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != session.get("user_id"):
        return redirect(url_for("home"))

    if request.method == "POST":
        note.text = request.form["new_text"]
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("edit.html", note=note)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Username already exists. Try a different one."

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return '''
        <h2>Register</h2>
        <form method="POST">
            Username: <input name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Register</button>
        </form>
        <p><a href="/login">Already have an account? Login</a></p>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            session["user_id"] = user.id
            return redirect(url_for("home"))
        return "Invalid username or password"

    return '''
        <h2>Login</h2>
        <form method="POST">
            Username: <input name="username" required><br>
            Password: <input type="password" name="password" required><br>
            <button type="submit">Login</button>
        </form>
        <p><a href="/register">New user? Register here</a></p>
    '''

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
