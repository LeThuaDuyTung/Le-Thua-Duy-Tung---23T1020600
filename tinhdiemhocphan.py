
import math
from flask import Flask, request, render_template

app = Flask(
    __name__,
    template_folder="templates_tinhdiemhocphan"
)


# Ham kiem tra diem dung chung cho ca 3 o
def validate_score(value):
    value = value.strip()

    if value == "":
        return None, "Vui long nhap mot so"

    # Chap nhan dau phay thap phan
    value = value.replace(",", ".")

    try:
        score = float(value)
    except ValueError:
        return None, "Vui long nhap mot so hop le"

    # Tu choi NaN va vo cuc
    if not math.isfinite(score):
        return None, "Vui long nhap mot so hop le"

    # Diem phai nam trong khoang 0 den 10
    if score < 0 or score > 10:
        return None, "Diem phai tu 0 den 10"

    return score, None


# Ham tinh diem hoc phan
def calculate_average(cc, gk, ck):
    average = cc * 0.1 + gk * 0.3 + ck * 0.6
    return round(average + 1e-9, 1)


# Ham xep loai diem chu
def calculate_letter(score, final_score):
    # Diem cuoi ky duoi 1 la diem liet
    if final_score < 1:
        return "F"

    if score >= 8.5:
        return "A"
    elif score >= 7.0:
        return "B"
    elif score >= 5.5:
        return "C"
    elif score >= 4.0:
        return "D"
    else:
        return "F"


@app.route("/", methods=["GET", "POST"])
def index():
    # Gia tri mac dinh cua cac o nhap
    values = {
        "cc": "",
        "gk": "",
        "ck": ""
    }

    # Thong bao loi cho tung o
    errors = {
        "cc": "",
        "gk": "",
        "ck": ""
    }

    result = None
    letter = ""
    warning = ""

    if request.method == "POST":
        # Lay du lieu nguoi dung nhap
        values["cc"] = request.form.get("cc", "")
        values["gk"] = request.form.get("gk", "")
        values["ck"] = request.form.get("ck", "")

        scores = {}

        # Ten cac truong de hien thi loi
        fields = {
            "cc": "CC",
            "gk": "GK",
            "ck": "CK"
        }

        # Kiem tra ca 3 o bang cung mot ham
        for field, field_name in fields.items():
            score, error = validate_score(values[field])

            if error:
                errors[field] = (
                    f"Loi o {field_name}: {error}"
                )
            else:
                scores[field] = score

        # Chi tinh diem khi ca 3 o deu hop le
        if not any(errors.values()):
            cc = scores["cc"]
            gk = scores["gk"]
            ck = scores["ck"]

            # Tinh diem hoc phan va lam tron 1 chu so thap phan
            result = calculate_average(cc, gk, ck)

            # Xep loai diem chu
            letter = calculate_letter(result, ck)

            # Canh bao neu diem cuoi ky bi diem liet
            if ck < 1:
                warning = "Diem thi cuoi ky duoi 1: Diem liet."

    return render_template(
        "index.html",
        values=values,
        errors=errors,
        result=result,
        letter=letter,
        warning=warning
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
