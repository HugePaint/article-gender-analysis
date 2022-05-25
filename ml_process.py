import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.inspection import DecisionBoundaryDisplay

# Ref: https://scikit-learn.org/stable/auto_examples/classification/plot_classifier_comparison.html
names = [
    "Nearest Neighbors",
    "Linear SVM",
    "RBF SVM",
    "Gaussian Process",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes",
    "QDA",
]
classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    GaussianProcessClassifier(1.0 * RBF(1.0)),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    MLPClassifier(alpha=1, max_iter=1000),
    AdaBoostClassifier(),
    GaussianNB(),
    QuadraticDiscriminantAnalysis(),
]

# TODO: flip male/female and append them to X_train
# TODO: try use counts instead of frequency
# additional feature: word count, highest fequency of a full name
# TODO: try regression 

article_list = json.load(open('article_list.json',))
expect_results = json.load(open('expect_results.json',))

feature_list = list()
# get feature from extracted list
for a in article_list:
    segment_words = a["word_count"] // a["segments"]
    features = [a["male_person"] - a["female_person"]]
    for segment in a["segmented_gender_word_count"]:
        for x in segment:
            features.append(x / segment_words)
    feature_list.append(features)

    # flip
    segment_words = a["word_count"] // a["segments"]
    features = [a["female_person"] - a["male_person"]]
    for segment in a["segmented_gender_word_count"]:
        features.append(segment[1] / segment_words)
        features.append(segment[0] / segment_words)
    feature_list.append(features)
# print(feature_list)

female_results = list()
male_results = list()
for e in expect_results.values():
    # for each e:
    # ["Female Central (out of 5) - ZY", "Male Central (out of 5) - ZY"]
    female_results.append(e[0])
    male_results.append(e[1])

    # flip
    female_results.append(e[1])
    male_results.append(e[0])


X = feature_list
y = male_results

# cross validation
# Ref: https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
# clf = RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1).fit(X_train, y_train)
# print(clf.score(X_test, y_test))

y = male_results
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
print("--------Testing male set")
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(name + ": " + str(score))

print("\n")
y = female_results
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=0)
print("---------Testing female set")
for name, clf in zip(names, classifiers):
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(name + ": " + str(score))