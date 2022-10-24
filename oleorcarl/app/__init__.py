# TODO move app logic to separate file?

from flask import Flask, render_template, request
from scipy.special import expit as sigmoid  # pylint: disable=no-name-in-module
from matplotlib.colors import LinearSegmentedColormap

from ..database import Student
from ..settings import OLAF_IMG_URL, CARLETON_IMG_URL
from ..classifier import model


img_urls = {
    "stolaf": OLAF_IMG_URL,
    "carleton": CARLETON_IMG_URL,
}

app = Flask(__name__)

students = [
    dict(name=student.name, email=student.email)
    for student in Student.select()
    if student.face is not None
]


@app.route("/", methods=["GET", "POST"])
def home_page():

    # TODO implement search autocomplete
    if request.method == "GET":
        return render_template("home.html", students=students)

    student: Student = Student.get_or_none(Student.name == request.form["name"])

    if not student:
        return render_template(
            "home.html",
            students=students,
            failed_name=request.form["name"],
        )

    student.img_url = img_urls[student.school].format(student.email.split("@")[0])

    # TODO move scoring logic to `model` sub-package
    student.score = round(model.decision_function(student.face.reshape(1, -1))[0], 3)

    # scale by 1.5 to use more of the range (value chosen arbitrarily)
    student.translate_percent = sigmoid(student.score * 1.5) * 100

    return render_template("student.html", student=student, abs=abs)


if __name__ == "__main__":
    app.run(debug=True, port=3000, host="localhost")
