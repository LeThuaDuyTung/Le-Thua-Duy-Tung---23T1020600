
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, func


# ==========================================
# BUOC 1: TAO LOP BASE
# ==========================================

class Base(DeclarativeBase):
    pass


# ==========================================
# BUOC 2: KHOI TAO DATABASE
# ==========================================

db = SQLAlchemy(model_class=Base)


# ==========================================
# BUOC 3: KHOI TAO UNG DUNG FLASK
# ==========================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///qlsv.db"

db.init_app(app)


# ==========================================
# BUOC 4: KHAI BAO MODEL STUDENT
# ==========================================

class Student(db.Model):

    id: Mapped[int] = mapped_column(primary_key=True)

    mssv: Mapped[str] = mapped_column(
        String(20),
        unique=True
    )

    name: Mapped[str] = mapped_column(String(100))

    gpa: Mapped[float | None] = mapped_column(nullable=True)

    score: Mapped[float | None] = mapped_column(nullable=True)

    age: Mapped[int] = mapped_column(default=0)

    def __repr__(self):
        return f"<Student {self.mssv} {self.name}>"


# ==========================================
# BUOC 5: TAO DATABASE VA BANG
# ==========================================

with app.app_context():
    db.create_all()
    print("Da tao database va bang Student thanh cong!")


# ==========================================
# BUOC 6: TRANG CHU
# ==========================================

@app.get("/")
def index():

    students = db.session.execute(
        db.select(Student).order_by(Student.id)
    ).scalars().all()

    total = len(students)

    avg = db.session.scalar(
        db.select(func.avg(Student.gpa))
    )

    return render_template(
        "index.html",
        students=students,
        total=total,
        avg=avg
    )


# ==========================================
# BUOC 7: THEM DU LIEU MAU
# ==========================================

@app.get("/them-mau")
def add_sample():

    total = db.session.scalar(
        db.select(func.count(Student.id))
    )

    if total >= 5:
        return redirect(url_for("index"))

    samples = [
        Student(
            mssv="23T1020001",
            name="Nguyễn Văn An",
            gpa=8.5,
            score=8.5,
            age=22
        ),
        Student(
            mssv="23T1020002",
            name="Trần Thị Bình",
            gpa=6.8,
            score=6.8,
            age=21
        ),
        Student(
            mssv="23T1020003",
            name="Lê Hoàng Cường",
            gpa=9.1,
            score=9.1,
            age=22
        ),
        Student(
            mssv="23T1020004",
            name="Phạm Minh Dũng",
            gpa=4.5,
            score=4.5,
            age=23
        ),
        Student(
            mssv="23T1020005",
            name="Hoàng Thu Hà",
            gpa=7.4,
            score=7.4,
            age=21
        )
    ]

    # Chi them MSSV chua ton tai
    for student in samples:
        exists = db.session.scalar(
            db.select(Student).filter_by(mssv=student.mssv)
        )

        if exists is None:
            db.session.add(student)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return redirect(url_for("index"))


# ==========================================
# BUOC 8: THU TRUY VAN
# ==========================================

@app.get("/thu-truy-van")
def try_queries():

    students = db.session.execute(
        db.select(Student).order_by(Student.id)
    ).scalars().all()

    good = db.session.execute(
        db.select(Student)
        .where(Student.gpa >= 8)
        .order_by(Student.gpa.desc())
    ).scalars().all()

    count = db.session.scalar(
        db.select(func.count(Student.id))
    )

    avg = db.session.scalar(
        db.select(func.avg(Student.gpa))
    )

    student_3 = db.session.get(Student, 3)
    student_99 = db.session.get(Student, 99)

    binh = db.session.scalar(
        db.select(Student).filter_by(
            mssv="23T1020002"
        )
    )

    return render_template(
        "students.html",
        students=students,
        good=good,
        count=count,
        avg=avg,
        student_3=student_3,
        student_99=student_99,
        binh=binh
    )


# ==========================================
# BUOC 9: CHAY UNG DUNG
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
