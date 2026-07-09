# Miepan Bangladesh - Web Pemesanan Menu

Flask + MySQL (MariaDB) + Bootstrap-free CSS custom.

## Setup Ubuntu Server 24.04 LTS

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip mariadb-server libmariadb-dev pkg-config

sudo mysql_secure_installation
sudo mysql -u root -p
```

Di prompt MySQL:
```sql
CREATE DATABASE miepan_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
CREATE USER 'miepan'@'localhost' IDENTIFIED BY 'password_kuat_disini';
GRANT ALL PRIVILEGES ON miepan_db.* TO 'miepan'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Import dump asli:
```bash
mysql -u miepan -p miepan_db < miepan_db.sql
```

## Setup Python

```bash
cd miepan_web
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # isi DB_USER=miepan, DB_PASSWORD=..., SECRET_KEY=random string
```

Password admin di dump asli hash bcrypt `$2y$` (dari PHP). Kode Python (`routes/auth.py`)
pakai lib `bcrypt` yang baca hash `$2y$` langsung, jadi akun `ezra`/`jaewo` lama tetap bisa
dipakai asal kamu tahu password plaintext aslinya. Kalau lupa, buat akun baru lewat
`flask shell` (lihat bawah) atau reset lewat query manual.

## Jalankan (dev)

```bash
python app.py
# atau
flask --app app:create_app run --host=0.0.0.0 --port=5000 --debug
```

Buka `http://<ip-server>:5000/` — ini halaman yang di-scan lewat QR customer.

## Bikin akun superadmin baru (kalau perlu, via shell)

```bash
flask --app app:create_app shell
```
```python
from extensions import db
from models import Admin, gen_id
from routes.auth import hash_password

id_admin = gen_id('ADM', Admin, Admin.id_admin)
akun = Admin(id_admin=id_admin, username='superadmin', password=hash_password('passwordbaru'),
             nama_lengkap='Super Admin', akses_level='kepala_admin')
db.session.add(akun)
db.session.commit()
```

## QR Code buat customer

QR tinggal generate dari URL `http://<ip-server-atau-domain>:5000/` pakai tool apapun
(qrencode CLI, situs qr generator, dll), print, taruh di meja. Scan -> langsung ke halaman menu.

```bash
sudo apt install -y qrencode
qrencode -o qr_menu.png "http://ip-server:5000/"
```

## Deploy production (opsional, singkat)

Pakai gunicorn + nginx reverse proxy + systemd service kalau mau jalan permanen:

```bash
pip install gunicorn
gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app()"
```

Lalu nginx proxy_pass ke `127.0.0.1:8000`, dan bikin systemd unit biar auto-start pas reboot.

## Struktur akses role

| Fitur                     | Admin | Superadmin |
|---------------------------|:-----:|:----------:|
| Login                     | ya    | ya         |
| Halaman status pesanan    | ya    | ya         |
| Update status pesanan     | ya    | ya         |
| Dashboard penjualan       | -     | ya         |
| CRUD menu (tambah/edit)   | -     | ya         |
| Hapus menu                | -     | ya         |
| Kelola akun admin         | -     | ya         |

Admin biasa yang coba akses `/admin/menu`, `/admin/dashboard`, `/admin/accounts` langsung
kena 403 (lihat `routes/decorators.py` -> `superadmin_required`).
