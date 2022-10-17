import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.pipeline import make_pipeline

from ..database import Student


def get_vectors_and_labels() -> tuple[np.ndarray, np.ndarray]:
    """Returns numpy arrays `X` and `y` where `X` is the stack of all
    face-embeddings and `y` is their corresponding labels."""

    students = list(Student.select())

    X = np.stack([s.face for s in students if s.face is not None])

    y = np.array([
        bool(s.school == "stolaf")
        for s in students
        if s.face is not None
    ])  # fmt: skip

    return X, y


model = make_pipeline(StandardScaler(), LinearSVC(dual=False))

X, y = get_vectors_and_labels()
model.fit(X, y)
