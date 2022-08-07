import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
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

# flip male/female and append them to X_train
# TODO: try use counts instead of frequency
# additional feature: word count, highest fequency of a full name
# TODO: try regression 

article_list = json.load(open('article_list.json',))
expect_results = json.load(open('expect_results.json',))

feature_list = list()
# get feature from extracted list
for a in article_list:
    # segment_words = a["word_count"] // a["segments"]
    # # features = [a["male_person"] - a["female_person"]]
    # features = [a["female_person"]]
    # features.append(a["word_count"])
    # for segment in a["segmented_gender_word_count"]:
    #     for x in segment:
    #         features.append(x / segment_words)
    # feature_list.append(features)

    # # flip
    # segment_words = a["word_count"] // a["segments"]
    # # features = [a["female_person"] - a["male_person"]]
    # features = [a["male_person"]]
    # features.append(a["word_count"])
    # for segment in a["segmented_gender_word_count"]:
    #     features.append(segment[1] / segment_words)
    #     features.append(segment[0] / segment_words)
    # feature_list.append(features)

    # features = [a["male_person"] - a["female_person"]]
    features = [a["female_person"]]
    features.append(a["word_count"])
    for segment in a["segmented_gender_word_count"]:
        for x in segment:
            features.append(x)
    feature_list.append(features)

    # flip
    # features = [a["female_person"] - a["male_person"]]
    features = [a["male_person"]]
    features.append(a["word_count"])
    for segment in a["segmented_gender_word_count"]:
        features.append(segment[1])
        features.append(segment[0])
    feature_list.append(features)


expect_results_with_flipped_data = list()
for e in expect_results.values():
    # for each e:
    # ["Female Central (out of 5) - ZY", "Male Central (out of 5) - ZY"]
    expect_results_with_flipped_data.append(e[0])

    # add flipped male score to the y set
    expect_results_with_flipped_data.append(e[1])



# cross validation
# Ref: https://scikit-learn.org/stable/modules/cross_validation.html#cross-validation

X = np.array(feature_list)
y = np.array(expect_results_with_flipped_data)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=0
)

x_min, x_max = min([i[0] for i in X]) - 0.5, max([i[0] for i in X]) + 0.5
y_min, y_max = min([i[1] for i in X]) - 0.5, max([i[1] for i in X]) + 0.5

# just plot the dataset first
cm = plt.cm.RdBu
cm_bright = ListedColormap(["#FF0000", "#0000FF"])
ax = plt.subplot(1, len(classifiers) + 1, 1)
ax.set_title("Input data")
# Plot the training points
# ax.scatter([i[0] for i in X_train], [i[1] for i in X_train], c=y_train, cmap=cm_bright, edgecolors="k")
ax.scatter(X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright, edgecolors="k")
# Plot the testing points
# ax.scatter(
#     [i[0] for i in X_test], [i[1] for i in X_test], c=y_test, cmap=cm_bright, alpha=0.6, edgecolors="k"
# )
ax.scatter(
        X_test[:, 0], X_test[:, 1], c=y_test, cmap=cm_bright, alpha=0.6, edgecolors="k"
)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_xticks(())
ax.set_yticks(())

i = 1
print("--------Testing male set")
for name, clf in zip(names, classifiers):
    # clf.fit(X_train, y_train)
    # score = clf.score(X_test, y_test)
    # print(name + ": " + str(score))

    
    ax = plt.subplot(1, len(classifiers) + 1, i)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    # DecisionBoundaryDisplay.from_estimator(
    #     clf, X, cmap=cm, alpha=0.8, ax=ax, eps=0.5
    # )

    # Plot the training points
    ax.scatter(
            X_train[:, 0], X_train[:, 1], c=y_train, cmap=cm_bright, edgecolors="k"
    )
    # Plot the testing points
    ax.scatter(
            X_test[:, 0],
            X_test[:, 1],
            c=y_test,
            cmap=cm_bright,
            edgecolors="k",
            alpha=0.6,
    )

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_xticks(())
    ax.set_yticks(())
    ax.set_title(name)
    ax.text(
        x_max - 0.3,
        y_min + 0.3,
        ("%.2f" % score).lstrip("0"),
        size=15,
        horizontalalignment="right",
    )
    i += 1

plt.tight_layout()
plt.show()
