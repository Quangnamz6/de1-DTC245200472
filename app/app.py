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
    <title>Hệ Thống Quản Lý Thư Viện - Smart Library System</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #f1f5f9; color: #0f172a; line-height: 1.5; padding-bottom: 50px; }
        
        /* Navigation */
        .navbar { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 18px 0; color: white; box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.25); border-bottom: 1px solid #334155; }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
        .nav-wrapper { display: flex; justify-content: space-between; align-items: center; }
        .brand { display: flex; align-items: center; gap: 12px; font-size: 20px; font-weight: 700; color: #fff; text-decoration: none; letter-spacing: -0.5px; }
        .brand-icon { background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35); }
        .nav-links { display: flex; gap: 8px; }
        .nav-links a { color: #94a3b8; text-decoration: none; font-weight: 500; font-size: 14px; padding: 8px 16px; border-radius: 8px; transition: all 0.2s ease; }
        .nav-links a:hover, .nav-links a.active { color: #ffffff; background: #334155; }

        /* Stats Dashboard */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-top: 30px; }
        .stat-card { background: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); display: flex; align-items: center; justify-content: space-between; }
        .stat-info div { font-size: 13px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-info h3 { font-size: 28px; font-weight: 700; color: #0f172a; margin-top: 4px; }
        .stat-icon { width: 52px; height: 52px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; }
        .stat-icon.blue { background: #eff6ff; color: #2563eb; }
        .stat-icon.emerald { background: #ecfdf5; color: #059669; }
        .stat-icon.purple { background: #faf5ff; color: #9333ea; }

        /* Form Card */
        .card { background: #ffffff; border-radius: 16px; border: 1px solid #e2e8f0; padding: 28px; margin-top: 24px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03); }
        .card-header { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; color: #0f172a; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #f1f5f9; }
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)) 120px; gap: 16px; align-items: end; }
        .form-group { display: flex; flex-direction: column; gap: 6px; }
        .form-group label { font-size: 13px; font-weight: 600; color: #475569; }
        input, select { width: 100%; height: 44px; padding: 0 14px; border: 1px solid #cbd5e1; border-radius: 10px; font-size: 14px; color: #0f172a; background: #f8fafc; outline: none; transition: all 0.2s; }
        input:focus, select:focus { border-color: #2563eb; background: #ffffff; box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1); }
        .btn { height: 44px; background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%); color: white; border: none; border-radius: 10px; font-weight: 600; font-size: 14px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2); }
        .btn:hover { background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); transform: translateY(-1px); box-shadow: 0 4px 8px rgba(37, 99, 235, 0.3); }
        .btn-sm { height: 32px; padding: 0 12px; font-size: 12px; border-radius: 6px; }
        .btn-success { background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2); }
        .btn-success:hover { background: linear-gradient(135deg, #059669 0%, #047857 100%); }

        /* Tables */
        .table-responsive { overflow-x: auto; margin-top: 8px; }
        table { width: 100%; border-collapse: separate; border-spacing: 0; }
        th { background: #f8fafc; color: #475569; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 14px 18px; border-bottom: 1px solid #e2e8f0; text-align: left; }
        td { padding: 16px 18px; border-bottom: 1px solid #f1f5f9; font-size: 14px; color: #334155; vertical-align: middle; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background-color: #f8fafc; }
        
        /* Badges */
        .badge { display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; }
        .badge-slate { background: #f1f5f9; color: #475569; border: 1px solid #e2e8f0; }
        .badge-emerald { background: #d1fae5; color: #065f46; }
        .badge-amber { background: #fef3c7; color: #92400e; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container nav-wrapper">
            <a class="brand" href="/">
                <div class="brand-icon">📚</div>
                <div>Smart Library System</div>
            </a>
            <div class="nav-links">
                <a href="/" class="{{ 'active' if active_page == 'books' else '' }}">📖 Tủ Sách</a>
                <a href="/readers" class="{{ 'active' if active_page == 'readers' else '' }}">👥 Độc Giả</a>
                <a href="/loans" class="{{ 'active' if active_page == 'loans' else '' }}">🔄 Mượn / Trả Sách</a>
            </div>
        </div>
    </nav>
    <div class="container">
        {{ body|safe }}
    </div>
</body>
</html>"""

def page(body, active_page="books"):
    return render_template_string(PAGE, body=body, active_page=active_page)

@app.route("/health")
def health():
    query("SELECT 1")
    return "ok"

@app.route("/")
def books():
    # Thống kê
    total_books = query("SELECT COALESCE(SUM(copies), 0) FROM books")[0][0]
    total_readers = query("SELECT COUNT(*) FROM readers")[0][0]
    active_loans = query("SELECT COUNT(*) FROM loans WHERE returned_at IS NULL")[0][0]

    rows = query("""SELECT b.id, b.title, b.author, b.copies,
        b.copies - COUNT(l.id) FILTER (WHERE l.returned_at IS NULL) AS available
        FROM books b LEFT JOIN loans l ON l.book_id=b.id
        GROUP BY b.id ORDER BY b.id""")
    
    trs = "".join(f"<tr><td style='font-weight:700; color:#64748b;'>#{r[0]}</td>"
                  f"<td style='font-weight:600; color:#0f172a;'>{escape(r[1])}</td>"
                  f"<td style='color:#64748b;'>{escape(r[2])}</td>"
                  f"<td><span class='badge badge-slate'>{r[3]} cuốn</span></td>"
                  f"<td><span class='badge badge-emerald'>{r[4]} khả dụng</span></td></tr>" for r in rows)
    
    stats_html = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-info"><div>Tổng Sách</div><h3>{total_books}</h3></div>
            <div class="stat-icon blue">📖</div>
        </div>
        <div class="stat-card">
            <div class="stat-info"><div>Độc Giả</div><h3>{total_readers}</h3></div>
            <div class="stat-icon emerald">👥</div>
        </div>
        <div class="stat-card">
            <div class="stat-info"><div>Đang Mượn</div><h3>{active_loans}</h3></div>
            <div class="stat-icon purple">🔄</div>
        </div>
    </div>
    """

    body = f"""
    {stats_html}
    <div class="card">
        <div class="card-header"><span>➕</span> Thêm Sách Mới Vào Thư Viện</div>
        <form method="post" action="/books" class="form-grid">
            <div class="form-group">
                <label>Tên Tiêu Đề Sách</label>
                <input name="title" placeholder="Nhập tiêu đề..." required>
            </div>
            <div class="form-group">
                <label>Tác Giả</label>
                <input name="author" placeholder="Nhập tên tác giả..." required>
            </div>
            <div class="form-group">
                <label>Số Lượng</label>
                <input name="copies" type="number" value="1" min="1" required>
            </div>
            <button class="btn">Thêm Sách</button>
        </form>
    </div>

    <div class="card">
        <div class="card-header"><span>📚</span> Danh Sách Kho Sách</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>Mã Sách</th><th>Tiêu Đề</th><th>Tác Giả</th><th>Tổng Số</th><th>Trạng Thái</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
    return page(body, active_page="books")

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
    trs = "".join(f"<tr><td style='font-weight:700; color:#64748b;'>#{r[0]}</td>"
                  f"<td style='font-weight:600; color:#0f172a;'>{escape(r[1])}</td>"
                  f"<td style='color:#64748b;'>{escape(r[2])}</td></tr>" for r in rows)
    
    body = f"""
    <div class="card">
        <div class="card-header"><span>👤</span> Đăng Ký Độc Giả Mới</div>
        <form method="post" class="form-grid" style="grid-template-columns: 1fr 1fr 140px;">
            <div class="form-group">
                <label>Họ và Tên</label>
                <input name="name" placeholder="Nhập tên độc giả..." required>
            </div>
            <div class="form-group">
                <label>Địa Chỉ Email</label>
                <input name="email" type="email" placeholder="example@domain.com" required>
            </div>
            <button class="btn">Thêm Độc Giả</button>
        </form>
    </div>

    <div class="card">
        <div class="card-header"><span>👥</span> Danh Sách Độc Giả Thư Viện</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>Mã Độc Giả</th><th>Họ Và Tên</th><th>Email Liên Hệ</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
    return page(body, active_page="readers")

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
        f"<tr><td style='font-weight:700; color:#64748b;'>#{r[0]}</td>"
        f"<td style='font-weight:600; color:#0f172a;'>{escape(r[1])}</td>"
        f"<td>{escape(r[2])}</td>"
        f"<td style='color:#64748b;'>{r[3]}</td><td>"
        + (f"<span class='badge badge-slate'>Đã trả ({r[4]})</span>" if r[4] else f'<form method="post" action="/return/{r[0]}" style="display:inline;"><button class="btn btn-sm btn-success">✓ Xạc Nhận Trả Sách</button></form>')
        + "</td></tr>" for r in rows)
    
    bopts = "".join(f'<option value="{b[0]}">{escape(b[1])}</option>' for b in query("SELECT id,title FROM books"))
    ropts = "".join(f'<option value="{r[0]}">{escape(r[1])}</option>' for r in query("SELECT id,name FROM readers"))
    
    body = f"""
    <div class="card">
        <div class="card-header"><span>🔄</span> Tạo Phiếu Mượn Sách</div>
        <form method="post" class="form-grid" style="grid-template-columns: 1fr 1fr 140px;">
            <div class="form-group">
                <label>Chọn Tên Sách</label>
                <select name="book_id">{bopts}</select>
            </div>
            <div class="form-group">
                <label>Chọn Độc Giả Mượn</label>
                <select name="reader_id">{ropts}</select>
            </div>
            <button class="btn">Cho Mượn Sách</button>
        </form>
    </div>

    <div class="card">
        <div class="card-header"><span>📋</span> Nhật Ký Mượn / Trả Sách</div>
        <div class="table-responsive">
            <table>
                <thead>
                    <tr><th>Mã Phiếu</th><th>Tên Sách</th><th>Người Mượn</th><th>Ngày Mượn</th><th>Hành Động / Trạng Thái</th></tr>
                </thead>
                <tbody>{trs}</tbody>
            </table>
        </div>
    </div>
    """
    return page(body, active_page="loans")

@app.route("/return/<int:loan_id>", methods=["POST"])
def return_book(loan_id):
    query("UPDATE loans SET returned_at=CURRENT_DATE WHERE id=%s AND returned_at IS NULL",
          (loan_id,), fetch=False)
    return redirect("/loans")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
