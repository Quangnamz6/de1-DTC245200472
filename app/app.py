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

PAGE = """<!doctype html>
<html lang="vi">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hệ thống Quản lý Thư viện</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <style>
        body { background-color: #f8f9fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { border-radius: 10px; border: none; }
        .table thead { background-color: #0d6efd; color: white; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/"><i class="bi bi-journal-bookmark-fill me-2"></i>Hệ thống Quản lý Thư viện</a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link fw-semibold text-white me-3" href="/"><i class="bi bi-book me-1"></i>Sách</a>
                <a class="nav-link fw-semibold text-white me-3" href="/readers"><i class="bi bi-people me-1"></i>Độc giả</a>
                <a class="nav-link fw-semibold text-white" href="/loans"><i class="bi bi-arrow-left-right me-1"></i>Mượn/Trả</a>
            </div>
        </div>
    </nav>
    <div class="container">
        {{ body|safe }}
    </div>
</body>
</html>"""

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
    
    trs = "".join(f"<tr><td class='fw-bold'>{r[0]}</td><td class='text-start fw-semibold'>{escape(r[1])}</td>"
                  f"<td class='text-start text-muted'>{escape(r[2])}</td>"
                  f"<td><span class='badge bg-secondary fs-6'>{r[3]}</span></td>"
                  f"<td><span class='badge bg-success fs-6'>{r[4]}</span></td></tr>" for r in rows)
    
    body = f"""
    <div class="card shadow-sm p-4 mb-4">
        <h5 class="card-title text-primary mb-3"><i class="bi bi-plus-circle me-2"></i>Thêm Sách Mới</h5>
        <form method="post" action="/books" class="row g-3 align-items-center">
            <div class="col-md-5">
                <input name="title" class="form-control" placeholder="Tiêu đề sách..." required>
            </div>
            <div class="col-md-4">
                <input name="author" class="form-control" placeholder="Tác giả..." required>
            </div>
            <div class="col-md-1">
                <input name="copies" type="number" class="form-control" value="1" min="1" required>
            </div>
            <div class="col-md-2">
                <button class="btn btn-primary w-100 fw-bold"><i class="bi bi-save me-1"></i>Thêm sách</button>
            </div>
        </form>
    </div>

    <div class="card shadow-sm p-4">
        <h5 class="card-title text-dark mb-3"><i class="bi bi-list-stars me-2"></i>Danh sách sách</h5>
        <div class="table-responsive">
            <table class="table table-hover table-striped align-middle text-center mb-0">
                <thead class="table-primary">
                    <tr><th>ID</th><th class="text-start">Tiêu đề</th><th class="text-start">Tác giả</th><th>Tổng</th><th>Còn lại</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
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
    trs = "".join(f"<tr><td class='fw-bold'>{r[0]}</td><td class='text-start fw-semibold'>{escape(r[1])}</td>"
                  f"<td class='text-start text-muted'>{escape(r[2])}</td></tr>" for r in rows)
    
    body = f"""
    <div class="card shadow-sm p-4 mb-4">
        <h5 class="card-title text-primary mb-3"><i class="bi bi-person-plus me-2"></i>Thêm Độc Giả</h5>
        <form method="post" class="row g-3 align-items-center">
            <div class="col-md-5">
                <input name="name" class="form-control" placeholder="Tên độc giả..." required>
            </div>
            <div class="col-md-5">
                <input name="email" type="email" class="form-control" placeholder="Email..." required>
            </div>
            <div class="col-md-2">
                <button class="btn btn-primary w-100 fw-bold"><i class="bi bi-person-check me-1"></i>Thêm độc giả</button>
            </div>
        </form>
    </div>

    <div class="card shadow-sm p-4">
        <h5 class="card-title text-dark mb-3"><i class="bi bi-people me-2"></i>Danh sách Độc giả</h5>
        <div class="table-responsive">
            <table class="table table-hover table-striped align-middle text-center mb-0">
                <thead class="table-primary">
                    <tr><th>ID</th><th class="text-start">Tên</th><th class="text-start">Email</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
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
        f"<tr><td class='fw-bold'>{r[0]}</td><td class='text-start fw-semibold'>{escape(r[1])}</td>"
        f"<td class='text-start'>{escape(r[2])}</td><td>{r[3]}</td><td>"
        + (f"<span class='badge bg-secondary'>{r[4]}</span>" if r[4] else f'<form method="post" action="/return/{r[0]}" class="d-inline"><button class="btn btn-sm btn-outline-success fw-bold"><i class="bi bi-check-circle me-1"></i>Trả sách</button></form>')
        + "</td></tr>" for r in rows)
    
    bopts = "".join(f'<option value="{b[0]}">{escape(b[1])}</option>' for b in query("SELECT id,title FROM books"))
    ropts = "".join(f'<option value="{r[0]}">{escape(r[1])}</option>' for r in query("SELECT id,name FROM readers"))
    
    body = f"""
    <div class="card shadow-sm p-4 mb-4">
        <h5 class="card-title text-primary mb-3"><i class="bi bi-arrow-left-right me-2"></i>Cho Mượn Sách</h5>
        <form method="post" class="row g-3 align-items-center">
            <div class="col-md-5">
                <select name="book_id" class="form-select">{bopts}</select>
            </div>
            <div class="col-md-5">
                <select name="reader_id" class="form-select">{ropts}</select>
            </div>
            <div class="col-md-2">
                <button class="btn btn-primary w-100 fw-bold"><i class="bi bi-journal-plus me-1"></i>Cho mượn</button>
            </div>
        </form>
    </div>

    <div class="card shadow-sm p-4">
        <h5 class="card-title text-dark mb-3"><i class="bi bi-clock-history me-2"></i>Lịch sử Mượn / Trả</h5>
        <div class="table-responsive">
            <table class="table table-hover table-striped align-middle text-center mb-0">
                <thead class="table-primary">
                    <tr><th>ID</th><th class="text-start">Sách</th><th class="text-start">Độc giả</th><th>Ngày mượn</th><th>Trạng thái / Ngày trả</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
    return page(body)

@app.route("/return/<int:loan_id>", methods=["POST"])
def return_book(loan_id):
    query("UPDATE loans SET returned_at=CURRENT_DATE WHERE id=%s AND returned_at IS NULL",
          (loan_id,), fetch=False)
    return redirect("/loans")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
