from flask_frozen import Freezer
from . import app
from .database import Student

app.config["FREEZER_DESTINATION"] = "./../build"
app.config["FREEZER_BASE_URL"] = "https://alipatti.github.io/oleorcarl/"
freezer = Freezer(app)


@freezer.register_generator
def student_page():
    # pylint: disable=not-an-iterable
    for student in Student.select().where(Student.face != None):
        username, school = student.email.replace(".edu", "").split("@")
        yield {"username": username, "school": school}


def freeze():
    freezer.freeze()


def test():
    freezer.serve(debug=True)
