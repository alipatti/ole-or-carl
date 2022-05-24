from scraper import get_directory, IMG_FOLDER

import os
import pickle
import numpy as np
from tqdm import tqdm

from face_recognition.api import face_encodings, load_image_file
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from IPython.display import Image, display

DIRECTORY = get_directory()
VECTOR_FILE = "data/face_vectors.pkl"
MODEL_FILE = "data/model.pkl"


##################
# MODEL BUILDING #
##################


def _vectorize_faces():
    vectors = {}

    emails = list(DIRECTORY.keys())
    for email in tqdm(emails, desc="Vectorizing faces"):

        img = load_image_file(IMG_FOLDER + email + ".jpg")

        vecs = face_encodings(img)
        vectors[email] = vecs[0] if vecs else None

    with open(VECTOR_FILE, "wb") as f:
        pickle.dump(vectors, f)


def _build_and_train_model(test_size=0.15):
    with open("face_vectors.pkl", "rb") as f:
        vectors = pickle.load(f)

    labeled_vectors = [
        (vector, int(email.endswith("carleton.edu")))
        for email, vector in vectors.items()
        if vector is not None
    ]

    X, Y = map(np.array, zip(*labeled_vectors))

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_size)

    pipe = make_pipeline(StandardScaler(), SVC())
    pipe.fit(X_train, Y_train)

    print(f"Test cases correct: {pipe.score(X_test, Y_test):.1%}")

    with open(MODEL_FILE, "wb") as f:
        pickle.dump(pipe, f)

    # done


#########################
# CONVENIENCE FUNCTIONS #
#########################


def load_vectors():
    with open(VECTOR_FILE, "rb") as f:
        return pickle.load(f)


def load_model():
    with open(MODEL_FILE, "rb") as f:
        return pickle.load(f)


def show_image(email):
    return display(Image(open(IMG_FOLDER + email + ".jpg", "rb").read()))


def predict(email, vectors=None, model=None):

    if not vectors:
        load_vectors()

    if not model:
        load_model()

    show_image(email)

    vec = vectors[email]
    prediction = model.decision_function(vec.reshape(1, -1))
    print(f"{'Carl' if prediction > 0 else 'Ole'} ({prediction[0]:.3f})")


########
# MAIN #
########


def create_model():
    if not os.path.exists(VECTOR_FILE):
        print("Vectorizing faces...")
        _vectorize_faces()

    if not os.path.exists(MODEL_FILE):
        print("Building model...")
        _build_and_train_model()


if __name__ == "__main__":
    create_model()
