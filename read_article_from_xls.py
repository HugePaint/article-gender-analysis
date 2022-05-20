import pandas as pd
import tagging_demo as analyzer

df = pd.read_excel (r"data\First 100 Articles scored ZY.xlsx", header=0)
print(df.loc[3])

article_list = list()
result_list = dict()
for i in range(0, len(df.index)):
    serie = df.loc[i]
    article = analyzer.Article(list(), list(), dict())
    article.id = serie["#"]
    article.country = serie["Country"]
    article.year = serie["Year"]
    article.category = serie["News Category"]
    article.title = serie["Title"]
    article.text = serie["Content "]
    article_list.append(article)

    expect_result = list([serie["Female Central (out of 5) - ZY"], serie["Male Central (out of 5) - ZY"]])
    result_list[str(serie["#"])] = expect_result

print(article_list)


