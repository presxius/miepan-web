import os
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
    current_app
)
from flask_login import login_required, current_user
from sqlalchemy import func
from werkzeug.utils import secure_filename

from extensions import db
from models import Menu, Pesanan, DetailPesanan, Admin, gen_id
from routes.decorators import superadmin_required
from routes.auth import hash_password

bp = Blueprint('admin', __name__, url_prefix='/admin')


def allowed_file(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']


def save_menu_image(file_storage):
    if not file_storage or file_storage.filename == '':
        return None
    if not allowed_file(file_storage.filename):
        flash('Format foto tidak didukung (pakai png/jpg/jpeg/webp).', 'danger')
        return None
    ts = int(datetime.utcnow().timestamp())
    safe_name = secure_filename(file_storage.filename)
    filename = f"{ts}_{safe_name}"
    file_storage.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename


# ---------- Dashboard (superadmin only) ----------

@bp.route('/dashboard')
@superadmin_required
def dashboard():
    total_pesanan = Pesanan.query.count()
    total_penjualan = db.session.query(func.sum(DetailPesanan.total_harga)).scalar() or 0
    pesanan_pending = Pesanan.query.filter_by(status_pesanan='pending').count()
    pesanan_diproses = Pesanan.query.filter_by(status_pesanan='diproses').count()
    pesanan_selesai = Pesanan.query.filter_by(status_pesanan='sudah selesai').count()

    menu_terlaris = (
        db.session.query(
            Menu.nama_menu,
            func.sum(DetailPesanan.jumlah_pesanan).label('terjual')
        )
        .join(DetailPesanan, DetailPesanan.id_menu == Menu.id_menu)
        .group_by(Menu.id_menu)
        .order_by(func.sum(DetailPesanan.jumlah_pesanan).desc())
        .limit(5)
        .all()
    )

    return render_template(
        'admin/dashboard.html',
        total_pesanan=total_pesanan,
        total_penjualan=total_penjualan,
        pesanan_pending=pesanan_pending,
        pesanan_diproses=pesanan_diproses,
        pesanan_selesai=pesanan_selesai,
        menu_terlaris=menu_terlaris,
    )


# ---------- CRUD Menu (superadmin only) ----------

@bp.route('/menu')
@superadmin_required
def menu_list():
    menus = Menu.query.order_by(Menu.kategori, Menu.nama_menu).all()
    return render_template('admin/menu_list.html', menus=menus)


@bp.route('/menu/add', methods=['GET', 'POST'])
@superadmin_required
def menu_add():
    if request.method == 'POST':
        nama_menu = request.form.get('nama_menu', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        harga = request.form.get('harga', type=int)
        kategori = request.form.get('kategori')
        status = request.form.get('status', 'tersedia')

        if not nama_menu or harga is None or kategori not in ('makanan', 'minuman'):
            flash('Lengkapi semua field wajib.', 'danger')
            return redirect(url_for('admin.menu_add'))

        gambar = save_menu_image(request.files.get('gambar'))

        id_menu = gen_id('MNU', Menu, Menu.id_menu)
        menu = Menu(
            id_menu=id_menu, nama_menu=nama_menu, deskripsi=deskripsi,
            harga=harga, gambar=gambar, kategori=kategori, status=status,
        )
        db.session.add(menu)
        db.session.commit()
        flash('Menu berhasil ditambah.', 'success')
        return redirect(url_for('admin.menu_list'))

    return render_template('admin/menu_form.html', menu=None)


@bp.route('/menu/edit/<id_menu>', methods=['GET', 'POST'])
@superadmin_required
def menu_edit(id_menu):
    menu = Menu.query.get_or_404(id_menu)

    if request.method == 'POST':
        menu.nama_menu = request.form.get('nama_menu', '').strip()
        menu.deskripsi = request.form.get('deskripsi', '').strip()
        menu.harga = request.form.get('harga', type=int)
        menu.kategori = request.form.get('kategori')
        menu.status = request.form.get('status', 'tersedia')

        new_gambar = save_menu_image(request.files.get('gambar'))
        if new_gambar:
            old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], menu.gambar or '')
            if menu.gambar and os.path.exists(old_path):
                os.remove(old_path)
            menu.gambar = new_gambar

        db.session.commit()
        flash('Menu berhasil diupdate.', 'success')
        return redirect(url_for('admin.menu_list'))

    return render_template('admin/menu_form.html', menu=menu)


@bp.route('/menu/delete/<id_menu>', methods=['POST'])
@superadmin_required
def menu_delete(id_menu):
    """Cuma kepala_admin lolos decorator ini -> admin biasa gabisa hapus menu."""
    menu = Menu.query.get_or_404(id_menu)
    if menu.gambar:
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], menu.gambar)
        if os.path.exists(path):
            os.remove(path)
    db.session.delete(menu)
    db.session.commit()
    flash('Menu berhasil dihapus.', 'success')
    return redirect(url_for('admin.menu_list'))


# ---------- Status Pesanan (admin & superadmin) ----------

@bp.route('/status')
@login_required
def status_list():
    status_filter = request.args.get('status')
    query = Pesanan.query
    if status_filter in ('pending', 'diproses', 'sudah selesai'):
        query = query.filter_by(status_pesanan=status_filter)
    pesanan_semua = query.order_by(Pesanan.waktu_pesan.desc()).all()
    return render_template('admin/orders.html', pesanan_semua=pesanan_semua,
                            status_filter=status_filter)


@bp.route('/status/<id_pesanan>/update', methods=['POST'])
@login_required
def status_update(id_pesanan):
    pesanan = Pesanan.query.get_or_404(id_pesanan)
    status_baru = request.form.get('status_pesanan')
    if status_baru in ('pending', 'diproses', 'sudah selesai'):
        pesanan.status_pesanan = status_baru
        db.session.commit()
        flash('Status pesanan diupdate.', 'success')
    return redirect(url_for('admin.status_list'))


# ---------- Kelola Akun Admin (superadmin only) ----------

@bp.route('/accounts')
@superadmin_required
def account_list():
    accounts = Admin.query.order_by(Admin.created_at.desc()).all()
    return render_template('admin/accounts.html', accounts=accounts)


@bp.route('/accounts/add', methods=['GET', 'POST'])
@superadmin_required
def account_add():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        nama_lengkap = request.form.get('nama_lengkap', '').strip()
        akses_level = request.form.get('akses_level', 'admin')

        if not username or not password:
            flash('Username & password wajib diisi.', 'danger')
            return redirect(url_for('admin.account_add'))

        if Admin.query.filter_by(username=username).first():
            flash('Username sudah dipakai.', 'danger')
            return redirect(url_for('admin.account_add'))

        id_admin = gen_id('ADM', Admin, Admin.id_admin)
        akun = Admin(
            id_admin=id_admin, username=username,
            password=hash_password(password),
            nama_lengkap=nama_lengkap,
            akses_level=akses_level if akses_level in ('admin', 'kepala_admin') else 'admin',
        )
        db.session.add(akun)
        db.session.commit()
        flash('Akun admin berhasil dibuat.', 'success')
        return redirect(url_for('admin.account_list'))

    return render_template('admin/account_form.html', account=None)


@bp.route('/accounts/edit/<id_admin>', methods=['GET', 'POST'])
@superadmin_required
def account_edit(id_admin):
    akun = Admin.query.get_or_404(id_admin)

    if request.method == 'POST':
        akun.nama_lengkap = request.form.get('nama_lengkap', '').strip()
        akun.akses_level = request.form.get('akses_level', akun.akses_level)
        new_password = request.form.get('password', '')
        if new_password:
            akun.password = hash_password(new_password)
        db.session.commit()
        flash('Akun admin berhasil diupdate.', 'success')
        return redirect(url_for('admin.account_list'))

    return render_template('admin/account_form.html', account=akun)


@bp.route('/accounts/delete/<id_admin>', methods=['POST'])
@superadmin_required
def account_delete(id_admin):
    if id_admin == current_user.id_admin:
        flash('Tidak bisa hapus akun sendiri.', 'danger')
        return redirect(url_for('admin.account_list'))
    akun = Admin.query.get_or_404(id_admin)
    db.session.delete(akun)
    db.session.commit()
    flash('Akun admin berhasil dihapus.', 'success')
    return redirect(url_for('admin.account_list'))
