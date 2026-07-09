from datetime import datetime
from flask_login import UserMixin
from extensions import db


def gen_id(prefix, model, id_column):
    """Bikin id gaya PREFIX-YYYYMMDDNNN, konsisten sama dump SQL asli."""
    today_str = datetime.now().strftime('%Y%m%d')
    like_pattern = f"{prefix}-{today_str}%"
    last = (
        db.session.query(model)
        .filter(id_column.like(like_pattern))
        .order_by(id_column.desc())
        .first()
    )
    if last:
        last_id = getattr(last, id_column.key)
        seq = int(last_id[-3:]) + 1
    else:
        seq = 1
    return f"{prefix}-{today_str}{seq:03d}"


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    id_admin = db.Column(db.String(20), primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    nama_lengkap = db.Column(db.String(100))
    akses_level = db.Column(
        db.Enum('admin', 'kepala_admin'), nullable=False, default='admin'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Flask-Login butuh id unik string -> pakai id_admin
    def get_id(self):
        return self.id_admin

    @property
    def is_superadmin(self):
        return self.akses_level == 'kepala_admin'


class Menu(db.Model):
    __tablename__ = 'menu'

    id_menu = db.Column(db.String(20), primary_key=True)
    nama_menu = db.Column(db.String(100), nullable=False)
    deskripsi = db.Column(db.Text)
    harga = db.Column(db.Integer, nullable=False)
    gambar = db.Column(db.String(255))
    kategori = db.Column(db.Enum('makanan', 'minuman'), nullable=False)
    status = db.Column(db.Enum('tersedia', 'tidak tersedia'), default='tersedia')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Pesanan(db.Model):
    __tablename__ = 'pesanan'

    id_pesanan = db.Column(db.String(20), primary_key=True)
    nama_pemesan = db.Column(db.String(100))
    waktu_pesan = db.Column(db.DateTime, default=datetime.utcnow)
    status_pesanan = db.Column(
        db.Enum('pending', 'diproses', 'sudah selesai'),
        nullable=False,
        default='pending',
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    details = db.relationship(
        'DetailPesanan', backref='pesanan', cascade='all, delete-orphan'
    )


class DetailPesanan(db.Model):
    __tablename__ = 'detail_pesanan'

    id_detail_pesanan = db.Column(db.String(20), primary_key=True)
    id_pesanan = db.Column(
        db.String(20), db.ForeignKey('pesanan.id_pesanan', ondelete='CASCADE'), nullable=False
    )
    id_menu = db.Column(
        db.String(20), db.ForeignKey('menu.id_menu', ondelete='CASCADE'), nullable=False
    )
    total_harga = db.Column(db.Numeric(10, 2), nullable=False)
    jumlah_pesanan = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    menu = db.relationship('Menu')
