from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date, timedelta
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key"
DB = Path(__file__).with_name("library.db")

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    with connect() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            total_copies INTEGER NOT NULL CHECK(total_copies > 0),
            available_copies INTEGER NOT NULL CHECK(available_copies >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
            borrower TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            returned_date TEXT,
            fine REAL NOT NULL DEFAULT 0
        );
        """)

@app.get("/")
def index():
    q = request.args.get("q", "").strip()
    with connect() as db:
        if q:
            books = db.execute("""SELECT * FROM books WHERE title LIKE ? OR author LIKE ?
                               ORDER BY id DESC""", (f"%{q}%", f"%{q}%")).fetchall()
        else:
            books = db.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
        stats = db.execute("""SELECT COUNT(*) titles, COALESCE(SUM(total_copies),0) copies,
                           COALESCE(SUM(total_copies-available_copies),0) issued FROM books""").fetchone()
        active = db.execute("""SELECT l.*, b.title FROM loans l JOIN books b ON b.id=l.book_id
                               WHERE l.returned_date IS NULL ORDER BY l.due_date""").fetchall()
    return render_template("index.html", books=books, stats=stats, active=active, q=q, today=date.today().isoformat())

@app.post("/books")
def add_book():
    title=request.form.get("title","").strip()
    author=request.form.get("author","").strip()
    try: copies=int(request.form.get("copies","1"))
    except ValueError: copies=0
    if not title or not author or copies < 1:
        flash("Enter a title, author and a valid copy count.", "error")
    else:
        with connect() as db:
            db.execute("INSERT INTO books(title,author,total_copies,available_copies) VALUES(?,?,?,?)",
                       (title,author,copies,copies))
        flash("Book added successfully.", "success")
    return redirect(url_for("index"))

@app.post("/books/<int:book_id>/delete")
def delete_book(book_id):
    with connect() as db:
        active=db.execute("SELECT COUNT(*) FROM loans WHERE book_id=? AND returned_date IS NULL",(book_id,)).fetchone()[0]
        if active:
            flash("Return all issued copies before deleting this book.", "error")
        else:
            db.execute("DELETE FROM books WHERE id=?",(book_id,))
            flash("Book deleted.", "success")
    return redirect(url_for("index"))

@app.post("/books/<int:book_id>/issue")
def issue_book(book_id):
    borrower=request.form.get("borrower","").strip()
    try: qty=int(request.form.get("quantity","1"))
    except ValueError: qty=0
    with connect() as db:
        book=db.execute("SELECT * FROM books WHERE id=?",(book_id,)).fetchone()
        if not book:
            flash("Book not found.", "error")
        elif not borrower or qty < 1 or qty > book["available_copies"]:
            flash("Enter a borrower and a quantity within available copies.", "error")
        else:
            issued=date.today()
            due=issued+timedelta(days=14)
            db.execute("INSERT INTO loans(book_id,borrower,quantity,issue_date,due_date) VALUES(?,?,?,?,?)",
                       (book_id,borrower,qty,issued.isoformat(),due.isoformat()))
            db.execute("UPDATE books SET available_copies=available_copies-? WHERE id=?",(qty,book_id))
            flash(f"Issued {qty} cop(y/ies). Due date: {due.isoformat()}.", "success")
    return redirect(url_for("index"))

@app.post("/loans/<int:loan_id>/return")
def return_book(loan_id):
    with connect() as db:
        loan=db.execute("SELECT * FROM loans WHERE id=? AND returned_date IS NULL",(loan_id,)).fetchone()
        if not loan:
            flash("Active loan not found.", "error")
        else:
            returned=date.today()
            days_late=max(0,(returned-date.fromisoformat(loan["due_date"])).days)
            fine=days_late*2.0*loan["quantity"]
            db.execute("UPDATE loans SET returned_date=?, fine=? WHERE id=?",(returned.isoformat(),fine,loan_id))
            db.execute("UPDATE books SET available_copies=available_copies+? WHERE id=?",(loan["quantity"],loan["book_id"]))
            msg=f"Book returned. Fine: ₹{fine:.2f}" if fine else "Book returned successfully. No fine."
            flash(msg,"success")
    return redirect(url_for("index"))

@app.get("/api/books")
def api_books():
    with connect() as db:
        rows=db.execute("SELECT * FROM books ORDER BY id DESC").fetchall()
    return {"books":[dict(r) for r in rows]}

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
