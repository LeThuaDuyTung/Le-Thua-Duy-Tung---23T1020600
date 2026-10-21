
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)

# Thong tin quan ca phe
SHOP = {
    "name": "Ca phe Song Huong",
    "address": "12 Le Loi, Hue",
    "open": 7,
    "close": 22
}

# Danh sach khuyen mai cua bai truoc
PROMOTIONS = [
    "Giam 10% cho sinh vien",
    "Mua 2 tang 1 vao thu Hai",
    "Giam 15% khi dat hang truc tuyen"
]

# Danh sach 5 mon trong thuc don
MENU = [
    {"name": "ca phe den", "price": 20000, "available": True},
    {"name": "bac xiu", "price": 30000, "available": False},
    {"name": "ca phe sua", "price": 25000, "available": True},
    {"name": "tra dao", "price": 35000, "available": True},
    {"name": "matcha latte", "price": 40000, "available": True}
]


# Filter dinh dang tien Viet Nam
@app.template_filter("vnd")
def vnd(gia):
    return "{:,.0f}".format(gia).replace(",", ".") + " đ"


# Trang chu bai 1
@app.route("/")
def trang_chu():
    gio = request.args.get("gio", type=int)

    if gio is None:
        gio = datetime.now().hour

    if gio < 0 or gio > 23:
        return "Gio phai nam trong khoang tu 0 den 23.", 400

    dang_mo = SHOP["open"] <= gio < SHOP["close"]

    if len(PROMOTIONS) == 0:
        khuyen_mai = ["Hien chua co khuyen mai."]
    else:
        khuyen_mai = PROMOTIONS

    return render_template(
        "index.html",
        shop=SHOP,
        gio=gio,
        dang_mo=dang_mo,
        khuyen_mai=khuyen_mai
    )


# Trang thuc don bai 2
@app.route("/menu")
def thuc_don():
    so_mon = len(MENU)

    # Dem so mon dang co
    so_mon_dang_co = 0

    # Tinh tong gia cac mon
    tong_gia = 0

    for mon in MENU:
        tong_gia += mon["price"]

        if mon["available"]:
            so_mon_dang_co += 1

    # Tinh gia trung binh, tranh chia cho 0
    if so_mon > 0:
        gia_trung_binh = tong_gia / so_mon
    else:
        gia_trung_binh = 0

    return render_template(
        "menu.html",
        menu=MENU,
        so_mon=so_mon,
        so_mon_dang_co=so_mon_dang_co,
        gia_trung_binh=gia_trung_binh
    )


if __name__ == "__main__":
    app.run(debug=True)
