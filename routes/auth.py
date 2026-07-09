import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from models import Admin

bp = Blueprint('auth', __name__, url_prefix='/admin')


def check_password(plain_password, hashed_password):
    """Hash lama dari phpMyAdmin pakai prefix $2y$ (PHP bcrypt).
    Python bcrypt lib bisa langsung verify hash $2y$ tanpa perlu convert."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard') if current_user.is_superadmin
                         else url_for('admin.status_list'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password(password, admin.password):
            login_user(admin)
            flash(f'Selamat datang, {admin.nama_lengkap or admin.username}!', 'success')
            if admin.is_superadmin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('admin.status_list'))

        flash('Username atau password salah.', 'danger')

    return render_template('admin/login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Berhasil logout.', 'info')
    return redirect(url_for('auth.login'))
