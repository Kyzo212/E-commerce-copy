import os
import uuid
import json
from decimal import Decimal, InvalidOperation

from jinja2 import Environment, FileSystemLoader
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.exceptions import NotFound
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash

from database import SessionLocal
from models import Product, User, Order, OrderItem, SellerProfile
from sqlalchemy.orm import joinedload

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def _save_upload(file_storage):
    """Save an uploaded file; return the URL path or None."""
    if not file_storage or not file_storage.filename:
        return None
    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_EXT:
        return None
    filename = uuid.uuid4().hex + ext
    file_storage.save(os.path.join(UPLOAD_DIR, filename))
    return f"/static/uploads/{filename}"

jinja_env = Environment(loader=FileSystemLoader(os.path.join(BASE_DIR, "templates")))


def _price(value):
    try:
        return f"{float(value):.2f}"
    except Exception:
        return "0.00"


jinja_env.filters["price"] = _price

url_map = Map([
    Rule("/",                          endpoint="home"),
    Rule("/login/",                    endpoint="login",          methods=["GET", "POST"]),
    Rule("/register/",                 endpoint="register",       methods=["GET", "POST"]),
    Rule("/logout/",                   endpoint="logout",         methods=["POST"]),
    Rule("/profile/",                  endpoint="profile",        methods=["GET", "POST"]),
    Rule("/profile/password/",         endpoint="profile_password", methods=["POST"]),
    Rule("/products/",                 endpoint="product_list",   methods=["GET"]),
    Rule("/products/create/",          endpoint="product_create", methods=["GET", "POST"]),
    Rule("/products/<int:id>/",        endpoint="product_detail", methods=["GET"]),
    Rule("/products/<int:id>/edit/",   endpoint="product_edit",   methods=["GET", "POST"]),
    Rule("/products/<int:id>/delete/", endpoint="product_delete", methods=["POST"]),
    Rule("/cart/",                     endpoint="cart_view",      methods=["GET"]),
    Rule("/cart/add/",                 endpoint="cart_add",       methods=["POST"]),
    Rule("/cart/update/",              endpoint="cart_update",    methods=["POST"]),
    Rule("/cart/remove/",              endpoint="cart_remove",    methods=["POST"]),
    Rule("/checkout/",                 endpoint="checkout",       methods=["GET", "POST"]),
    Rule("/orders/",                   endpoint="order_list",     methods=["GET"]),
    Rule("/orders/<int:id>/",          endpoint="order_detail",   methods=["GET"]),
    Rule("/admin/",                    endpoint="admin_dashboard", methods=["GET"]),
    Rule("/admin/orders/",             endpoint="admin_orders",   methods=["GET"]),
    Rule("/admin/orders/<int:id>/",    endpoint="admin_order_detail", methods=["GET"]),
    Rule("/admin/orders/<int:id>/status/", endpoint="admin_order_status", methods=["POST"]),
    Rule("/admin/users/",              endpoint="admin_users",    methods=["GET"]),
    Rule("/admin/users/<int:id>/toggle/", endpoint="admin_user_toggle", methods=["POST"]),
    Rule("/admin/users/<int:id>/approve-seller/", endpoint="admin_user_approve_seller", methods=["POST"]),
    Rule("/seller/listings/",          endpoint="seller_listings", methods=["GET"]),
])


# ── Session helpers ───────────────────────────────────────────────────────────

def _get_current_user(request):
    """Return the logged-in User object or None."""
    try:
        uid = int(json.loads(request.cookies.get("session", "{}")).get("uid", 0))
    except Exception:
        return None
    if not uid:
        return None
    db = SessionLocal()
    try:
        user = db.get(User, uid)
        if user and not user.is_active:
            return None
        return user
    finally:
        db.close()


def _set_session(response, user_id):
    response.set_cookie("session", json.dumps({"uid": user_id}),
                        max_age=86400 * 30, httponly=True, samesite="Lax")
    return response


def _require_admin(request):
    """Return None if user is admin, else return a redirect/403 response."""
    user = _get_current_user(request)
    if not user:
        return redirect("/login/")
    if not user.is_admin:
        return render("403.html", {}, status=403, request=request)
    return None


def _require_seller(request):
    """Return None if user is a seller/admin, else return a redirect/403 response."""
    user = _get_current_user(request)
    if not user:
        return redirect("/login/")
    if not user.is_seller:
        return render("403.html", {}, status=403, request=request)
    return None


def _clear_session(response):
    response.delete_cookie("session")
    return response


# ── Cart helpers ──────────────────────────────────────────────────────────────

def _get_cart(request):
    try:
        raw = json.loads(request.cookies.get("cart", "{}"))
        return {str(k): int(v) for k, v in raw.items() if int(v) > 0}
    except Exception:
        return {}


def _cart_count(request):
    return sum(_get_cart(request).values())


def _cart_items(request):
    cart = _get_cart(request)
    if not cart:
        return [], Decimal("0")
    db = SessionLocal()
    try:
        items, total = [], Decimal("0")
        for pid, qty in cart.items():
            product = db.get(Product, int(pid))
            if product:
                subtotal = Decimal(str(product.product_price)) * qty
                items.append({"product": product, "quantity": qty, "subtotal": subtotal})
                total += subtotal
        return items, total
    finally:
        db.close()


def _set_cart(response, cart):
    response.set_cookie("cart", json.dumps(cart), max_age=86400 * 7)
    return response


# ── Render helper ─────────────────────────────────────────────────────────────

def render(template_name, ctx=None, status=200, request=None):
    ctx = ctx or {}
    if request is not None:
        ctx.setdefault("cart_count", _cart_count(request))
        ctx.setdefault("current_user", _get_current_user(request))
    html = jinja_env.get_template(template_name).render(ctx)
    return Response(html, status=status, content_type="text/html; charset=utf-8")


# ── Views ─────────────────────────────────────────────────────────────────────

def login(request):
    if _get_current_user(request):
        return redirect("/")
    errors = []
    form = {}
    if request.method == "GET":
        if request.args.get("need_login") == "1":
            errors.append("Please sign in first to continue checkout.")
    if request.method == "POST":
        form = request.form
        email    = form.get("email", "").strip().lower()
        password = form.get("password", "")
        if not email or not password:
            errors.append("Email and password are required.")
        else:
            db = SessionLocal()
            try:
                user = db.query(User).filter_by(email=email).first()
            finally:
                db.close()
            if user and user.is_active and check_password_hash(user.password, password):
                resp = redirect(request.args.get("next") or "/")
                return _set_session(resp, user.user_id)
            if user and not user.is_active:
                errors.append("Your account has been deactivated.")
            else:
                errors.append("Invalid email or password.")
    return render("auth/login.html", {"errors": errors, "form": form}, request=request)


def register(request):
    if _get_current_user(request):
        return redirect("/")
    errors = []
    form = {}
    if request.method == "POST":
        form = request.form
        username = form.get("username", "").strip()
        email    = form.get("email", "").strip().lower()
        password = form.get("password", "")
        confirm  = form.get("confirm", "")
        wants_seller = form.get("want_seller") == "on"
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if not errors:
            db = SessionLocal()
            try:
                if db.query(User).filter_by(email=email).first():
                    errors.append("An account with that email already exists.")
                elif db.query(User).filter_by(username=username).first():
                    errors.append("That username is already taken.")
                else:
                    user = User(
                        username      = username,
                        email         = email,
                        password      = generate_password_hash(password),
                        seller_status = "pending" if wants_seller else "none",
                    )
                    db.add(user)
                    db.flush()
                    if wants_seller:
                        db.add(SellerProfile(user_id=user.user_id))
                    db.commit()
                    uid = user.user_id
                    resp = redirect("/")
                    return _set_session(resp, uid)
            except Exception:
                db.rollback()
                errors.append("Could not create account — please try again.")
            finally:
                db.close()
    return render("auth/register.html", {"errors": errors, "form": form}, request=request)


def logout(request):
    resp = redirect("/")
    return _clear_session(resp)


def profile(request):
    user = _get_current_user(request)
    if not user:
        return redirect("/login/?next=/profile/")

    info_errors, info_success = [], False
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email    = request.form.get("email", "").strip().lower()
        if not username:
            info_errors.append("Username is required.")
        if not email:
            info_errors.append("Email is required.")
        if not info_errors:
            db = SessionLocal()
            try:
                clash_u = db.query(User).filter(
                    User.username == username, User.user_id != user.user_id).first()
                clash_e = db.query(User).filter(
                    User.email == email, User.user_id != user.user_id).first()
                if clash_u:
                    info_errors.append("That username is already taken.")
                elif clash_e:
                    info_errors.append("That email is already in use.")
                else:
                    u = db.get(User, user.user_id)
                    u.username = username
                    u.email    = email
                    db.commit()
                    info_success = True
            except Exception:
                db.rollback()
                info_errors.append("Could not update profile — please try again.")
            finally:
                db.close()
            user = _get_current_user(request)   # refresh

    db = SessionLocal()
    try:
        product_count = db.query(Product).count()
    finally:
        db.close()

    return render("auth/profile.html", {
        "user":         user,
        "info_errors":  info_errors,
        "info_success": info_success,
        "product_count": product_count,
    }, request=request)


def profile_password(request):
    user = _get_current_user(request)
    if not user:
        return redirect("/login/")

    errors, success = [], False
    current  = request.form.get("current_password", "")
    new_pw   = request.form.get("new_password", "")
    confirm  = request.form.get("confirm_password", "")

    db = SessionLocal()
    try:
        u = db.get(User, user.user_id)
        if not check_password_hash(u.password, current):
            errors.append("Current password is incorrect.")
        elif len(new_pw) < 6:
            errors.append("New password must be at least 6 characters.")
        elif new_pw != confirm:
            errors.append("New passwords do not match.")
        else:
            u.password = generate_password_hash(new_pw)
            db.commit()
            success = True
    except Exception:
        db.rollback()
        errors.append("Could not update password — please try again.")
    finally:
        db.close()

    return render("auth/profile.html", {
        "user":          _get_current_user(request),
        "pw_errors":     errors,
        "pw_success":    success,
        "product_count": 0,
    }, request=request)


def home(request):
    db = SessionLocal()
    try:
        featured   = db.query(Product).order_by(Product.product_id.desc()).limit(8).all()
        categories = [r[0] for r in db.query(Product.product_category).distinct()
                      .filter(Product.product_category.isnot(None)).all()]
        return render("index.html", {"featured": featured, "categories": categories}, request=request)
    finally:
        db.close()


def product_list(request):
    db = SessionLocal()
    try:
        category = request.args.get("category", "")
        search   = request.args.get("search", "")
        q = db.query(Product)
        if category:
            q = q.filter(Product.product_category == category)
        if search:
            q = q.filter(Product.product_name.ilike(f"%{search}%"))
        products   = q.order_by(Product.product_name).all()
        categories = [r[0] for r in db.query(Product.product_category).distinct()
                      .filter(Product.product_category.isnot(None)).all()]
        return render("products/list.html", {
            "products":         products,
            "categories":       categories,
            "current_category": category,
            "search":           search,
        }, request=request)
    finally:
        db.close()


def product_detail(request, id):
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if not product:
            return render("404.html", {}, status=404, request=request)
        related = (db.query(Product)
                   .filter(Product.product_category == product.product_category,
                           Product.product_id != id)
                   .limit(4).all())
        return render("products/detail.html",
                      {"product": product, "related": related}, request=request)
    finally:
        db.close()


def _validate_product_form(form):
    errors = []
    name  = form.get("product_name", "").strip()
    price = form.get("product_price", "").strip()
    if not name:
        errors.append("Product name is required.")
    price_val = None
    try:
        price_val = Decimal(price)
        if price_val <= 0:
            errors.append("Price must be greater than zero.")
    except InvalidOperation:
        errors.append("Enter a valid price (e.g. 299.00).")
    stock = 0
    try:
        stock = int(form.get("product_stock", 0))
        if stock < 0:
            errors.append("Stock cannot be negative.")
    except ValueError:
        errors.append("Stock must be a whole number.")
    return errors, name, price_val, stock


def _get_categories():
    db = SessionLocal()
    try:
        return sorted(r[0] for r in db.query(Product.product_category).distinct()
                      .filter(Product.product_category.isnot(None)).all())
    finally:
        db.close()


def product_create(request):
    denied = _require_seller(request)
    if denied:
        return denied
    if request.method == "POST":
        errors, name, price_val, stock = _validate_product_form(request.form)
        if not errors:
            db = SessionLocal()
            try:
                image = (_save_upload(request.files.get("product_image_file"))
                         or request.form.get("product_image", "").strip()
                         or None)
                product = Product(
                    product_name        = name,
                    product_description = request.form.get("product_description", "").strip() or None,
                    product_category    = request.form.get("product_category", "").strip() or None,
                    product_price       = price_val,
                    product_stock       = stock,
                    product_image       = image,
                )
                db.add(product)
                db.commit()
                pid = product.product_id
            except Exception:
                db.rollback()
                errors.append("Database error — please try again.")
                pid = None
            finally:
                db.close()
            if pid:
                return redirect(f"/products/{pid}/")
        return render("products/form.html",
                      {"action": "Create", "errors": errors, "form": request.form,
                       "categories": _get_categories()},
                      status=400, request=request)
    return render("products/form.html",
                  {"action": "Create", "form": {}, "categories": _get_categories()},
                  request=request)


def product_edit(request, id):
    denied = _require_seller(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if not product:
            return render("404.html", {}, status=404, request=request)

        if request.method == "POST":
            errors, name, price_val, stock = _validate_product_form(request.form)
            if not errors:
                uploaded = _save_upload(request.files.get("product_image_file"))
                product.product_name        = name
                product.product_description = request.form.get("product_description", "").strip() or None
                product.product_category    = request.form.get("product_category", "").strip() or None
                product.product_price       = price_val
                product.product_stock       = stock
                product.product_image       = (uploaded
                                               or request.form.get("product_image", "").strip()
                                               or None)
                db.commit()
                return redirect(f"/products/{id}/")
            return render("products/form.html", {
                "action":     "Edit",
                "product":    product,
                "errors":     errors,
                "form":       request.form,
                "categories": _get_categories(),
            }, status=400, request=request)

        return render("products/form.html", {
            "action":     "Edit",
            "product":    product,
            "form":       product.to_dict(),
            "categories": _get_categories(),
        }, request=request)
    finally:
        db.close()


def product_delete(request, id):
    denied = _require_seller(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        product = db.get(Product, id)
        if product:
            db.delete(product)
            db.commit()
    finally:
        db.close()
    return redirect("/products/")


def cart_view(request):
    items, total = _cart_items(request)
    return render("cart.html", {"items": items, "total": total}, request=request)


def cart_add(request):
    cart = _get_cart(request)
    pid  = str(request.form.get("product_id", ""))
    try:
        qty = max(1, int(request.form.get("quantity", 1)))
    except ValueError:
        qty = 1
    if pid:
        cart[pid] = cart.get(pid, 0) + qty
    next_url = request.form.get("next", "/cart/")
    return _set_cart(redirect(next_url), cart)


def cart_update(request):
    cart = _get_cart(request)
    for key, val in request.form.items():
        if key.startswith("qty_"):
            pid = key[4:]
            try:
                qty = int(val)
                if qty > 0:
                    cart[pid] = qty
                else:
                    cart.pop(pid, None)
            except ValueError:
                pass
    return _set_cart(redirect("/cart/"), cart)


def cart_remove(request):
    cart = _get_cart(request)
    cart.pop(str(request.form.get("product_id", "")), None)
    return _set_cart(redirect("/cart/"), cart)


def checkout(request):
    user = _get_current_user(request)
    if not user:
        return redirect("/login/?next=/checkout/&need_login=1")

    items, total = _cart_items(request)
    if request.method == "POST":
        order_id = None
        if items:
            db = SessionLocal()
            try:
                product_ids = [item["product"].product_id for item in items]
                products = (
                    db.query(Product)
                    .filter(Product.product_id.in_(product_ids))
                    .with_for_update()
                    .all()
                )
                products_by_id = {product.product_id: product for product in products}

                for item in items:
                    product = products_by_id.get(item["product"].product_id)
                    if not product:
                        raise ValueError("One of the products is no longer available.")
                    if (product.product_stock or 0) < item["quantity"]:
                        raise ValueError(f"Not enough stock for {product.product_name}.")

                order = Order(
                    user_id = user.user_id,
                    total   = total,
                    status  = "pending",
                )
                db.add(order)
                db.flush()

                for item in items:
                    product = products_by_id[item["product"].product_id]
                    product.product_stock = (product.product_stock or 0) - item["quantity"]
                    db.add(OrderItem(
                        order_id      = order.order_id,
                        product_id    = product.product_id,
                        product_name  = product.product_name,
                        product_price = product.product_price,
                        quantity      = item["quantity"],
                    ))

                db.commit()
                order_id = order.order_id
            except Exception:
                db.rollback()
            finally:
                db.close()
        resp = render("checkout_success.html",
                      {"items": items, "total": total, "order_id": order_id},
                      request=request)
        resp.delete_cookie("cart")
        return resp
    return render("checkout.html", {"items": items, "total": total}, request=request)


def order_list(request):
    user = _get_current_user(request)
    if not user:
        return redirect("/login/?next=/orders/")
    db = SessionLocal()
    try:
        orders = (db.query(Order)
                  .filter(Order.user_id == user.user_id)
                  .order_by(Order.created_at.desc())
                  .all())
        return render("orders/list.html", {"orders": orders}, request=request)
    finally:
        db.close()


def order_detail(request, id):
    user = _get_current_user(request)
    if not user:
        return redirect("/login/")
    db = SessionLocal()
    try:
        order = db.get(Order, id)
        if not order or order.user_id != user.user_id:
            return render("404.html", {}, status=404, request=request)
        return render("orders/detail.html", {"order": order}, request=request)
    finally:
        db.close()


def admin_dashboard(request):
    denied = _require_admin(request)
    if denied:
        return denied
    return redirect("/admin/orders/")


def admin_orders(request):
    denied = _require_admin(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        orders = (db.query(Order)
                  .options(joinedload(Order.user), joinedload(Order.items))
                  .order_by(Order.created_at.desc())
                  .all())
        return render("admin/orders.html", {"orders": orders}, request=request)
    finally:
        db.close()


def admin_order_detail(request, id):
    denied = _require_admin(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        order = (db.query(Order)
                 .options(joinedload(Order.user), joinedload(Order.items))
                 .filter(Order.order_id == id)
                 .first())
        if not order:
            return render("404.html", {}, status=404, request=request)
        return render("admin/order_detail.html", {"order": order}, request=request)
    finally:
        db.close()


def admin_order_status(request, id):
    denied = _require_admin(request)
    if denied:
        return denied
    status = request.form.get("status", "").strip().lower()
    allowed = {"pending", "processing", "completed", "cancelled"}
    if status not in allowed:
        return render("403.html", {}, status=403, request=request)
    db = SessionLocal()
    try:
        order = db.get(Order, id)
        if not order:
            return render("404.html", {}, status=404, request=request)
        order.status = status
        db.commit()
    finally:
        db.close()
    return redirect(f"/admin/orders/{id}/")


def admin_users(request):
    denied = _require_admin(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        return render("admin/users.html", {"users": users}, request=request)
    finally:
        db.close()


def admin_user_toggle(request, id):
    denied = _require_admin(request)
    if denied:
        return denied
    current = _get_current_user(request)
    if current and current.user_id == id:
        return render("403.html", {}, status=403, request=request)
    db = SessionLocal()
    try:
        user = db.get(User, id)
        if not user:
            return render("404.html", {}, status=404, request=request)
        user.is_active = not user.is_active
        db.commit()
    finally:
        db.close()
    return redirect("/admin/users/")


def admin_user_approve_seller(request, id):
    denied = _require_admin(request)
    if denied:
        return denied
    current = _get_current_user(request)
    if current and current.user_id == id:
        return render("403.html", {}, status=403, request=request)
    db = SessionLocal()
    try:
        user = db.get(User, id)
        if not user:
            return render("404.html", {}, status=404, request=request)
        user.role = "seller"
        user.seller_status = "approved"
        if not user.seller_profile:
            db.add(SellerProfile(user_id=user.user_id))
            db.flush()
        db.commit()
    finally:
        db.close()
    return redirect("/admin/users/")


def seller_listings(request):
    denied = _require_seller(request)
    if denied:
        return denied
    db = SessionLocal()
    try:
        products = db.query(Product).order_by(Product.product_id.desc()).all()
        return render("seller/listings.html", {"products": products}, request=request)
    finally:
        db.close()


def not_found(request):
    return render("404.html", {}, status=404, request=request)


# ── Router ────────────────────────────────────────────────────────────────────

VIEWS = {
    "home":           home,
    "login":            login,
    "register":         register,
    "logout":           logout,
    "profile":          profile,
    "profile_password": profile_password,
    "product_list":   product_list,
    "product_create": product_create,
    "product_detail": product_detail,
    "product_edit":   product_edit,
    "product_delete": product_delete,
    "cart_view":      cart_view,
    "cart_add":       cart_add,
    "cart_update":    cart_update,
    "cart_remove":    cart_remove,
    "checkout":       checkout,
    "order_list":     order_list,
    "order_detail":   order_detail,
    "admin_dashboard": admin_dashboard,
    "admin_orders":   admin_orders,
    "admin_order_detail": admin_order_detail,
    "admin_order_status": admin_order_status,
    "admin_users":    admin_users,
    "admin_user_toggle": admin_user_toggle,
    "admin_user_approve_seller": admin_user_approve_seller,
    "seller_listings": seller_listings,
}


def wsgi_app(environ, start_response):
    request = Request(environ)
    adapter = url_map.bind_to_environ(environ)
    try:
        endpoint, kwargs = adapter.match()
        response = VIEWS[endpoint](request, **kwargs)
    except NotFound:
        response = not_found(request)
    except Exception as exc:
        response = Response(f"500 Internal Server Error: {exc}", status=500)
    return response(environ, start_response)


app = SharedDataMiddleware(wsgi_app, {
    "/static": os.path.join(BASE_DIR, "static"),
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple("0.0.0.0", 5000, app, use_debugger=True, use_reloader=True)
