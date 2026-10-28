from datetime import datetime

from flask import Flask, render_template, request, abort

app = Flask(__name__, template_folder="templates_chuong4")


# =========================
# BÀI 1: TRANG CHỦ
# =========================

SHOP = {
    "name": "Cà phê Sông Hương",
    "address": "12 Lê Lợi, Huế",
    "phone": "0234 3888 999",
    "open": 7,
    "close": 22
}

PROMOTIONS = [
    "Giảm 10% cho sinh viên",
    "Mua 2 tặng 1 vào thứ Hai"
]


# =========================
# BÀI 2: BẢNG THỰC ĐƠN 5 MÓN
# =========================

MENU_BANG = [
    {"name": "cà phê đen", "price": 20000, "available": True},
    {"name": "bạc xỉu", "price": 30000, "available": False},
    {"name": "cà phê sữa", "price": 25000, "available": True},
    {"name": "trà đào", "price": 35000, "available": True},
    {"name": "nước cam", "price": 35000, "available": True}
]


# =========================
# BÀI 3 VÀ BÀI 4: MENU 7 MÓN
# =========================

MENU = [
    {
        "id": 1,
        "name": "Cà phê đen",
        "price": 20000,
        "available": True,
        "image": "ca-phe-den.jpg"
    },
    {
        "id": 2,
        "name": "Cà phê sữa",
        "price": 25000,
        "available": True,
        "image": "ca-phe-sua.jpg"
    },
    {
        "id": 3,
        "name": "Bạc xỉu",
        "price": 30000,
        "available": True,
        "image": "bac-xiu.jpg"
    },
    {
        "id": 4,
        "name": "Trà đào",
        "price": 35000,
        "available": True,
        "image": "tra-dao.jpg"
    },
    {
        "id": 5,
        "name": "Trà sữa",
        "price": 30000,
        "available": True,
        "image": "tra-sua.jpg"
    },
    {
        "id": 6,
        "name": "Nước cam",
        "price": 25000,
        "available": True,
        "image": "nuoc-cam.jpg"
    },
    {
        "id": 7,
        "name": "Sinh tố bơ",
        "price": 40000,
        "available": True,
        "image": "sinh-to-bo.jpg"
    }
]

PER_PAGE = 3


# Bộ lọc định dạng tiền Việt Nam
@app.template_filter("vnd")
def vnd(value):
    return f"{value:,.0f}".replace(",", ".") + " đ"


# =========================
# BÀI 1: TRANG CHỦ
# =========================

@app.route("/")
def index():
    gio_text = request.args.get("gio")

    if gio_text is not None:
        try:
            gio = int(gio_text)

            if gio < 0 or gio > 23:
                gio = datetime.now().hour
        except ValueError:
            gio = datetime.now().hour
    else:
        gio = datetime.now().hour

    dang_mo = SHOP["open"] <= gio < SHOP["close"]

    return render_template(
        "index.html",
        shop=SHOP,
        promotions=PROMOTIONS,
        gio=gio,
        dang_mo=dang_mo
    )


# =========================
# BÀI 2: BẢNG THỰC ĐƠN
# =========================

@app.route("/menu-bang")
def menu_bang():
    tong_mon = len(MENU_BANG)

    if tong_mon > 0:
        gia_trung_binh = sum(
            item["price"] for item in MENU_BANG
        ) / tong_mon

        so_mon_con = sum(
            1 for item in MENU_BANG if item["available"]
        )
    else:
        gia_trung_binh = 0
        so_mon_con = 0

    return render_template(
        "menu_bang.html",
        items=MENU_BANG,
        tong_mon=tong_mon,
        gia_trung_binh=gia_trung_binh,
        so_mon_con=so_mon_con
    )


# =========================
# BÀI 3 VÀ BÀI 4: MENU PHÂN TRANG
# =========================

@app.route("/menu")
def menu():
    page_text = request.args.get("page", "1")

    try:
        page = int(page_text)
    except (ValueError, TypeError):
        page = 1

    total_items = len(MENU)
    pages = (total_items + PER_PAGE - 1) // PER_PAGE

    if page < 1 or page > pages:
        abort(404)

    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE

    items = MENU[start:end]

    return render_template(
        "menu.html",
        shop=SHOP,
        items=items,
        page=page,
        pages=pages
    )


# =========================
# BÀI 3: LIÊN HỆ
# =========================

@app.route("/contact")
def contact():
    return render_template("contact.html", shop=SHOP)


# =========================
# TRANG LỖI 404
# =========================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", shop=SHOP), 404


if __name__ == "__main__":
    app.run(debug=True)