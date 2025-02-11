import statistics
import pandas as pd
import tagging_core as analyzer
import json
import dataclasses
import numpy as np

# Ref1: https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
# Ref2: https://stackoverflow.com/questions/51286748/make-the-python-json-encoder-support-pythons-new-dataclasses
class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            if isinstance(o, np.integer):
                return int(o)
            if isinstance(o, np.floating):
                return float(o)
            if isinstance(o, np.ndarray):
                return o.tolist()
            return super().default(o)


df = pd.read_excel(r"data\score corrected.xlsx", header=0)
article_list = list()
expect_result = dict()
for i in range(0, len(df.index)):
# for i in range(0, 3):
    serie = df.loc[i]
    article = analyzer.Article(list(), list(), dict())
    # article.id = serie["#"]
    # article.id = i
    article.id = serie["sample_article"]
    article.country = serie["Country"]
    article.year = serie["year"]
    article.category = serie["New Type"]
    # article.title = serie["Title"]
    article.text = serie["Content"]
    article_list.append(article)

    # female_score = np.mean([serie["Female Central (out of 5) - ZY"], serie["Female Central (out of 5) - Rafael"]])
    # male_score = np.mean([serie["Male Central (out of 5) - ZY"], serie["Male Central (out of 5) - Rafael"]])
    female_score = serie["female_score"]
    male_score = serie["Male_score"]
    print(female_score, " ", male_score)
    # expect_result[str(serie["#"])] = list([female_score, male_score])
    expect_result[i] = list([female_score, male_score])

index = 0
total = len(article_list)
for a in article_list:
    index += 1
    analyzer.analyze(a)
    print(f'({index}/{total}) - ID: {a.id}')
    # clean up
    a.text = ""
    a.text_tagged = list()

# Serializing json 
json_articles = json.dumps(article_list, indent = 4, cls=EnhancedJSONEncoder)
json_expect_results = json.dumps(expect_result, indent = 4, cls=EnhancedJSONEncoder)
  
# Writing to sample.json
with open("training_article_list.json", "w") as outfile:
    outfile.write(json_articles)
with open("training_results.json", "w") as outfile:
    outfile.write(json_expect_results)


print(article_list)


