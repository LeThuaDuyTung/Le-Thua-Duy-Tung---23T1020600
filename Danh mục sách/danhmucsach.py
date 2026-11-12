
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Float, Integer, ForeignKey
import os


# =====================================================
# PHẦN 1: KHỞI TẠO FLASK VÀ SQLALCHEMY
# =====================================================

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

app = Flask(
    __name__,
    template_folder="templates_danhmucsach"
)

app.config["SECRET_KEY"] = "danh-muc-sach-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///danhmucsach.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# =====================================================
# PHẦN 2: KHAI BÁO MODEL DANH MỤC SÁCH
# =====================================================

class DanhMuc(db.Model):
    __tablename__ = "danhmuc"

    id: Mapped[int] = mapped_column(primary_key=True)

    ten_danh_muc: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    mo_ta: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Một danh mục có nhiều sách
    sach_list: Mapped[list["Sach"]] = relationship(
        back_populates="danh_muc",
        lazy="select"
    )

    def __repr__(self):
        return f"<DanhMuc {self.ten_danh_muc}>"


# =====================================================
# PHẦN 3: KHAI BÁO MODEL SÁCH
# =====================================================

class Sach(db.Model):
    __tablename__ = "sach"

    id: Mapped[int] = mapped_column(primary_key=True)

    ten_sach: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    tac_gia: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    gia: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    so_luong: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    danh_muc_id: Mapped[int] = mapped_column(
        ForeignKey("danhmuc.id"),
        nullable=False
    )

    # Mỗi sách thuộc về một danh mục
    danh_muc: Mapped["DanhMuc"] = relationship(
        back_populates="sach_list"
    )

    def __repr__(self):
        return f"<Sach {self.ten_sach}>"


# =====================================================
# PHẦN 4: BỘ LỌC ĐỊNH DẠNG TIỀN VIỆT NAM
# =====================================================

@app.template_filter("vnd")
def vnd(value):
    return f"{value:,.0f}".replace(",", ".") + " đ"


# =====================================================
# PHẦN 5: DASHBOARD QUẢN LÝ
# =====================================================

@app.route("/")
@app.route("/dashboard")
def dashboard():

    tong_danh_muc = db.session.query(DanhMuc).count()
    tong_sach = db.session.query(Sach).count()

    tong_so_luong = db.session.query(
        db.func.sum(Sach.so_luong)
    ).scalar() or 0

    sach_moi = db.session.execute(
        db.select(Sach).order_by(Sach.id.desc()).limit(5)
    ).scalars().all()

    danh_muc_list = db.session.execute(
        db.select(DanhMuc).order_by(DanhMuc.id.desc())
    ).scalars().all()

    return render_template(
        "dashboard.html",
        tong_danh_muc=tong_danh_muc,
        tong_sach=tong_sach,
        tong_so_luong=tong_so_luong,
        sach_moi=sach_moi,
        danh_muc_list=danh_muc_list
    )


# =====================================================
# PHẦN 6: CRUD DANH MỤC SÁCH
# CREATE - READ - UPDATE - DELETE
# =====================================================

# -------------------------
# 6.1. READ: DANH SÁCH DANH MỤC
# -------------------------

@app.route("/danhmuc")
def danhmuc_list():

    danh_muc_list = db.session.execute(
        db.select(DanhMuc).order_by(DanhMuc.id.desc())
    ).scalars().all()

    return render_template(
        "danhmuc_list.html",
        danh_muc_list=danh_muc_list
    )


# -------------------------
# 6.2. CREATE: THÊM DANH MỤC
# -------------------------

@app.route("/danhmuc/them", methods=["GET", "POST"])
def danhmuc_add():

    if request.method == "POST":

        ten_danh_muc = request.form.get(
            "ten_danh_muc", ""
        ).strip()

        mo_ta = request.form.get(
            "mo_ta", ""
        ).strip()

        if not ten_danh_muc:
            flash("Vui lòng nhập tên danh mục!", "danger")
            return render_template("danhmuc_form.html", action="Thêm")

        danh_muc_trung = db.session.execute(
            db.select(DanhMuc).where(
                db.func.lower(DanhMuc.ten_danh_muc)
                == ten_danh_muc.lower()
            )
        ).scalar_one_or_none()

        if danh_muc_trung:
            flash("Tên danh mục đã tồn tại!", "danger")
            return render_template("danhmuc_form.html", action="Thêm")

        danh_muc = DanhMuc(
            ten_danh_muc=ten_danh_muc,
            mo_ta=mo_ta
        )

        db.session.add(danh_muc)
        db.session.commit()

        flash("Thêm danh mục thành công!", "success")
        return redirect(url_for("danhmuc_list"))

    return render_template(
        "danhmuc_form.html",
        action="Thêm"
    )


# -------------------------
# 6.3. UPDATE: SỬA DANH MỤC
# -------------------------

@app.route("/danhmuc/sua/<int:id>", methods=["GET", "POST"])
def danhmuc_edit(id):

    danh_muc = db.get_or_404(DanhMuc, id)

    if request.method == "POST":

        ten_danh_muc = request.form.get(
            "ten_danh_muc", ""
        ).strip()

        mo_ta = request.form.get(
            "mo_ta", ""
        ).strip()

        if not ten_danh_muc:
            flash("Tên danh mục không được để trống!", "danger")
            return render_template(
                "danhmuc_form.html",
                action="Sửa",
                danh_muc=danh_muc
            )

        danh_muc_trung = db.session.execute(
            db.select(DanhMuc).where(
                db.func.lower(DanhMuc.ten_danh_muc)
                == ten_danh_muc.lower(),
                DanhMuc.id != id
            )
        ).scalar_one_or_none()

        if danh_muc_trung:
            flash("Tên danh mục đã được sử dụng!", "danger")
            return render_template(
                "danhmuc_form.html",
                action="Sửa",
                danh_muc=danh_muc
            )

        danh_muc.ten_danh_muc = ten_danh_muc
        danh_muc.mo_ta = mo_ta

        db.session.commit()

        flash("Cập nhật danh mục thành công!", "success")
        return redirect(url_for("danhmuc_list"))

    return render_template(
        "danhmuc_form.html",
        action="Sửa",
        danh_muc=danh_muc
    )


# -------------------------
# 6.4. DELETE: XÓA DANH MỤC
# -------------------------

@app.route("/danhmuc/xoa/<int:id>", methods=["POST"])
def danhmuc_delete(id):

    danh_muc = db.get_or_404(DanhMuc, id)

    # Không cho xóa danh mục nếu vẫn còn sách
    if danh_muc.sach_list:
        flash(
            "Không thể xóa danh mục đang có sách. "
            "Hãy chuyển hoặc xóa sách trước!",
            "danger"
        )
        return redirect(url_for("danhmuc_list"))

    db.session.delete(danh_muc)
    db.session.commit()

    flash("Xóa danh mục thành công!", "success")
    return redirect(url_for("danhmuc_list"))


# =====================================================
# PHẦN 7: CRUD SÁCH THEO DANH MỤC
# =====================================================

# -------------------------
# 7.1. READ: DANH SÁCH SÁCH
# -------------------------

@app.route("/sach")
def sach_list():

    danh_muc_id = request.args.get("danh_muc_id", type=int)

    query = db.select(Sach).join(DanhMuc)

    if danh_muc_id:
        query = query.where(Sach.danh_muc_id == danh_muc_id)

    sach_list = db.session.execute(
        query.order_by(Sach.id.desc())
    ).scalars().all()

    danh_muc_list = db.session.execute(
        db.select(DanhMuc).order_by(DanhMuc.ten_danh_muc)
    ).scalars().all()

    return render_template(
        "sach_list.html",
        sach_list=sach_list,
        danh_muc_list=danh_muc_list,
        danh_muc_id=danh_muc_id
    )


# -------------------------
# 7.2. CREATE: THÊM SÁCH
# -------------------------

@app.route("/sach/them", methods=["GET", "POST"])
def sach_add():

    danh_muc_list = db.session.execute(
        db.select(DanhMuc).order_by(DanhMuc.ten_danh_muc)
    ).scalars().all()

    if not danh_muc_list:
        flash("Bạn cần tạo danh mục trước khi thêm sách!", "warning")
        return redirect(url_for("danhmuc_add"))

    if request.method == "POST":

        ten_sach = request.form.get("ten_sach", "").strip()
        tac_gia = request.form.get("tac_gia", "").strip()
        gia_text = request.form.get("gia", "").strip()
        so_luong_text = request.form.get("so_luong", "").strip()
        danh_muc_id = request.form.get("danh_muc_id", type=int)

        try:
            gia = float(gia_text)
            so_luong = int(so_luong_text)
        except ValueError:
            flash("Giá và số lượng phải là số hợp lệ!", "danger")
            return render_template(
                "sach_form.html",
                action="Thêm",
                danh_muc_list=danh_muc_list
            )

        if not ten_sach or not tac_gia:
            flash("Vui lòng nhập tên sách và tác giả!", "danger")
            return render_template(
                "sach_form.html",
                action="Thêm",
                danh_muc_list=danh_muc_list
            )

        if gia < 0 or so_luong < 0:
            flash("Giá và số lượng không được âm!", "danger")
            return render_template(
                "sach_form.html",
                action="Thêm",
                danh_muc_list=danh_muc_list
            )

        danh_muc = db.session.get(DanhMuc, danh_muc_id)

        if danh_muc is None:
            flash("Danh mục không hợp lệ!", "danger")
            return render_template(
                "sach_form.html",
                action="Thêm",
                danh_muc_list=danh_muc_list
            )

        sach = Sach(
            ten_sach=ten_sach,
            tac_gia=tac_gia,
            gia=gia,
            so_luong=so_luong,
            danh_muc_id=danh_muc_id
        )

        db.session.add(sach)
        db.session.commit()

        flash("Thêm sách thành công!", "success")
        return redirect(url_for("sach_list"))

    return render_template(
        "sach_form.html",
        action="Thêm",
        danh_muc_list=danh_muc_list
    )


# -------------------------
# 7.3. UPDATE: SỬA SÁCH
# -------------------------

@app.route("/sach/sua/<int:id>", methods=["GET", "POST"])
def sach_edit(id):

    sach = db.get_or_404(Sach, id)

    danh_muc_list = db.session.execute(
        db.select(DanhMuc).order_by(DanhMuc.ten_danh_muc)
    ).scalars().all()

    if request.method == "POST":

        ten_sach = request.form.get("ten_sach", "").strip()
        tac_gia = request.form.get("tac_gia", "").strip()
        gia_text = request.form.get("gia", "").strip()
        so_luong_text = request.form.get("so_luong", "").strip()
        danh_muc_id = request.form.get("danh_muc_id", type=int)

        try:
            gia = float(gia_text)
            so_luong = int(so_luong_text)
        except ValueError:
            flash("Giá và số lượng phải là số hợp lệ!", "danger")
            return render_template(
                "sach_form.html",
                action="Sửa",
                sach=sach,
                danh_muc_list=danh_muc_list
            )

        if not ten_sach or not tac_gia:
            flash("Vui lòng nhập tên sách và tác giả!", "danger")
            return render_template(
                "sach_form.html",
                action="Sửa",
                sach=sach,
                danh_muc_list=danh_muc_list
            )

        if gia < 0 or so_luong < 0:
            flash("Giá và số lượng không được âm!", "danger")
            return render_template(
                "sach_form.html",
                action="Sửa",
                sach=sach,
                danh_muc_list=danh_muc_list
            )

        danh_muc = db.session.get(DanhMuc, danh_muc_id)

        if danh_muc is None:
            flash("Danh mục không hợp lệ!", "danger")
            return render_template(
                "sach_form.html",
                action="Sửa",
                sach=sach,
                danh_muc_list=danh_muc_list
            )

        sach.ten_sach = ten_sach
        sach.tac_gia = tac_gia
        sach.gia = gia
        sach.so_luong = so_luong
        sach.danh_muc_id = danh_muc_id

        db.session.commit()

        flash("Cập nhật sách thành công!", "success")
        return redirect(url_for("sach_list"))

    return render_template(
        "sach_form.html",
        action="Sửa",
        sach=sach,
        danh_muc_list=danh_muc_list
    )


# -------------------------
# 7.4. DELETE: XÓA SÁCH
# -------------------------

@app.route("/sach/xoa/<int:id>", methods=["POST"])
def sach_delete(id):

    sach = db.get_or_404(Sach, id)

    db.session.delete(sach)
    db.session.commit()

    flash("Xóa sách thành công!", "success")
    return redirect(url_for("sach_list"))


# =====================================================
# PHẦN 8: TRANG LỖI 404
# =====================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# =====================================================
# PHẦN 9: TẠO DATABASE VÀ CHẠY ỨNG DỤNG
# =====================================================

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

        print("Da tao database va cac bang thanh cong!")

    app.run(debug=True)
