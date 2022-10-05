Ole or Carl?
============

At Carleton, there's a stereotype that all St. Olaf students look the same. If true, then a machine learning model should be able to distinguish between Carleton and St. Olaf students with some accuracy. So can it?

Sort of. An SVM classifier trained on current students is able to correctly predict the college of test students with 67 percent accuracy. Not too shabby.

Profile photos were scraped from each college's respective directory using [`selenium`](https://selenium-python.readthedocs.io/) and [`BeautifulSoup`](https://www.crummy.com/software/BeautifulSoup/bs4/doc/), faces were vectorized using a Python api for [`dlib`](http://dlib.net/), and classification was done using an SVC pipeline from [`scikit-learn`](http://scikit-learn.org).

TODO
----

- [ ] Add more training data by scraping photos from alumni directories or LinkedIn
- [ ] Test the model on each schools incoming class
- [ ] Test the model on photos not taken in the school ID office
- [ ] Write whitepaper