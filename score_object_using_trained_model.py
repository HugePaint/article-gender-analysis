import json
import os
import csv
import numpy as np
import tkinter as tk
from tkinter import filedialog


root = tk.Tk()
root.withdraw()
folder_selected = filedialog.askdirectory(title='Select folder that contains json file (article list)')

from joblib import dump, load
loaded_model = load('AdaBoostRegressor.joblib')

file_path_list = list()
for root, dirs, files in os.walk(folder_selected):
    for file in files:
        if file.endswith(".json"):
             file_path_list.append(os.path.join(root, file))

for file_path in file_path_list:
    print("Processing " + file_path)
    csv_out_path = os.path.splitext(file_path)[0]+'.csv'

    if os.path.exists(csv_out_path):
        if os.path.getsize(csv_out_path) > 100:
            print(os.path.basename(csv_out_path) + " is exist. Skipped.")
            continue

    article_list = json.load(open(file_path,))
    result_list = list()

    # get feature from extracted list
    feature_list_for_female_score = list()
    feature_list_for_male_score = list()
    for a in article_list: 
        segment_words = a["word_count"] // a["segments"]
        female_features = [a["female_person"]]
        female_features.append(a["word_count"])
        for segment in a["segmented_gender_word_count"]:
            for x in segment:
                female_features.append(x / segment_words)

        segment_words = a["word_count"] // a["segments"]
        male_features = [a["male_person"]]
        male_features.append(a["word_count"])
        for segment in a["segmented_gender_word_count"]:
            male_features.append(segment[1] / segment_words)
            male_features.append(segment[0] / segment_words)

        female_score = loaded_model.predict(np.array(female_features).reshape(1, -1))
        male_score = loaded_model.predict(np.array(male_features).reshape(1, -1))
        result = [a["id"], a["year"], a["country"], a["category"], a["title"], a["text"], a["word_count"], float(female_score[0]), float(male_score[0])]
        result_list.append(result)

    # Save results to csv
    with open(csv_out_path, 'w') as csvfile:
        writer = csv.writer(csvfile)
        result_header = ['id', 'year', 'country', 'category', 'title', 'text', 'word_count', 'female_score', 'male_score']
        writer.writerow(result_header)
        writer.writerows(result_list)
        print("Saved:  " + csv_out_path)







