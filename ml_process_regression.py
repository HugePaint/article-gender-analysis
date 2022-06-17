import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn.model_selection import train_test_split
from sklearn.ensemble import AdaBoostRegressor
from sklearn.tree import DecisionTreeRegressor
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score

# flip male/female and append them to X_train
# TODO: try use counts instead of frequency
# additional feature: word count, highest fequency of a full name
# TODO: try regression 

article_list = json.load(open('article_list.json',))
expect_results = json.load(open('expect_results.json',))

feature_list = list()
# get feature from extracted list
for a in article_list: 
    segment_words = a["word_count"] // a["segments"]
    # features = [a["male_person"] - a["female_person"]]
    features = [a["female_person"]]
    features.append(a["word_count"])
    for segment in a["segmented_gender_word_count"]:
        for x in segment:
            features.append(x / segment_words)
    feature_list.append(features)

    # flip
    segment_words = a["word_count"] // a["segments"]
    # features = [a["female_person"] - a["male_person"]]
    features = [a["male_person"]]
    features.append(a["word_count"])
    for segment in a["segmented_gender_word_count"]:
        features.append(segment[1] / segment_words)
        features.append(segment[0] / segment_words)
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
    X, y, test_size=0.3, random_state=0
)

# Decision Tree Regression with AdaBoost
# Ref: https://scikit-learn.org/stable/auto_examples/ensemble/plot_adaboost_regression.html

regr_1 = DecisionTreeRegressor(max_depth=6)

regr_2 = AdaBoostRegressor(
    DecisionTreeRegressor(max_depth=6), n_estimators=300, random_state=None
)

regr_1.fit(X_train, y_train)
regr_2.fit(X_train, y_train)

y_1 = regr_1.predict(X_test)
y_2 = regr_2.predict(X_test)

print(r2_score(y_test, y_1))
print(r2_score(y_test, y_2))


colors = sns.color_palette("colorblind")

# Model persistence
# Ref: https://scikit-learn.org/stable/model_persistence.html

from joblib import dump, load
dump(regr_1, 'DecisionTreeRegressor.joblib') 
dump(regr_2, 'AdaBoostRegressor.joblib') 