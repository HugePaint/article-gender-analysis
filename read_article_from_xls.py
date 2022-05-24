import pandas as pd
import tagging_demo as analyzer
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


df = pd.read_excel(r"data\First 100 Articles scored ZY.xlsx", header=0)
article_list = list()
expect_result = dict()
# for i in range(0, len(df.index)):
for i in range(0, 3):
    serie = df.loc[i]
    article = analyzer.Article(list(), list(), dict())
    article.id = serie["#"]
    article.country = serie["Country"]
    article.year = serie["Year"]
    article.category = serie["News Category"]
    article.title = serie["Title"]
    article.text = serie["Content "]
    article_list.append(article)

    expect_result[str(serie["#"])] = list([serie["Female Central (out of 5) - ZY"], serie["Male Central (out of 5) - ZY"]])

for a in article_list:
    analyzer.analyze(a)
    # clean up
    a.text = ""
    a.text_tagged = list()

# Serializing json 
json_articles = json.dumps(article_list, indent = 4, cls=EnhancedJSONEncoder)
json_expect_results = json.dumps(expect_result, indent = 4, cls=EnhancedJSONEncoder)
  
# Writing to sample.json
with open("article_list.json", "w") as outfile:
    outfile.write(json_articles)
with open("expect_results.json", "w") as outfile:
    outfile.write(json_expect_results)


print(article_list)


