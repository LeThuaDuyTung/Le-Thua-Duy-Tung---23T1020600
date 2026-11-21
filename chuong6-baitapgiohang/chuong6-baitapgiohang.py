
import os
import uuid
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import (
    DataRequired, Email, Optional, Regexp, Length
)
from sqlalchemy import func, or_


# =========================================================
# 1. KHỞI TẠO FLASK, DATABASE, CSRF
# =========================================================

app = Flask(
    __name__,
    template_folder="templates_chuong6-baitapgio"
)

app.config["SECRET_KEY"] = "nha-sach-song-huong-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///nhasach.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

UPLOAD_FOLDER = os.path.join(
    app.root_path, "static", "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

SHIPPING_FEE = 20000
FREE_SHIPPING_FROM = 200000

ORDER_STATUSES = [
    "Chờ xác nhận",
    "Đang giao",
    "Hoàn tất",
    "Đã huỷ"
]


# =========================================================
# 2. MODEL CATEGORY
# =========================================================

class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)

    books = db.relationship(
        "Book",
        back_populates="category"
    )


# =========================================================
# 3. MODEL BOOK
# =========================================================

class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    publisher = db.Column(db.String(150))
    publication_year = db.Column(db.Integer)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(255))

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    category = db.relationship(
        "Category",
        back_populates="books"
    )

    order_items = db.relationship(
        "OrderItem",
        back_populates="book"
    )


# =========================================================
# 4. MODEL ORDER
# =========================================================

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(150),
        nullable=False
    )

    phone = db.Column(
        db.String(10),
        nullable=False
    )

    email = db.Column(db.String(150))
    address = db.Column(db.Text, nullable=False)
    note = db.Column(db.Text)

    payment_method = db.Column(
        db.String(50),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="Chờ xác nhận"
    )

    subtotal = db.Column(db.Integer, nullable=False)

    shipping_fee = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    total = db.Column(db.Integer, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    items = db.relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )

    histories = db.relationship(
        "OrderHistory",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderHistory.created_at"
    )


# =========================================================
# 5. MODEL ORDER ITEM
# =========================================================

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    book_id = db.Column(
        db.Integer,
        db.ForeignKey("books.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Integer, nullable=False)

    order = db.relationship(
        "Order",
        back_populates="items"
    )

    book = db.relationship(
        "Book",
        back_populates="order_items"
    )


# =========================================================
# 6. MODEL ORDER HISTORY
# =========================================================

class OrderHistory(db.Model):
    __tablename__ = "order_histories"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("orders.id"),
        nullable=False
    )

    status = db.Column(db.String(50), nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )

    order = db.relationship(
        "Order",
        back_populates="histories"
    )


# =========================================================
# 7. FORM CHECKOUT
# =========================================================

class CheckoutForm(FlaskForm):

    customer_name = StringField(
        "Họ tên",
        validators=[
            DataRequired(message="Vui lòng nhập họ tên."),
            Length(max=150)
        ]
    )

    phone = StringField(
        "Số điện thoại",
        validators=[
            DataRequired(message="Vui lòng nhập số điện thoại."),
            Regexp(
                r"^0[0-9]{9}$",
                message="Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0."
            )
        ]
    )

    email = StringField(
        "Email",
        validators=[
            Optional(),
            Email(message="Email không đúng định dạng.")
        ]
    )

    address = TextAreaField(
        "Địa chỉ",
        validators=[
            DataRequired(message="Vui lòng nhập địa chỉ."),
            Length(max=500)
        ]
    )

    note = TextAreaField(
        "Ghi chú",
        validators=[Optional()]
    )

    payment_method = SelectField(
        "Thanh toán",
        choices=[
            ("Tiền mặt khi nhận hàng", "Tiền mặt khi nhận hàng"),
            ("Chuyển khoản", "Chuyển khoản")
        ],
        validators=[DataRequired()]
    )

    submit = SubmitField("Xác nhận đặt hàng")


# =========================================================
# 8. HÀM TIỆN ÍCH
# =========================================================

def get_cart():
    return session.get("cart", {})


def cart_count():
    return sum(
        int(quantity)
        for quantity in get_cart().values()
    )


def get_cart_items():
    cart_data = get_cart()
    result = []
    total = 0

    for book_id, quantity in cart_data.items():

        book = db.session.get(Book, int(book_id))

        if book is None:
            continue

        quantity = int(quantity)

        line_total = book.price * quantity
        total += line_total

        result.append({
            "book": book,
            "quantity": quantity,
            "line_total": line_total
        })

    return result, total


def shipping_cost(subtotal):
    if subtotal >= FREE_SHIPPING_FROM:
        return 0

    return SHIPPING_FEE


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


def save_cover(file):
    if not file or not file.filename:
        return None

    if not allowed_file(file.filename):
        raise ValueError(
            "Ảnh phải có định dạng JPG, PNG hoặc WEBP."
        )

    extension = file.filename.rsplit(".", 1)[1].lower()

    filename = f"{uuid.uuid4().hex}.{extension}"

    file.save(
        os.path.join(UPLOAD_FOLDER, filename)
    )

    return filename


def delete_cover(filename):
    if not filename:
        return

    path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if os.path.isfile(path):
        os.remove(path)


@app.context_processor
def inject_global_values():

    return {
        "cart_count": cart_count(),

        "pending_orders": Order.query.filter_by(
            status="Chờ xác nhận"
        ).count(),

        "now": datetime.now()
    }


# =========================================================
# 9. DỮ LIỆU MẪU
# =========================================================

def create_sample_data():

    if Category.query.first():
        return

    category_names = [
        "Lập trình",
        "Cơ sở dữ liệu",
        "Công cụ",
        "Mạng",
        "Kỹ năng lập trình",
        "Thiết kế"
    ]

    categories = {}

    for name in category_names:

        category = Category(name=name)

        db.session.add(category)

        categories[name] = category

    db.session.flush()

    sample_books = [
        (
            "Lập trình Python cơ bản",
            "Nguyễn Văn A",
            "Đại học Huế",
            2024,
            95000,
            30,
            "Lập trình"
        ),
        (
            "Giáo trình Flask",
            "Miguel Grinberg",
            "O'Reilly",
            2022,
            120000,
            20,
            "Lập trình"
        ),
        (
            "Cơ sở dữ liệu",
            "Trần Văn B",
            "Giáo dục",
            2023,
            85000,
            0,
            "Cơ sở dữ liệu"
        ),
        (
            "Pro Git",
            "Scott Chacon",
            "Apress",
            2014,
            150000,
            15,
            "Công cụ"
        ),
        (
            "Mạng máy tính",
            "Lê Văn C",
            "Giáo dục",
            2023,
            110000,
            12,
            "Mạng"
        ),
        (
            "Clean Code",
            "Robert C. Martin",
            "Prentice Hall",
            2008,
            180000,
            5,
            "Kỹ năng lập trình"
        )
    ]

    for item in sample_books:

        title, author, publisher, year, price, stock, category_name = item

        book = Book(
            title=title,
            author=author,
            publisher=publisher,
            publication_year=year,
            price=price,
            stock=stock,
            category=categories[category_name]
        )

        db.session.add(book)

    db.session.commit()

    print("Da tao 6 sach mau va 6 danh muc.")


# =========================================================
# PHẦN A - TRANG BÁN HÀNG
# =========================================================

# =========================================================
# 10. TRANG CHỦ VÀ DANH SÁCH SÁCH
# =========================================================

@app.route("/")
def index():
    return redirect(url_for("books"))


@app.route("/books")
def books():

    keyword = request.args.get(
        "keyword", ""
    ).strip()

    category_id = request.args.get(
        "category_id", ""
    )

    query = Book.query

    if keyword:

        query = query.filter(
            or_(
                Book.title.ilike(f"%{keyword}%"),
                Book.author.ilike(f"%{keyword}%")
            )
        )

    if category_id.isdigit():

        query = query.filter(
            Book.category_id == int(category_id)
        )

    book_list = query.order_by(
        Book.id.asc()
    ).all()

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        "books.html",
        books=book_list,
        categories=categories,
        keyword=keyword,
        selected_category=category_id
    )


# =========================================================
# 11. CHI TIẾT SÁCH
# =========================================================

@app.route("/books/<int:book_id>")
def book_detail(book_id):

    book = db.session.get(Book, book_id)

    if book is None:
        abort(404)

    current_quantity = int(
        get_cart().get(str(book_id), 0)
    )

    max_quantity = max(
        0,
        book.stock - current_quantity
    )

    return render_template(
        "book_detail.html",
        book=book,
        current_quantity=current_quantity,
        max_quantity=max_quantity
    )


# =========================================================
# 12. THÊM SÁCH VÀO GIỎ
# =========================================================

@app.route(
    "/cart/add/<int:book_id>",
    methods=["POST"]
)
def add_to_cart(book_id):

    book = db.session.get(Book, book_id)

    if book is None:
        abort(404)

    try:
        quantity = int(
            request.form.get("quantity", 1)
        )
    except (ValueError, TypeError):
        quantity = 0

    cart_data = get_cart()

    key = str(book_id)

    old_quantity = int(
        cart_data.get(key, 0)
    )

    if quantity < 1:

        flash(
            "Số lượng phải từ 1 trở lên.",
            "danger"
        )

    elif old_quantity + quantity > book.stock:

        flash(
            f"Không đủ hàng. Sách {book.title} "
            f"hiện còn {book.stock - old_quantity} cuốn có thể thêm.",
            "danger"
        )

    else:

        cart_data[key] = old_quantity + quantity

        session["cart"] = cart_data
        session.modified = True

        flash(
            f"Đã thêm {quantity} × {book.title} vào giỏ hàng.",
            "success"
        )

    return redirect(
        request.referrer or url_for("books")
    )


# =========================================================
# 13. GIỎ HÀNG
# =========================================================

@app.route("/cart")
def cart():

    items, subtotal = get_cart_items()

    return render_template(
        "cart.html",
        items=items,
        subtotal=subtotal
    )


@app.route(
    "/cart/increase/<int:book_id>",
    methods=["POST"]
)
def cart_increase(book_id):

    book = db.session.get(Book, book_id)

    cart_data = get_cart()

    key = str(book_id)

    if book is None:

        cart_data.pop(key, None)

        session["cart"] = cart_data

        flash(
            "Sách không còn tồn tại.",
            "warning"
        )

    else:

        quantity = int(
            cart_data.get(key, 0)
        )

        if quantity < book.stock:

            cart_data[key] = quantity + 1

            flash(
                "Đã tăng số lượng.",
                "success"
            )

        else:

            flash(
                "Số lượng đã đạt tồn kho.",
                "warning"
            )

        session["cart"] = cart_data

    return redirect(url_for("cart"))


@app.route(
    "/cart/decrease/<int:book_id>",
    methods=["POST"]
)
def cart_decrease(book_id):

    cart_data = get_cart()

    key = str(book_id)

    quantity = int(
        cart_data.get(key, 0)
    )

    if quantity <= 1:

        cart_data.pop(key, None)

    else:

        cart_data[key] = quantity - 1

    session["cart"] = cart_data

    flash(
        "Đã cập nhật giỏ hàng.",
        "success"
    )

    return redirect(url_for("cart"))


@app.route(
    "/cart/remove/<int:book_id>",
    methods=["POST"]
)
def cart_remove(book_id):

    cart_data = get_cart()

    cart_data.pop(str(book_id), None)

    session["cart"] = cart_data

    flash(
        "Đã xóa sách khỏi giỏ hàng.",
        "success"
    )

    return redirect(url_for("cart"))


@app.route(
    "/cart/clear",
    methods=["POST"]
)
def cart_clear():

    session["cart"] = {}

    flash(
        "Đã xóa toàn bộ giỏ hàng.",
        "success"
    )

    return redirect(url_for("cart"))


# =========================================================
# 14. CHECKOUT
# =========================================================

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():

    items, subtotal = get_cart_items()

    if not items:

        flash(
            "Giỏ hàng trống. Vui lòng chọn sách trước.",
            "warning"
        )

        return redirect(url_for("cart"))

    form = CheckoutForm()

    fee = shipping_cost(subtotal)

    total = subtotal + fee

    if form.validate_on_submit():

        # Kiểm tra tồn kho lại trước khi tạo đơn.
        for item in items:

            book = db.session.get(
                Book,
                item["book"].id
            )

            if book is None or book.stock < item["quantity"]:

                flash(
                    f"Sách {item['book'].title} không đủ tồn kho. "
                    "Đơn hàng chưa được tạo.",
                    "danger"
                )

                return redirect(url_for("cart"))

        try:

            order = Order(
                customer_name=form.customer_name.data.strip(),

                phone=form.phone.data.strip(),

                email=(
                    (form.email.data or "").strip() or None
                ),

                address=form.address.data.strip(),

                note=(form.note.data or "").strip(),

                payment_method=form.payment_method.data,

                status="Chờ xác nhận",

                subtotal=subtotal,

                shipping_fee=fee,

                total=total
            )

            db.session.add(order)

            db.session.flush()

            for item in items:

                book = db.session.get(
                    Book,
                    item["book"].id
                )

                quantity = item["quantity"]

                db.session.add(
                    OrderItem(
                        order_id=order.id,
                        book_id=book.id,
                        quantity=quantity,
                        unit_price=book.price
                    )
                )

                book.stock -= quantity

            db.session.add(
                OrderHistory(
                    order_id=order.id,
                    status="Chờ xác nhận"
                )
            )

            db.session.commit()

            session["cart"] = {}

            flash(
                "Đặt hàng thành công!",
                "success"
            )

            return redirect(
                url_for(
                    "order_success",
                    order_id=order.id
                )
            )

        except Exception as error:

            db.session.rollback()

            app.logger.exception(
                "Loi khi tao don hang: %s",
                error
            )

            flash(
                "Có lỗi khi tạo đơn hàng. Vui lòng thử lại.",
                "danger"
            )

    return render_template(
        "checkout.html",
        form=form,
        items=items,
        subtotal=subtotal,
        shipping_fee=fee,
        total=total
    )


# =========================================================
# 15. ĐẶT HÀNG THÀNH CÔNG
# =========================================================

@app.route("/orders/<int:order_id>")
def order_success(order_id):

    order = db.session.get(
        Order,
        order_id
    )

    if order is None:
        abort(404)

    return render_template(
        "order_success.html",
        order=order
    )


# =========================================================
# PHẦN B - TRANG QUẢN TRỊ
# =========================================================

# =========================================================
# 16. HÀM HIỂN THỊ TEMPLATE ADMIN
# =========================================================

def render_admin(page, **kwargs):

    templates = {
        "dashboard": "admin/dashboard.html",
        "admin_books": "admin/books.html",
        "book_form": "admin/book_form.html",
        "categories": "admin/categories.html",
        "admin_orders": "admin/orders.html",
        "admin_order_detail": "admin/order_detail.html"
    }

    template_name = templates.get(page)

    if template_name is None:
        abort(404)

    return render_template(
        template_name,
        **kwargs
    )


# =========================================================
# 17. DASHBOARD
# =========================================================

@app.route("/admin")
def admin_dashboard():

    book_count = db.session.query(
        func.count(Book.id)
    ).scalar() or 0

    pending_count = db.session.query(
        func.count(Order.id)
    ).filter(
        Order.status == "Chờ xác nhận"
    ).scalar() or 0

    month_start = datetime.now().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    month_revenue = db.session.query(
        func.sum(Order.total)
    ).filter(
        Order.status == "Hoàn tất",
        Order.created_at >= month_start
    ).scalar() or 0

    low_stock_count = db.session.query(
        func.count(Book.id)
    ).filter(
        Book.stock <= 5
    ).scalar() or 0

    latest_orders = Order.query.order_by(
        Order.created_at.desc()
    ).limit(5).all()

    low_stock_books = Book.query.filter(
        Book.stock <= 5
    ).order_by(
        Book.stock.asc()
    ).all()

    return render_admin(
        "dashboard",
        book_count=book_count,
        pending_count=pending_count,
        month_revenue=month_revenue,
        low_stock_count=low_stock_count,
        latest_orders=latest_orders,
        low_stock_books=low_stock_books
    )


# =========================================================
# 18. QUẢN LÝ SÁCH
# =========================================================

@app.route("/admin/books")
def admin_books():

    keyword = request.args.get(
        "keyword", ""
    ).strip()

    category_id = request.args.get(
        "category_id", ""
    )

    stock_filter = request.args.get(
        "stock", ""
    )

    page_number = request.args.get(
        "page", 1, type=int
    )

    query = Book.query

    if keyword:

        query = query.filter(
            or_(
                Book.title.ilike(f"%{keyword}%"),
                Book.author.ilike(f"%{keyword}%")
            )
        )

    if category_id.isdigit():

        query = query.filter(
            Book.category_id == int(category_id)
        )

    if stock_filter == "available":

        query = query.filter(
            Book.stock > 5
        )

    elif stock_filter == "low":

        query = query.filter(
            Book.stock.between(1, 5)
        )

    elif stock_filter == "out":

        query = query.filter(
            Book.stock == 0
        )

    pagination = query.order_by(
        Book.created_at.desc(),
        Book.id.desc()
    ).paginate(
        page=page_number,
        per_page=5,
        error_out=False
    )

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_admin(
        "admin_books",
        pagination=pagination,
        categories=categories,
        keyword=keyword,
        selected_category=category_id,
        stock_filter=stock_filter
    )


# =========================================================
# 19. THÊM / SỬA SÁCH
# =========================================================

@app.route(
    "/admin/books/new",
    methods=["GET", "POST"]
)
@app.route(
    "/admin/books/<int:book_id>/edit",
    methods=["GET", "POST"]
)
def admin_book_form(book_id=None):

    book = (
        db.session.get(Book, book_id)
        if book_id else None
    )

    if book_id and book is None:
        abort(404)

    categories = Category.query.order_by(
        Category.name
    ).all()

    if request.method == "POST":

        title = request.form.get(
            "title", ""
        ).strip()

        author = request.form.get(
            "author", ""
        ).strip()

        publisher = request.form.get(
            "publisher", ""
        ).strip()

        year_text = request.form.get(
            "publication_year", ""
        ).strip()

        price_text = request.form.get(
            "price", ""
        ).strip()

        stock_text = request.form.get(
            "stock", ""
        ).strip()

        category_text = request.form.get(
            "category_id", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        errors = []

        if not title:
            errors.append("Tên sách là bắt buộc.")

        if not author:
            errors.append("Tác giả là bắt buộc.")

        duplicate = Book.query.filter(
            func.lower(Book.title) == title.lower()
        )

        if book:
            duplicate = duplicate.filter(
                Book.id != book.id
            )

        if title and duplicate.first():
            errors.append("Tên sách đã tồn tại.")

        try:

            price = int(price_text)

            if price < 1000:
                errors.append(
                    "Giá sách phải từ 1.000 đồng."
                )

        except (ValueError, TypeError):

            price = 0

            errors.append(
                "Giá sách phải là số nguyên."
            )

        try:

            stock = int(stock_text)

            if stock < 0:
                errors.append(
                    "Tồn kho phải lớn hơn hoặc bằng 0."
                )

        except (ValueError, TypeError):

            stock = 0

            errors.append(
                "Tồn kho phải là số nguyên."
            )

        year = None

        if year_text:

            try:

                year = int(year_text)

                if year < 1900 or year > datetime.now().year:

                    errors.append(
                        "Năm xuất bản phải từ 1900 đến năm hiện tại."
                    )

            except ValueError:

                errors.append(
                    "Năm xuất bản không hợp lệ."
                )

        category = None

        if category_text.isdigit():

            category = db.session.get(
                Category,
                int(category_text)
            )

        if category is None:

            errors.append(
                "Vui lòng chọn danh mục."
            )

        uploaded_file = request.files.get(
            "cover_image"
        )

        new_cover = None

        if uploaded_file and uploaded_file.filename:

            try:

                new_cover = save_cover(
                    uploaded_file
                )

            except ValueError as error:

                errors.append(str(error))

        if errors:

            # Tránh để lại file ảnh mới nếu dữ liệu không hợp lệ.
            if new_cover:
                delete_cover(new_cover)

            for error in errors:

                flash(
                    error,
                    "danger"
                )

            return render_admin(
                "book_form",
                book=book,
                categories=categories,
                values=request.form
            )

        if book is None:

            book = Book()

            db.session.add(book)

        old_cover = book.cover_image

        book.title = title
        book.author = author
        book.publisher = publisher
        book.publication_year = year
        book.price = price
        book.stock = stock
        book.category = category
        book.description = description

        if new_cover:
            book.cover_image = new_cover

        try:

            db.session.commit()

        except Exception:

            db.session.rollback()

            if new_cover:
                delete_cover(new_cover)

            flash(
                "Không thể lưu thông tin sách.",
                "danger"
            )

            return redirect(
                request.url
            )

        if new_cover and old_cover:
            delete_cover(old_cover)

        flash(
            "Đã lưu thông tin sách.",
            "success"
        )

        return redirect(
            url_for("admin_books")
        )

    return render_admin(
        "book_form",
        book=book,
        categories=categories,
        values={}
    )


# =========================================================
# 20. XÓA SÁCH
# =========================================================

@app.route(
    "/admin/books/<int:book_id>/delete",
    methods=["POST"]
)
def admin_book_delete(book_id):

    book = db.session.get(
        Book,
        book_id
    )

    if book is None:
        abort(404)

    if OrderItem.query.filter_by(
        book_id=book_id
    ).first():

        flash(
            "Không thể xóa sách đã có trong đơn hàng.",
            "danger"
        )

    else:

        delete_cover(book.cover_image)

        db.session.delete(book)

        db.session.commit()

        flash(
            "Đã xóa sách.",
            "success"
        )

    return redirect(
        url_for("admin_books")
    )


# =========================================================
# 21. QUẢN LÝ DANH MỤC
# =========================================================

@app.route(
    "/admin/categories",
    methods=["GET", "POST"]
)
def admin_categories():

    edit_id = request.args.get(
        "edit",
        type=int
    )

    editing = (
        db.session.get(Category, edit_id)
        if edit_id else None
    )

    if request.method == "POST":

        action = request.form.get(
            "action", "add"
        )

        name = request.form.get(
            "name", ""
        ).strip()

        description = request.form.get(
            "description", ""
        ).strip()

        if not name:

            flash(
                "Tên danh mục không được để trống.",
                "danger"
            )

            return redirect(
                url_for("admin_categories")
            )

        current_id = request.form.get(
            "category_id",
            type=int
        )

        category = (
            db.session.get(Category, current_id)
            if current_id else None
        )

        duplicate = Category.query.filter(
            func.lower(Category.name) == name.lower()
        )

        if category:

            duplicate = duplicate.filter(
                Category.id != category.id
            )

        if duplicate.first():

            flash(
                "Danh mục đã tồn tại.",
                "danger"
            )

            return redirect(
                url_for("admin_categories")
            )

        if action == "edit":

            if category is None:
                abort(404)

            category.name = name
            category.description = description

            flash(
                "Đã cập nhật danh mục.",
                "success"
            )

        else:

            db.session.add(
                Category(
                    name=name,
                    description=description
                )
            )

            flash(
                "Đã thêm danh mục.",
                "success"
            )

        db.session.commit()

        return redirect(
            url_for("admin_categories")
        )

    counts = db.session.query(
        Category,
        func.count(Book.id).label("book_count")
    ).outerjoin(
        Book
    ).group_by(
        Category.id
    ).order_by(
        Category.name
    ).all()

    return render_admin(
        "categories",
        category_counts=counts,
        editing=editing
    )


# =========================================================
# 22. XÓA DANH MỤC
# =========================================================

@app.route(
    "/admin/categories/<int:category_id>/delete",
    methods=["POST"]
)
def admin_category_delete(category_id):

    category = db.session.get(
        Category,
        category_id
    )

    if category is None:
        abort(404)

    count = Book.query.filter_by(
        category_id=category_id
    ).count()

    if count > 0:

        flash(
            f'Không thể xóa "{category.name}": còn {count} sách.',
            "danger"
        )

    else:

        db.session.delete(category)

        db.session.commit()

        flash(
            "Đã xóa danh mục.",
            "success"
        )

    return redirect(
        url_for("admin_categories")
    )


# =========================================================
# 23. DANH SÁCH ĐƠN HÀNG
# =========================================================

@app.route("/admin/orders")
def admin_orders():

    status = request.args.get(
        "status", ""
    ).strip()

    keyword = request.args.get(
        "keyword", ""
    ).strip()

    page_number = request.args.get(
        "page", 1, type=int
    )

    grouped = db.session.query(
        Order.status,
        func.count(Order.id)
    ).group_by(
        Order.status
    ).all()

    status_counts = {
        name: count
        for name, count in grouped
    }

    total_count = sum(
        status_counts.values()
    )

    query = Order.query

    if status in ORDER_STATUSES:

        query = query.filter(
            Order.status == status
        )

    if keyword:

        conditions = [
            Order.customer_name.ilike(
                f"%{keyword}%"
            ),
            Order.phone.ilike(
                f"%{keyword}%"
            )
        ]

        if keyword.isdigit():

            conditions.append(
                Order.id == int(keyword)
            )

        query = query.filter(
            or_(*conditions)
        )

    filtered_count = query.count()

    filtered_total = query.with_entities(
        func.sum(Order.total)
    ).scalar() or 0

    pagination = query.order_by(
        Order.created_at.desc(),
        Order.id.desc()
    ).paginate(
        page=page_number,
        per_page=10,
        error_out=False
    )

    return render_admin(
        "admin_orders",
        pagination=pagination,
        status=status,
        keyword=keyword,
        status_counts=status_counts,
        total_count=total_count,
        filtered_count=filtered_count,
        filtered_total=filtered_total,
        statuses=ORDER_STATUSES
    )


# =========================================================
# 24. CHI TIẾT ĐƠN HÀNG
# =========================================================

@app.route(
    "/admin/orders/<int:order_id>"
)
def admin_order_detail(order_id):

    order = db.session.get(
        Order,
        order_id
    )

    if order is None:
        abort(404)

    return render_admin(
        "admin_order_detail",
        order=order
    )


# =========================================================
# 25. CẬP NHẬT TRẠNG THÁI ĐƠN HÀNG
# =========================================================

@app.route(
    "/admin/orders/<int:order_id>/status",
    methods=["POST"]
)
def admin_order_status(order_id):

    order = db.session.get(
        Order,
        order_id
    )

    if order is None:
        abort(404)

    new_status = request.form.get(
        "status", ""
    ).strip()

    old_status = order.status

    if old_status in ["Hoàn tất", "Đã huỷ"]:

        flash(
            "Đơn hàng đã kết thúc, không thể đổi trạng thái.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_order_detail",
                order_id=order_id
            )
        )

    valid_transitions = {
        "Chờ xác nhận": [
            "Đang giao",
            "Đã huỷ"
        ],
        "Đang giao": [
            "Hoàn tất",
            "Đã huỷ"
        ]
    }

    if new_status not in valid_transitions.get(
        old_status, []
    ):

        flash(
            "Chuyển trạng thái không hợp lệ.",
            "danger"
        )

        return redirect(
            url_for(
                "admin_order_detail",
                order_id=order_id
            )
        )

    try:

        if new_status == "Đã huỷ":

            # Hoàn lại tồn kho khi hủy đơn.
            for item in order.items:

                book = db.session.get(
                    Book,
                    item.book_id
                )

                if book:
                    book.stock += item.quantity

        order.status = new_status

        db.session.add(
            OrderHistory(
                order_id=order.id,
                status=new_status
            )
        )

        db.session.commit()

        flash(
            "Đã cập nhật trạng thái đơn hàng.",
            "success"
        )

    except Exception:

        db.session.rollback()

        flash(
            "Không thể cập nhật trạng thái đơn hàng.",
            "danger"
        )

    return redirect(
        url_for(
            "admin_order_detail",
            order_id=order_id
        )
    )


# =========================================================
# 26. LỖI 404
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "errors/404.html"
    ), 404


# =========================================================
# 27. TẠO DATABASE VÀ CHẠY ỨNG DỤNG
# =========================================================

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

        create_sample_data()

    print("NHA SACH SONG HUONG - DATABASE READY")

    app.run(
        debug=True
    )
