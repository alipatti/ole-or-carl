# Ole or Carl?

🚨 **FALL 2023 UPDATE**: I've been asked to take down the public site due to
privacy concerns.

This project was built as a joke to refute claims that I look like a St. Olaf
student and test the validity of a long-standing stereotype that students from
Northfield's two colleges look meaningfully different. If they are, then a
machine learning model should be able to tell them apart? Right?

## The Nitty-Gritty

Under the hood, the model first creates a vector embedding of every student's
face with an off-the-shelf neural net from
[`dlib`](http://dlib.net/python/index.html#dlib_pybind11.face_recognition_model_v1)
(see `oleorcarl.scraper.pipelines.FaceEmbedder`). These are then used to train a
vector classifier (`oleorcarl.model`). An SVC with a nonlinear kernel has the
highest cross-validated accuracy (around 67%), but the final site uses a linear
SVC for the best mix of accuracy, speed, and resistance to overfitting. Check
out the `model_selection` folder for more details.

Every student is then assigned an "ole-score" that captures whether they look
more like Carleton or St. Olaf students. Internally, this is just the sigmoid of
the model's decision function.

One should not take their score seriously (although if it says you look like an
Ole, I can't help but think less of you).

## TODO

- [x] Scrape directories
- [x] Choose ML model
- [x] Build a goofy-ass website
- [ ] Get more training data from alumni LinkedIn profiles and the alumni
      directory
- [ ] Experiment with training a from-scratch neural net (this runs the risk of
      the model just learning the OneCard photo background—can we remove the
      background before processing?)
- [ ] Experiment with transfer learning from the dlib model (probably needs more
      training data)
