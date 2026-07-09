from functools import wraps
from flask import abort
from flask_login import current_user, login_required


def superadmin_required(f):
    """Cuma kepala_admin lolos. Admin biasa kena 403."""
    @wraps(f)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_superadmin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper
