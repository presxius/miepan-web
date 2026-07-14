from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from extensions import db
from models import Menu, Pesanan, DetailPesanan, gen_id
from routes.decorators import superadmin_required

bp = Blueprint('api', __name__, url_prefix='/api')


# ---------- Helper: serialize model jadi dict ----------

def menu_to_dict(menu):
    return {
        'id_menu': menu.id_menu,
        'nama_menu': menu.nama_menu,
        'deskripsi': menu.deskripsi,
        'harga': menu.harga,
        'gambar': menu.gambar,
        'kategori': menu.kategori,
        'status': menu.status,
    }


def pesanan_to_dict(pesanan):
    return {
        'id_pesanan': pesanan.id_pesanan,
        'nama_pemesan': pesanan.nama_pemesan,
        'waktu_pesan': pesanan.waktu_pesan.isoformat(),
        'status_pesanan': pesanan.status_pesanan,
        'items': [
            {
                'id_menu': d.id_menu,
                'nama_menu': d.menu.nama_menu,
                'jumlah': d.jumlah_pesanan,
                'subtotal': float(d.total_harga),
            }
            for d in pesanan.details
        ],
        'total': float(sum(d.total_harga for d in pesanan.details)),
    }


# ---------- Public: Menu ----------

@bp.route('/menu', methods=['GET'])
def api_menu_list():
    """Daftar menu. Optional: ?kategori=makanan / ?kategori=minuman"""
    kategori = request.args.get('kategori')
    query = Menu.query.filter_by(status='tersedia')
    if kategori in ('makanan', 'minuman'):
        query = query.filter_by(kategori=kategori)
    menus = query.order_by(Menu.kategori, Menu.nama_menu).all()
    return jsonify([menu_to_dict(m) for m in menus])


@bp.route('/menu/<id_menu>', methods=['GET'])
def api_menu_detail(id_menu):
    menu = Menu.query.get(id_menu)
    if not menu:
        return jsonify({'error': 'Menu tidak ditemukan'}), 404
    return jsonify(menu_to_dict(menu))


# ---------- Public: Checkout & Status ----------

@bp.route('/checkout', methods=['POST'])
def api_checkout():
    """
    Body JSON:
    {
        "nama_pemesan": "Radit",
        "items": [{"id_menu": "MNU-xxx", "jumlah": 2}, ...]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Body JSON gak valid'}), 400

    nama_pemesan = (data.get('nama_pemesan') or '').strip()
    items = data.get('items') or []

    if not nama_pemesan:
        return jsonify({'error': 'nama_pemesan wajib diisi'}), 400
    if not items:
        return jsonify({'error': 'items gak boleh kosong'}), 400

    # Validasi semua menu ada & tersedia SEBELUM nulis apa-apa ke DB
    validated = []
    for item in items:
        id_menu = item.get('id_menu')
        jumlah = item.get('jumlah')
        if not id_menu or not isinstance(jumlah, int) or jumlah <= 0:
            return jsonify({'error': f'item gak valid: {item}'}), 400

        menu = Menu.query.get(id_menu)
        if not menu or menu.status != 'tersedia':
            return jsonify({'error': f'Menu {id_menu} gak tersedia'}), 400

        validated.append((menu, jumlah))

    id_pesanan = gen_id('PSN', Pesanan, Pesanan.id_pesanan)
    pesanan = Pesanan(id_pesanan=id_pesanan, nama_pemesan=nama_pemesan, status_pesanan='pending')
    db.session.add(pesanan)
    db.session.flush()

    for menu, jumlah in validated:
        id_detail = gen_id('DTL', DetailPesanan, DetailPesanan.id_detail_pesanan)
        db.session.add(DetailPesanan(
            id_detail_pesanan=id_detail, id_pesanan=id_pesanan, id_menu=menu.id_menu,
            total_harga=menu.harga * jumlah, jumlah_pesanan=jumlah,
        ))

    db.session.commit()
    return jsonify(pesanan_to_dict(pesanan)), 201


@bp.route('/status/<id_pesanan>', methods=['GET'])
def api_status(id_pesanan):
    pesanan = Pesanan.query.get(id_pesanan)
    if not pesanan:
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404
    return jsonify(pesanan_to_dict(pesanan))


# ---------- Protected: Admin (butuh login session, sama kayak halaman admin biasa) ----------

@bp.route('/admin/pesanan', methods=['GET'])
@login_required
def api_admin_pesanan_list():
    """Admin & superadmin boleh liat semua pesanan. Optional: ?status=pending"""
    status_filter = request.args.get('status')
    query = Pesanan.query
    if status_filter in ('pending', 'diproses', 'sudah selesai'):
        query = query.filter_by(status_pesanan=status_filter)
    pesanan_semua = query.order_by(Pesanan.waktu_pesan.desc()).all()
    return jsonify([pesanan_to_dict(p) for p in pesanan_semua])


@bp.route('/admin/pesanan/<id_pesanan>/status', methods=['PATCH'])
@login_required
def api_admin_update_status(id_pesanan):
    """Body JSON: {"status_pesanan": "diproses"}"""
    pesanan = Pesanan.query.get(id_pesanan)
    if not pesanan:
        return jsonify({'error': 'Pesanan tidak ditemukan'}), 404

    data = request.get_json(silent=True) or {}
    status_baru = data.get('status_pesanan')
    if status_baru not in ('pending', 'diproses', 'sudah selesai'):
        return jsonify({'error': 'status_pesanan gak valid'}), 400

    pesanan.status_pesanan = status_baru
    db.session.commit()
    return jsonify(pesanan_to_dict(pesanan))


@bp.route('/admin/menu', methods=['POST'])
@superadmin_required
def api_admin_menu_create():
    """
    Body JSON:
    {"nama_menu": "...", "deskripsi": "...", "harga": 15000, "kategori": "makanan", "status": "tersedia"}
    Catatan: upload foto tetep lewat halaman admin biasa (butuh multipart/form-data, bukan JSON).
    """
    data = request.get_json(silent=True) or {}
    nama_menu = (data.get('nama_menu') or '').strip()
    harga = data.get('harga')
    kategori = data.get('kategori')

    if not nama_menu or not isinstance(harga, int) or kategori not in ('makanan', 'minuman'):
        return jsonify({'error': 'nama_menu, harga (angka), dan kategori wajib diisi bener'}), 400

    id_menu = gen_id('MNU', Menu, Menu.id_menu)
    menu = Menu(
        id_menu=id_menu, nama_menu=nama_menu, deskripsi=data.get('deskripsi', ''),
        harga=harga, kategori=kategori, status=data.get('status', 'tersedia'),
    )
    db.session.add(menu)
    db.session.commit()
    return jsonify(menu_to_dict(menu)), 201


@bp.route('/admin/menu/<id_menu>', methods=['PUT'])
@superadmin_required
def api_admin_menu_update(id_menu):
    menu = Menu.query.get(id_menu)
    if not menu:
        return jsonify({'error': 'Menu tidak ditemukan'}), 404

    data = request.get_json(silent=True) or {}
    if 'nama_menu' in data:
        menu.nama_menu = data['nama_menu']
    if 'deskripsi' in data:
        menu.deskripsi = data['deskripsi']
    if 'harga' in data:
        menu.harga = data['harga']
    if 'kategori' in data and data['kategori'] in ('makanan', 'minuman'):
        menu.kategori = data['kategori']
    if 'status' in data and data['status'] in ('tersedia', 'tidak tersedia'):
        menu.status = data['status']

    db.session.commit()
    return jsonify(menu_to_dict(menu))


@bp.route('/admin/menu/<id_menu>', methods=['DELETE'])
@superadmin_required
def api_admin_menu_delete(id_menu):
    """Sama kayak versi HTML: cuma superadmin yang bisa hapus, admin biasa kena 403."""
    menu = Menu.query.get(id_menu)
    if not menu:
        return jsonify({'error': 'Menu tidak ditemukan'}), 404
    db.session.delete(menu)
    db.session.commit()
    return jsonify({'message': 'Menu berhasil dihapus'})
