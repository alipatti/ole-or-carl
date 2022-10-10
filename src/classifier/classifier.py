from pprint import pprint
import numpy as np
import yaml

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

from ..settings import CLASSIFIER_PARAMS_PATH, GRID_SEARCH_RESULTS_PATH
from ..database import Student


def get_best_params() -> dict:

    X, y = _get_vectors_and_labels()

    # ranges loosely taken from page 6 of
    # https://www.csie.ntu.edu.tw/~cjlin/papers/guide/guide.pdf
    param_grid = [
        {
            "svc__kernel": ["linear"],
            "svc__C": np.logspace(-3, 6, 10, base=2),
        },
        {
            "svc__kernel": ["rbf"],
            "svc__C": np.logspace(-5, 15, 5, base=2),
            "svc__gamma": np.logspace(-15, 3, 5, base=2),
        },
        {
            "svc__kernel": ["poly"],
            "svc__C": np.logspace(-5, 15, 5, base=2),
            "svc__degree": [2, 3, 4],
            "svc__gamma": np.logspace(-15, 3, 5, base=2),
        },
    ]

    model = GridSearchCV(
        estimator=make_pipeline(StandardScaler(), SVC()),
        param_grid=param_grid,
        scoring="accuracy",
        n_jobs=12,  # use all available threads
        refit=True,  # so we get the refit time
        cv=5,  # 5-fold CV
    )

    print("Finding best hyper-parameters by exhaustive grid search...")
    model.fit(X, y)

    print(" --- Done! --- ")

    best_params = {
        "params": model.best_params_,
        "info": {
            "score": model.best_score_,
            "fit_time": model.refit_time_,
        },
    }
    pprint(best_params)

    print(" --- Saving... ---")

    print(f"...the best hyper-parameters to {CLASSIFIER_PARAMS_PATH}")
    with open(CLASSIFIER_PARAMS_PATH, "wt", encoding="utf-8") as f:
        yaml.safe_dump(best_params, f)

    print(f"...the complete results to {GRID_SEARCH_RESULTS_PATH}")
    with open(GRID_SEARCH_RESULTS_PATH, "wt", encoding="utf-8") as f:
        yaml.safe_dump(model.cv_results_, f)


def score_all_students():
    # load students from database

    # store the results back in the database
    pass


def _get_vectors_and_labels() -> tuple[np.ndarray, np.ndarray]:
    """Returns numpy arrays `X` and `y` where `X` is the stack of all
    face-embeddings and `y` is the corresponding labels."""

    students = list(Student.select())

    X = np.stack([s.face for s in students if s.face is not None])

    y = np.array([
        bool(s.school == "stolaf")
        for s in students
        if s.face is not None
    ])  # fmt: skip

    return X, y
