# Ole or Carl

Click [here](http://alipatti.github.io/oleorcarl/) to have some fun.

This project was originally built as a joke to refute claims that I look like an Ole and test the validity of a long-standing stereotype that students from Northfield's two colleges look meaningfully different. If they are, then a machine learning model should be able to tell them apart? Right?

## The nitty gritty

Under the hood, the model first creates a vector embedding of every student's face with an off-the-shelf neural net from [`dlib`](http://dlib.net/python/index.html#dlib_pybind11.face_recognition_model_v1) (see `oleorcarl.scraper.pipelines.FaceEmbedder`). These are then used to train a vector classifier (`oleorcarl.model`).
I tested a handful of different types and found that a support-vector classifier with the radial basis kernel has the highest cross-validated classification accuracy (around 67%), although the final site uses a linear SVC for the best mix of accuracy, transparency, speed, and resistance to overfitting. Check out the `model_selection` folder for more details.

## Website

Built with `Flask`, then pre-rendered into a static site so I can put it on github pages and make Bill Gates pay my server costs.
A students' "ole-score" is just the sigmoid of 1.5 times the model's decision function.
One should not take it seriously (although if it says you look like an Ole, I can't help but think less of you).

## TODO

- [x] Scrape directories
- [x] Choose ML model
- [x] Build a goofy-ass website
- [ ] Get more training data from alumni LinkedIn profiles and the alumni directory
- [ ] Experiment with training a from-scratch neural net (this runs the risk of the model just learning the OneCard photo background—can we remove the background before processing?)
- [ ] Experiment with fine tuning/transfer learning from the dlib model (probably needs more training data)
