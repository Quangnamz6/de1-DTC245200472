import os
import psycopg2
from flask import Flask, request, redirect, render_template_string
from markupsafe import escape

app = Flask(__name__)

def db():
    return psycopg2.connect(
        host=os.environ["DB_HOST"], dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"], password=os.environ["POSTGRES_PASSWORD"])

def query(sql, params=(), fetch=True):
    conn = db()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall() if fetch else None
    finally:
        conn.close()

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>Quan ly Thu vien</title>
<style>body{font-family:sans-serif;max-width:900px;margin:20px auto}
table{border-collapse:collapse;width:100%;margin:10px 0}
td,th{border:1px solid #ccc;padding:6px}nav a{margin-right:15px}
form{margin:10px 0}</style></head><body>
<h2>He thong Quan ly Thu vien</h2>
<nav><a href="/">Sach</a><a href="/readers">Doc gia</a><a href="/loans">Muon/Tra</a></nav>
{{ body|safe }}</body></html>"""

def page(body):
    return render_template_string(PAGE, body=body)

@app.route("/health")
def health():
    query("SELECT 1")
    return "ok"

@app.route("/")
def books():
    rows = query("""SELECT b.id, b.title, b.author, b.copies,
        b.copies - COUNT(l.id) FILTER (WHERE l.returned_at IS NULL) AS available
        FROM books b LEFT JOIN loans l ON l.book_id=b.id
        GROUP BY b.id ORDER BY b.id""")
    trs = "".join(f"<tr><td>{r[0]}</td><td>{escape(r[1])}</td><td>{escape(r[2])}</td>"
                  f"<td>{r[3]}</td><td>{r[4]}</td></tr>" for r in rows)
    body = ("<h3>Danh sach sach</h3><table><tr><th>ID</th><th>Tieu de</th>"
            "<th>Tac gia</th><th>Tong</th><th>Con lai</th></tr>" + trs + "</table>"
            '<form method="post" action="/books">Tieu de <input name="title" required> '
            'Tac gia <input name="author" required> SL <input name="copies" type="number" '
            'value="1" min="1" style="width:50px"> <button>Them sach</button></form>')
    return page(body)

@app.route("/books", methods=["POST"])
def add_book():
    query("INSERT INTO books (title, author, copies) VALUES (%s,%s,%s)",
          (request.form["title"], request.form["author"], int(request.form["copies"])), fetch=False)
    return redirect("/")

@app.route("/readers", methods=["GET", "POST"])
def readers():
    if request.method == "POST":
        query("INSERT INTO readers (name, email) VALUES (%s,%s)",
              (request.form["name"], request.form["email"]), fetch=False)
        return redirect("/readers")
    rows = query("SELECT id, name, email FROM readers ORDER BY id")
    trs = "".join(f"<tr><td>{r[0]}</td><td>{escape(r[1])}</td><td>{escape(r[2])}</td></tr>" for r in rows)
    body = ("<h3>Doc gia</h3><table><tr><th>ID</th><th>Ten</th><th>Email</th></tr>" + trs + "</table>"
            '<form method="post">Ten <input name="name" required> Email '
            '<input name="email" type="email" required> <button>Them doc gia</button></form>')
    return page(body)

@app.route("/loans", methods=["GET", "POST"])
def loans():
    if request.method == "POST":
        query("INSERT INTO loans (book_id, reader_id) VALUES (%s,%s)",
              (int(request.form["book_id"]), int(request.form["reader_id"])), fetch=False)
        return redirect("/loans")
    rows = query("""SELECT l.id, b.title, r.name, l.borrowed_at, l.returned_at
        FROM loans l JOIN books b ON b.id=l.book_id JOIN readers r ON r.id=l.reader_id
        ORDER BY l.id DESC""")
    trs = "".join(
        f"<tr><td>{r[0]}</td><td>{escape(r[1])}</td><td>{escape(r[2])}</td><td>{r[3]}</td><td>"
        + (str(r[4]) if r[4] else f'<form method="post" action="/return/{r[0]}"><button>Tra sach</button></form>')
        + "</td></tr>" for r in rows)
    bopts = "".join(f'<option value="{b[0]}">{escape(b[1])}</option>' for b in query("SELECT id,title FROM books"))
    ropts = "".join(f'<option value="{r[0]}">{escape(r[1])}</option>' for r in query("SELECT id,name FROM readers"))
    body = ("<h3>Muon / Tra sach</h3>"
            f'<form method="post">Sach <select name="book_id">{bopts}</select> '
            f'Doc gia <select name="reader_id">{ropts}</select> <button>Cho muon</button></form>'
            "<table><tr><th>ID</th><th>Sach</th><th>Doc gia</th><th>Ngay muon</th><th>Ngay tra</th></tr>"
            + trs + "</table>")
    return page(body)

@app.route("/return/<int:loan_id>", methods=["POST"])
def return_book(loan_id):
    query("UPDATE loans SET returned_at=CURRENT_DATE WHERE id=%s AND returned_at IS NULL",
          (loan_id,), fetch=False)
    return redirect("/loans")
