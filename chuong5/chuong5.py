from flask import Flask, render_template, request

app = Flask(__name__, template_folder="templates_chuong5")


@app.route("/", methods=["GET", "POST"])
def index():
    ket_qua = None
    chuc_nang = "tongquan"
    loi = None

    if request.method == "POST":
        chuc_nang = request.form.get("chuc_nang", "tongquan")

        try:
            # Chức năng 1: Tính điểm học phần
            if chuc_nang == "tinhdiem":
                chuyen_can = float(request.form["chuyen_can"])
                giua_ky = float(request.form["giua_ky"])
                cuoi_ky = float(request.form["cuoi_ky"])

                if not all(0 <= diem <= 10 for diem in
                           [chuyen_can, giua_ky, cuoi_ky]):
                    raise ValueError("Điểm phải nằm trong khoảng từ 0 đến 10.")

                diem_tong_ket = (
                    chuyen_can * 0.1
                    + giua_ky * 0.3
                    + cuoi_ky * 0.6
                )

                ket_qua = {
                    "loai": "tinhdiem",
                    "diem_tong_ket": round(diem_tong_ket, 2),
                    "xep_loai": (
                        "Giỏi" if diem_tong_ket >= 8
                        else "Khá" if diem_tong_ket >= 6.5
                        else "Trung bình" if diem_tong_ket >= 5
                        else "Yếu"
                    )
                }

            # Chức năng 2: Tính BMI
            elif chuc_nang == "bmi":
                can_nang = float(request.form["can_nang"])
                chieu_cao = float(request.form["chieu_cao"])

                if can_nang <= 0 or chieu_cao <= 0:
                    raise ValueError(
                        "Cân nặng và chiều cao phải lớn hơn 0."
                    )

                bmi = can_nang / (chieu_cao / 100) ** 2

                if bmi < 18.5:
                    phan_loai = "Thiếu cân"
                elif bmi < 25:
                    phan_loai = "Bình thường"
                elif bmi < 30:
                    phan_loai = "Thừa cân"
                else:
                    phan_loai = "Béo phì"

                ket_qua = {
                    "loai": "bmi",
                    "bmi": round(bmi, 2),
                    "phan_loai": phan_loai
                }

            # Chức năng 3: Máy tính
            elif chuc_nang == "maytinh":
                so_a = float(request.form["so_a"])
                so_b = float(request.form["so_b"])
                phep_tinh = request.form["phep_tinh"]

                if phep_tinh == "cong":
                    ket_qua_tinh = so_a + so_b
                    ky_hieu = "+"
                elif phep_tinh == "tru":
                    ket_qua_tinh = so_a - so_b
                    ky_hieu = "-"
                elif phep_tinh == "nhan":
                    ket_qua_tinh = so_a * so_b
                    ky_hieu = "×"
                elif phep_tinh == "chia":
                    if so_b == 0:
                        raise ValueError("Không thể chia cho 0.")
                    ket_qua_tinh = so_a / so_b
                    ky_hieu = "÷"
                else:
                    raise ValueError("Phép tính không hợp lệ.")

                ket_qua = {
                    "loai": "maytinh",
                    "so_a": so_a,
                    "so_b": so_b,
                    "ky_hieu": ky_hieu,
                    "ket_qua_tinh": round(ket_qua_tinh, 6)
                }

        except ValueError as e:
            loi = str(e) or "Vui lòng nhập dữ liệu hợp lệ."
        except (KeyError, TypeError):
            loi = "Vui lòng nhập đầy đủ thông tin."

    return render_template(
        "index.html",
        ket_qua=ket_qua,
        chuc_nang=chuc_nang,
        loi=loi
    )


if __name__ == "__main__":
    app.run(debug=True)