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
    <title>Enterprise Library OS - Book Catalog</title>
    <style>
        :root {
            --bg-body: #0f172a;
            --bg-card: #1e293b;
            --border-color: #334155;
            --primary: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #c084fc;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: var(--bg-body); color: var(--text-main); line-height: 1.6; padding-bottom: 60px; min-height: 100vh; }
        .container { max-width: 1280px; margin: 0 auto; padding: 0 24px; }

        /* Top Navigation */
        .navbar { background: rgba(30, 41, 59, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; padding: 16px 0; }
        .nav-wrapper { display: flex; justify-content: space-between; align-items: center; }
        .brand { display: flex; align-items: center; gap: 14px; text-decoration: none; color: var(--text-main); }
        .brand-logo { background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%); width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.35); }
        .brand-text h1 { font-size: 18px; font-weight: 800; background: linear-gradient(to right, #ffffff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .brand-text span { font-size: 11px; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; font-weight: 700; display: block; }

        .nav-links { display: flex; gap: 8px; background: #0f172a; padding: 4px; border-radius: 10px; border: 1px solid var(--border-color); }
        .nav-links a { color: var(--text-muted); text-decoration: none; font-weight: 600; font-size: 13px; padding: 8px 18px; border-radius: 8px; transition: all 0.2s; }
        .nav-links a.active { color: #ffffff; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4); }

        /* Stats Section */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-top: 32px; }
        .stat-card { background: var(--bg-card); border: 1px solid var(--border-color); padding: 24px; border-radius: 16px; display: flex; justify-content: space-between; align-items: center; }
        .stat-info div { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .stat-info h2 { font-size: 32px; font-weight: 800; color: var(--text-main); margin-top: 4px; }
        .stat-icon { width: 54px; height: 54px; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 26px; }
        .stat-icon.blue { background: rgba(56, 189, 248, 0.1); color: var(--primary); border: 1px solid rgba(56, 189, 248, 0.2); }
        .stat-icon.green { background: rgba(52, 211, 153, 0.1); color: var(--accent-green); border: 1px solid rgba(52, 211, 153, 0.2); }
        .stat-icon.purple { background: rgba(192, 132, 252, 0.1); color: var(--accent-purple); border: 1px solid rgba(192, 132, 252, 0.2); }

        /* Card Panels */
        .card { background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 18px; padding: 28px; margin-top: 28px; }
        .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
        .card-title { display: flex; align-items: center; gap: 10px; font-size: 18px; font-weight: 700; color: var(--text-main); }
        .card-title span { color: var(--primary); }

        /* Form Controls */
        .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)) 140px; gap: 16px; align-items: end; }
        .form-group { display: flex; flex-direction: column; gap: 8px; }
        .form-group label { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        input, select { width: 100%; height: 46px; padding: 0 16px; background: #0f172a; border: 1px solid var(--border-color); border-radius: 10px; font-size: 14px; color: var(--text-main); outline: none; }
        input:focus, select:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15); }
        
        .btn { height: 46px; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; border: none; border-radius: 10px; font-weight: 700; font-size: 14px; cursor: pointer; transition: all 0.2s; width: 100%; }
        .btn:hover { background: linear-gradient(135deg, #0369a1 0%, #075985 100%); transform: translateY(-1px); }
        .btn-sm { height: 34px; padding: 0 14px; font-size: 12px; border-radius: 8px; }
        .btn-success { background: linear-gradient(135deg, #059669 0%, #047857 100%); }

        /* Book Grid Layout */
        .books-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 24px; margin-top: 10px; }
        .book-card { background: #0f172a; border: 1px solid var(--border-color); border-radius: 14px; overflow: hidden; transition: all 0.25s; display: flex; flex-direction: column; }
        .book-card:hover { transform: translateY(-5px); border-color: var(--primary); box-shadow: 0 12px 24px -10px rgba(56, 189, 248, 0.3); }
        .book-cover { width: 100%; height: 260px; object-fit: cover; background: #1e293b; border-bottom: 1px solid var(--border-color); }
        .book-details { padding: 16px; display: flex; flex-direction: column; flex-grow: 1; justify-content: space-between; }
        .book-title { font-weight: 700; font-size: 15px; color: #ffffff; margin-bottom: 4px; line-height: 1.3; }
        .book-author { font-size: 13px; color: var(--text-muted); margin-bottom: 12px; }
        .book-meta { display: flex; justify-content: space-between; align-items: center; margin-top: auto; }
        
        /* Badges */
        .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
        .badge-slate { background: rgba(148, 163, 184, 0.1); color: var(--text-muted); border: 1px solid rgba(148, 163, 184, 0.2); }
        .badge-green { background: rgba(52, 211, 153, 0.1); color: var(--accent-green); border: 1px solid rgba(52, 211, 153, 0.2); }

        /* Tables for Readers/Loans */
        .table-responsive { overflow-x: auto; margin-top: 10px; }
        table { width: 100%; border-collapse: separate; border-spacing: 0; }
        th { background: #0f172a; color: var(--text-muted); font-size: 12px; font-weight: 700; text-transform: uppercase; padding: 16px 20px; border-bottom: 1px solid var(--border-color); text-align: left; }
        td { padding: 18px 20px; border-bottom: 1px solid rgba(51, 65, 85, 0.5); font-size: 14px; color: var(--text-main); vertical-align: middle; }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container nav-wrapper">
            <a class="brand" href="/">
                <div class="brand-logo">⚡</div>
                <div class="brand-text">
                    <h1>LIBRARY OS</h1>
                    <span>Enterprise Edition</span>
                </div>
            </a>
            <div class="nav-links">
                <a href="/" class="{{ 'active' if active_page == 'books' else '' }}">📚 Kho Sách</a>
                <a href="/readers" class="{{ 'active' if active_page == 'readers' else '' }}">👥 Độc Giả</a>
                <a href="/loans" class="{{ 'active' if active_page == 'loans' else '' }}">🔄 Mượn / Trả</a>
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
    total_books = query("SELECT COALESCE(SUM(copies), 0) FROM books")[0][0]
    total_readers = query("SELECT COUNT(*) FROM readers")[0][0]
    active_loans = query("SELECT COUNT(*) FROM loans WHERE returned_at IS NULL")[0][0]

    rows = query("""SELECT b.id, b.title, b.author, b.copies,
        b.copies - COUNT(l.id) FILTER (WHERE l.returned_at IS NULL) AS available,
        COALESCE(b.cover_url, 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400')
        FROM books b LEFT JOIN loans l ON l.book_id=b.id
        GROUP BY b.id ORDER BY b.id""")
    
    cards = []
    for r in rows:
        cards.append(f"""
        <div class="book-card">
            <img src="{escape(r[5])}" class="book-cover" alt="Cover" onerror="this.src='https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400'">
            <div class="book-details">
                <div>
                    <div class="book-title">{escape(r[1])}</div>
                    <div class="book-author">✍️ {escape(r[2])}</div>
                </div>
                <div class="book-meta">
                    <span class="badge badge-slate">📦 Tổng: {r[3]}</span>
                    <span class="badge badge-green">✓ Còn: {r[4]}</span>
                </div>
            </div>
        </div>
        """)
    
    books_html = f'<div class="books-grid">{"".join(cards)}</div>' if cards else '<p style="color:var(--text-muted)">Chưa có sách trong kho.</p>'

    stats_html = f"""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-info"><div>Tổng Sách Kho</div><h2>{total_books}</h2></div>
            <div class="stat-icon blue">📚</div>
        </div>
        <div class="stat-card">
            <div class="stat-info"><div>Độc Giả Hệ Thống</div><h2>{total_readers}</h2></div>
            <div class="stat-icon green">👥</div>
        </div>
        <div class="stat-card">
            <div class="stat-info"><div>Phiếu Đang Mượn</div><h2>{active_loans}</h2></div>
            <div class="stat-icon purple">⚡</div>
        </div>
    </div>
    """

    body = f"""
    {stats_html}
    <div class="card">
        <div class="card-header">
            <div class="card-title"><span>➕</span> Khai Báo Sách Mới Kèm Ảnh Bìa</div>
        </div>
        <form method="post" action="/books" class="form-grid">
            <div class="form-group">
                <label>Tên Tiêu Đề Sách</label>
                <input name="title" placeholder="Ví dụ: Thiết kế Hệ thống..." required>
            </div>
            <div class="form-group">
                <label>Tác Giả</label>
                <input name="author" placeholder="Ví dụ: Martin Kleppmann..." required>
            </div>
            <div class="form-group">
                <label>Link Ảnh Bìa (URL)</label>
                <input name="cover_url" placeholder="https://..." value="https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400">
            </div>
            <div class="form-group">
                <label>Số Lượng Kho</label>
                <input name="copies" type="number" value="1" min="1" required>
            </div>
            <button class="btn">+ Thêm Sách</button>
        </form>
    </div>

    <div class="card">
        <div class="card-header">
            <div class="card-title"><span>📖</span> Tủ Sách Trực Quan Thư Viện</div>
        </div>
        {books_html}
    </div>
    """
    return page(body, active_page="books")

@app.route("/books", methods=["POST"])
def add_book():
    cover = request.form.get("cover_url", "").strip() or "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400"
    query("INSERT INTO books (title, author, copies, cover_url) VALUES (%s,%s,%s,%s)",
          (request.form["title"], request.form["author"], int(request.form["copies"]), cover), fetch=False)
    return redirect("/")

@app.route("/readers", methods=["GET", "POST"])
def readers():
    if request.method == "POST":
        query("INSERT INTO readers (name, email) VALUES (%s,%s)",
              (request.form["name"], request.form["email"]), fetch=False)
        return redirect("/readers")
    
    rows = query("SELECT id, name, email FROM readers ORDER BY id")
    trs = "".join(f"<tr><td style='font-weight:800; color:var(--primary);'>#{r[0]:03d}</td>"
                  f"<td style='font-weight:700; color:#ffffff;'>{escape(r[1])}</td>"
                  f"<td style='color:var(--text-muted);'>{escape(r[2])}</td></tr>" for r in rows)
    
    body = f"""
    <div class="card">
        <div class="card-header"><div class="card-title"><span>👤</span> Đăng Ký Độc Giả Mới</div></div>
        <form method="post" class="form-grid" style="grid-template-columns: 1fr 1fr 160px;">
            <div class="form-group"><label>Họ Và Tên</label><input name="name" placeholder="Ví dụ: Nguyễn Văn A..." required></div>
            <div class="form-group"><label>Email Liên Hệ</label><input name="email" type="email" placeholder="example@domain.com..." required></div>
            <button class="btn">+ Tạo Hồ Sơ</button>
        </form>
    </div>
    <div class="card">
        <div class="card-header"><div class="card-title"><span>👥</span> Danh Sách Độc Giả</div></div>
        <div class="table-responsive"><table><thead><tr><th>Mã ID</th><th>Họ Và Tên</th><th>Email</th></tr></thead><tbody>{trs}</tbody></table></div>
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
        f"<tr><td style='font-weight:800; color:var(--primary);'>#{r[0]:03d}</td>"
        f"<td style='font-weight:700; color:#ffffff;'>{escape(r[1])}</td>"
        f"<td>{escape(r[2])}</td><td style='color:var(--text-muted);'>{r[3]}</td><td>"
        + (f"<span class='badge badge-slate'>✓ Đã trả ({r[4]})</span>" if r[4] else f'<form method="post" action="/return/{r[0]}" style="display:inline;"><button class="btn btn-sm btn-success">✓ Xác Nhận Trả Sách</button></form>')
        + "</td></tr>" for r in rows)
    
    bopts = "".join(f'<option value="{b[0]}">{escape(b[1])}</option>' for b in query("SELECT id,title FROM books"))
    ropts = "".join(f'<option value="{r[0]}">{escape(r[1])}</option>' for r in query("SELECT id,name FROM readers"))
    
    body = f"""
    <div class="card">
        <div class="card-header"><div class="card-title"><span>⚡</span> Lập Phiếu Mượn Sách</div></div>
        <form method="post" class="form-grid" style="grid-template-columns: 1fr 1fr 160px;">
            <div class="form-group"><label>Sách Mượn</label><select name="book_id">{bopts}</select></div>
            <div class="form-group"><label>Độc Giả</label><select name="reader_id">{ropts}</select></div>
            <button class="btn">⚡ Cho Mượn</button>
        </form>
    </div>
    <div class="card">
        <div class="card-header"><div class="card-title"><span>📋</span> Lịch Sử Mượn / Trả</div></div>
        <div class="table-responsive"><table><thead><tr><th>Mã Phiếu</th><th>Tên Sách</th><th>Độc Giả</th><th>Ngày Mượn</th><th>Trạng Thái</th></tr></thead><tbody>{trs}</tbody></table></div>
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
