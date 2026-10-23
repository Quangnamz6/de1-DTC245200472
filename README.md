# De 1 - He thong Quan ly Thu vien

Sinh vien: Ta Quang Nam - MSV DTC245200472

## Thanh phan
- Ung dung web quan ly thu vien (Flask)
- PostgreSQL + pgAdmin
- Nginx reverse proxy (HTTPS tu ky + security headers)
- Chay bang Docker Compose

## Chay he thong
1. cp .env.example .env (dat mat khau manh)
2. Tao chung chi tu ky vao nginx/certs/
3. docker compose up -d --build
4. Website: https://<IP> | pgAdmin: https://<IP>:8443
