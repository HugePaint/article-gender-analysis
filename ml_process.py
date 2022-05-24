import json

article_list = json.load(open('article_list.json',))
expect_results = json.load(open('expect_results.json',))

# get feature from extracted list
for a in article_list:
    segment_words = a["word_count"] // a["segments"]
    features = [a["male_person"], a["female_person"]]
    for segment in a["segmented_gender_word_count"]:
        for x in segment:
            features.append(x / segment_words)
    print(features)
