import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline

from ..database import Student


def get_vectors_and_labels() -> tuple[np.ndarray, np.ndarray]:
    """Returns numpy arrays `X` and `y` where `X` is the stack of all
    face-embeddings and `y` is the corresponding labels."""

    students = list(Student.select().where(Student.face != None))

    X = np.stack([s.face for s in students])

    y = np.array([
        1 if s.school == "stolaf" else -1
        for s in students
    ])  # fmt: skip

    return X, y


model = make_pipeline(StandardScaler(), LinearSVC(dual=False))

X, y = get_vectors_and_labels()
model.fit(X, y)
