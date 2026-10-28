
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Máy tính cơ bản</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 500px;
            margin: 40px auto;
            padding: 20px;
        }

        input, select, button {
            padding: 8px;
            margin: 5px 0;
        }

        .loi {
            color: red;
            font-size: 14px;
        }

        .ketqua {
            margin-top: 15px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h2>Máy tính cơ bản</h2>

    <form method="POST">
        <label>Số thứ nhất (a):</label><br>
        <input type="text" name="a" value="{{ a }}">
        <div class="loi">{{ loi_a }}</div>

        <label>Phép toán:</label><br>
        <select name="op">
            <option value="+" {% if op == '+' %}selected{% endif %}>+</option>
            <option value="-" {% if op == '-' %}selected{% endif %}>-</option>
            <option value="*" {% if op == '*' %}selected{% endif %}>*</option>
            <option value="/" {% if op == '/' %}selected{% endif %}>/</option>
        </select>
        <br>

        <label>Số thứ hai (b):</label><br>
        <input type="text" name="b" value="{{ b }}">
        <div class="loi">{{ loi_b }}</div>

        <br>
        <button type="submit">Tính kết quả</button>
    </form>

    {% if ketqua != '' %}
        <div class="ketqua">{{ ketqua }}</div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def may_tinh():
    a = ""
    b = ""
    op = "+"
    loi_a = ""
    loi_b = ""
    ketqua = ""

    if request.method == "POST":
        a = request.form.get("a", "").strip()
        b = request.form.get("b", "").strip()
        op = request.form.get("op", "+")

        so_a = None
        so_b = None

        # Kiểm tra số thứ nhất
        try:
            so_a = float(a.replace(",", "."))
        except ValueError:
            loi_a = "Vui lòng nhập một số."

        # Kiểm tra số thứ hai
        try:
            so_b = float(b.replace(",", "."))
        except ValueError:
            loi_b = "Vui lòng nhập một số."

        if op not in ["+", "-", "*", "/"]:
            ketqua = "Phép toán không hợp lệ."

        elif loi_a or loi_b:
            if loi_a and loi_b:
                ketqua = "Lỗi cả hai ô."
            elif loi_a:
                ketqua = "Lỗi ô a: Vui lòng nhập một số."
            else:
                ketqua = "Lỗi ô b: Vui lòng nhập một số."

        elif op == "/" and so_b == 0:
            loi_b = "Không thể chia cho 0."
            ketqua = "Lỗi ô b: Không thể chia cho 0."

        else:
            if op == "+":
                kq = so_a + so_b
            elif op == "-":
                kq = so_a - so_b
            elif op == "*":
                kq = so_a * so_b
            else:
                kq = so_a / so_b

            ketqua = f"Kết quả: {a} {op} {b} = {kq:g}"

    return render_template_string(
        HTML,
        a=a,
        b=b,
        op=op,
        loi_a=loi_a,
        loi_b=loi_b,
        ketqua=ketqua
    )


if __name__ == "__main__":
    app.run(debug=True, port=8000)
