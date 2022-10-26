from math import exp

from flask import Flask, render_template, abort

from .database import Student
from . import classifier


app = Flask(__name__)

students = [
    dict(
        name=student.name,
        email=student.email,
        # TODO change to use `url_for`
        url=f"{student.school}/{student.username}.html"
    )
    for student in Student.select()
    if student.face is not None
]


@app.route("/")
def home_page():
    return render_template("home.html", students=students)


@app.route("/<string:school>/<string:username>.html")
def student_page(school: str, username: str):

    email = f"{username}@{school}.edu"
    student: Student = Student.get_or_none(Student.email == email)

    if not student:
        abort(404)

    student.score = classifier.score(student)

    # scale by 1.5 to use more of the range (value chosen arbitrarily)
    student.translate_percent = sigmoid(student.score * 1.5) * 100

    return render_template("student.html", student=student, abs=abs)


def sigmoid(x):
    return 1 / (1 + exp(-x))
