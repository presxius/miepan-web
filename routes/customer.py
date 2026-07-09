from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort

from extensions import db
from models import Menu, Pesanan, DetailPesanan, gen_id

bp = Blueprint('customer', __name__)


def get_cart():
    return session.setdefault('cart', {})  # {id_menu: qty}


@bp.route('/')
@bp.route('/menu')
def menu_list():
    """Landing page pas customer scan QR."""
    kategori = request.args.get('kategori')
    query = Menu.query.filter_by(status='tersedia')
    if kategori in ('makanan', 'minuman'):
        query = query.filter_by(kategori=kategori)
    menus = query.order_by(Menu.kategori, Menu.nama_menu).all()
    cart = get_cart()
    cart_count = sum(cart.values())
    return render_template('customer/menu.html', menus=menus, cart_count=cart_count,
                            kategori_aktif=kategori)


@bp.route('/cart/add/<id_menu>', methods=['POST'])
def cart_add(id_menu):
    menu = Menu.query.get_or_404(id_menu)
    if menu.status != 'tersedia':
        flash('Menu sedang tidak tersedia.', 'warning')
        return redirect(url_for('customer.menu_list'))

    cart = get_cart()
    cart[id_menu] = cart.get(id_menu, 0) + 1
    session.modified = True
    flash(f'{menu.nama_menu} ditambah ke keranjang.', 'success')
    return redirect(request.referrer or url_for('customer.menu_list'))


@bp.route('/cart')
def cart_view():
    cart = get_cart()
    items = []
    total = 0
    for id_menu, qty in cart.items():
        menu = Menu.query.get(id_menu)
        if not menu:
            continue
        subtotal = menu.harga * qty
        total += subtotal
        items.append({'menu': menu, 'qty': qty, 'subtotal': subtotal})
    return render_template('customer/cart.html', items=items, total=total)


@bp.route('/cart/update/<id_menu>', methods=['POST'])
def cart_update(id_menu):
    cart = get_cart()
    qty = request.form.get('qty', type=int)
    if qty is None or qty <= 0:
        cart.pop(id_menu, None)
    else:
        cart[id_menu] = qty
    session.modified = True
    return redirect(url_for('customer.cart_view'))


@bp.route('/cart/remove/<id_menu>', methods=['POST'])
def cart_remove(id_menu):
    cart = get_cart()
    cart.pop(id_menu, None)
    session.modified = True
    return redirect(url_for('customer.cart_view'))


@bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = get_cart()
    if not cart:
        flash('Keranjang masih kosong.', 'warning')
        return redirect(url_for('customer.menu_list'))

    if request.method == 'POST':
        nama_pemesan = request.form.get('nama_pemesan', '').strip()
        if not nama_pemesan:
            flash('Nama pemesan wajib diisi.', 'danger')
            return redirect(url_for('customer.checkout'))

        id_pesanan = gen_id('PSN', Pesanan, Pesanan.id_pesanan)
        pesanan = Pesanan(id_pesanan=id_pesanan, nama_pemesan=nama_pemesan,
                           status_pesanan='pending')
        db.session.add(pesanan)
        db.session.flush()  # supaya id_pesanan kepakai FK sebelum commit

        for id_menu, qty in cart.items():
            menu = Menu.query.get(id_menu)
            if not menu:
                continue
            id_detail = gen_id('DTL', DetailPesanan, DetailPesanan.id_detail_pesanan)
            detail = DetailPesanan(
                id_detail_pesanan=id_detail,
                id_pesanan=id_pesanan,
                id_menu=id_menu,
                total_harga=menu.harga * qty,
                jumlah_pesanan=qty,
            )
            db.session.add(detail)

        db.session.commit()
        session['cart'] = {}

        history = session.get('order_history', [])
        history.insert(0, id_pesanan)  # terbaru di paling depan
        session['order_history'] = history[:20]  # batasi 20 biar session gak membengkak
        session.modified = True

        return redirect(url_for('customer.status_page', id_pesanan=id_pesanan))

    items = []
    total = 0
    for id_menu, qty in cart.items():
        menu = Menu.query.get(id_menu)
        if not menu:
            continue
        subtotal = menu.harga * qty
        total += subtotal
        items.append({'menu': menu, 'qty': qty, 'subtotal': subtotal})
    return render_template('customer/checkout.html', items=items, total=total)


@bp.route('/status/<id_pesanan>')
def status_page(id_pesanan):
    pesanan = Pesanan.query.get_or_404(id_pesanan)
    return render_template('customer/status.html', pesanan=pesanan)


@bp.route('/cek-status')
def cek_status():
    """Tampilin history pesanan dari session browser customer, terbaru di atas."""
    order_ids = session.get('order_history', [])
    pesanan_list = []
    for id_pesanan in order_ids:
        pesanan = Pesanan.query.get(id_pesanan)
        if pesanan:
            pesanan_list.append(pesanan)

    return render_template('customer/cek_status.html', pesanan_list=pesanan_list)
