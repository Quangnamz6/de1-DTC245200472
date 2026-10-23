CREATE TABLE books (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  author VARCHAR(120) NOT NULL,
  copies INT NOT NULL DEFAULT 1 CHECK (copies >= 0)
);
CREATE TABLE readers (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(120) UNIQUE NOT NULL
);
CREATE TABLE loans (
  id SERIAL PRIMARY KEY,
  book_id INT REFERENCES books(id),
  reader_id INT REFERENCES readers(id),
  borrowed_at DATE NOT NULL DEFAULT CURRENT_DATE,
  returned_at DATE
);
INSERT INTO books (title, author, copies) VALUES
 ('Lap trinh Python', 'Nguyen Van A', 3),
 ('Co so du lieu', 'Tran Thi B', 2),
 ('Mang may tinh', 'Le Van C', 2);
INSERT INTO readers (name, email) VALUES
 ('Ta Quang Nam', 'dtc245200473@ictu.edu.vn'),
 ('Nguyen Thi D', 'd@example.com');
