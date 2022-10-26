from flask import Flask, render_template, url_for, abort
from scipy.special import expit as sigmoid  # pylint: disable=no-name-in-module
from .database import Student
from .settings import OLAF_IMG_URL, CARLETON_IMG_URL
from . import classifier


img_urls = {
    "stolaf": OLAF_IMG_URL,
    "carleton": CARLETON_IMG_URL,
}

app = Flask(__name__)

with app.app_context():  # needed for `url_for`
    students = [
        dict(
            name=student.name,
            email=student.email,
        )
        for student in Student.select()
        if student.face is not None
    ]


@app.route("/")
def home_page():
    return render_template("home.html", students=students)


@app.route("/<string:email>")
def student_page(email: str):

    student: Student = Student.get_or_none(Student.email == email)

    if not student:
        abort(404)

    student.img_url = img_urls[student.school].format(student.email.split("@")[0])

    student.score = classifier.score(student)

    # scale by 1.5 to use more of the range (value chosen arbitrarily)
    student.translate_percent = sigmoid(student.score * 1.5) * 100

    return render_template("student.html", student=student, abs=abs)


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="localhost")
